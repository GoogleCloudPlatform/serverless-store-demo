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
import datetime
from middlewares.auth import auth_required

from flask import Blueprint, render_template
from opencensus.trace.tracer import Tracer
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
# from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace import time_event

from helpers import eventing, orders, product_catalog
from middlewares.form_validation import checkout_form_validation_required

PUBSUB_TOPIC_PAYMENT_PROCESS = os.environ.get('PUBSUB_TOPIC_PAYMENT_PROCESS')

sde = stackdriver_exporter.StackdriverExporter(project_id="ubc-serverless-compliance")

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

    # Create an OpenCensus tracer to trace each payment process, and export
    # the data to Stackdriver Tracing.
    tracer = Tracer(exporter=sde)
    trace_id = tracer.span_context.trace_id 
    print("charge endpoint span context: ", tracer.span_context)
    print("charge endpoint trace id: ", trace_id)
    print("charge endpoint span id: ", tracer.span_context.span_id)

    # Prepare the order
    with tracer.span(name="prepare_order_info") as span_prepare_order_info:
        product_ids = form.product_ids.data
        stripe_token = form.stripeToken.data
        shipping = orders.Shipping(address_1=form.address_1.data,
                                   address_2=form.address_2.data,
                                   city=form.city.data,
                                   state=form.state.data,
                                   zip_code=form.zip_code.data,
                                   email=form.email.data,
                                   mobile=form.mobile.data)
        amount = product_catalog.calculate_total_price(product_ids)
        # get userId
        uid = auth_context.get('uid')
        order = orders.Order(amount=amount,
                             shipping=shipping,
                             status="order_created",
                             items=product_ids,
                             userId=uid)
        order_id = orders.add_order(order)

        serverEvent = time_event.MessageEvent(timestamp=datetime.datetime.utcnow(), id="EGYgJNh4JmOVWOC1yS4pnsK0GfF2",
                                              type=time_event.Type.SENT, uncompressed_size_bytes=1024, compressed_size_bytes=512)
        span_prepare_order_info.add_message_event(serverEvent)
        span_prepare_order_info.add_annotation(description="span prepare order info send description")

        # Stream a Payment event
        with tracer.span(name="send_payment_event") as span_send_payment_event:
            if stripe_token:
                # Publish an event to the topic for new payments.
                # Cloud Function pay_with_stripe subscribes to the topic and
                # processes the payment using the Stripe API upon arrival of new
                # events.
                # Cloud Function streamEvents (or App Engine service stream-event)
                # subscribes to the topic and saves the event to BigQuery for
                # data analytics upon arrival of new events.
                print("charge endpoint event context: ", order_id, stripe_token, trace_id)
                eventing.stream_event(
                    topic_name=PUBSUB_TOPIC_PAYMENT_PROCESS,
                    event_type='order_created',
                    event_context={
                        'order_id': order_id,
                        'token': stripe_token,
                        # Pass the trace ID in the event so that Cloud Function
                        # pay_with_stripe can continue the trace.
                        'trace_id': trace_id
                    }
                )
                serverEvent = time_event.MessageEvent(timestamp=datetime.datetime.utcnow(),
                                                      id="EGYgJNh4JmOVWOC1yS4pnsK0GfF2",
                                                      type=time_event.Type.SENT, uncompressed_size_bytes=1024,
                                                      compressed_size_bytes=512)
                span_send_payment_event.add_message_event(serverEvent)
                span_send_payment_event.add_annotation(description="span send payment event send description")

    return render_template("charge.html", auth_context=auth_context)
