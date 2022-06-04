# Copyright 2018 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This module is the Flask blueprint for the charge page (/charge).
"""

import os
from middlewares.auth import auth_required

from flask import Blueprint, render_template

from helpers import eventing, orders, product_catalog
from middlewares.form_validation import checkout_form_validation_required

from opentelemetry import trace, baggage
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import Link

PUBSUB_TOPIC_PAYMENT_PROCESS = os.environ.get('PUBSUB_TOPIC_PAYMENT_PROCESS')

tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter(project_id="ubc-serverless-compliance")
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

charge_page = Blueprint('charge_page', __name__)


@charge_page.route('/charge', methods=['POST'])
@auth_required
@checkout_form_validation_required
def process(auth_context, form):
    """
    View function for processing charges.

    Parameters:
       auth_context (dict): The authentication context of request.
                            See middlewares/auth.py for more information.
       form (CheckOutForm): A validated checkout form.
                            See middlewares/form_validation.py for more
                            information.
    Output:
       Rendered HTML page.
    """

    # Prepare the order
    with tracer.start_as_current_span("charge_endpoint", kind=trace.SpanKind.PRODUCER) as root_span:
        product_ids = form.product_ids.data
        stripe_token = form.stripeToken.data
        uid = auth_context.get('uid')
        root_span.set_attribute("userToken", uid)

        # prepare shipping
        shipping = orders.Shipping(address_1=form.address_1.data,
                                   address_2=form.address_2.data,
                                   city=form.city.data,
                                   state=form.state.data,
                                   zip_code=form.zip_code.data,
                                   email=form.email.data,
                                   mobile=form.mobile.data)
        amount = product_catalog.calculate_total_price(product_ids)

        # prepare order
        order = orders.Order(amount=amount,
                             shipping=shipping,
                             status="order_created",
                             items=product_ids,
                             userId=uid)
        order_id = orders.add_order(order)

        # trace event
        root_span.add_event(name="created order")
        context = root_span.get_span_context()
        print("charge endpoint root span context: ", context)
        # parent_ctx = baggage.set_baggage("parentBaggageKey", "parentBaggageValue")

        # Stream a Payment event
        with tracer.start_as_current_span("send_payment_event", kind=trace.SpanKind.PRODUCER) as child_span:
            # child_ctx = baggage.set_baggage("childBaggageKey", "childBaggageValue")
            carrier = dict()
            carrier['uid'] = uid
            TraceContextTextMapPropagator().inject(carrier=carrier)

            context = child_span.get_span_context()
            print("charge endpoint child span context: ", context)

            if stripe_token:
                # Publish an event to the topic for new payments.
                # Cloud Function pay_with_stripe subscribes to the topic and
                # processes the payment using the Stripe API upon arrival of new
                # events.
                # Cloud Function streamEvents (or App Engine service stream-event)
                # subscribes to the topic and saves the event to BigQuery for
                # data analytics upon arrival of new events.
                # print("charge endpoint event context: ", order_id, stripe_token, trace_id)
                eventing.stream_event(
                    topic_name=PUBSUB_TOPIC_PAYMENT_PROCESS,
                    event_type='order_created',
                    event_context={
                        'order_id': order_id,
                        'token': stripe_token,
                    },
                    carrier=carrier
                )
                child_span.add_event(name="published order created event")

    return render_template("charge.html", auth_context=auth_context)
