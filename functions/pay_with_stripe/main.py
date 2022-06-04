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
Cloud Function for processing Stripe payments.
"""


import base64
import json
import os
import random
import time
import datetime

from google.cloud import firestore
from google.cloud import pubsub_v1
import stripe

from opentelemetry import trace, baggage
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Link
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

import logging

API_KEY = os.environ.get('STRIPE_API_KEY')
GCP_PROJECT = os.environ.get('GCP_PROJECT')
PUBSUB_TOPIC_PAYMENT_COMPLETION = os.environ.get('PUBSUB_TOPIC_PAYMENT_COMPLETION')

firestore = firestore.Client()
publisher = pubsub_v1.PublisherClient()
stripe.api_key = API_KEY


def pay_with_stripe(data, context):

    # [START opentelemetry_setup_exporter]
    tracer_provider = TracerProvider()
    cloud_trace_exporter = CloudTraceSpanExporter(project_id="ubc-serverless-compliance")
    tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)
    # [END opentelemetry_setup_exporter]

    if 'data' in data:
        payment_request_json = base64.b64decode(data.get('data')).decode()
        payment_request = json.loads(payment_request_json)
        token = payment_request.get('event_context').get('token')
        order_id = payment_request.get('event_context').get('order_id')

        carrier = payment_request.get('carrier')
        logging.info("pay_with_stripe carrier: ")
        logging.info(carrier)
        ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
        logging.info("pay_with_stripe received context: ")
        logging.info(ctx)

        with tracer.start_as_current_span("pay_with_stripe_process_payment", context=ctx,
                                          kind=trace.SpanKind.CONSUMER) as link_target:
            userToken = carrier.get('uid')
            link_target.set_attribute("userToken", userToken)
            logging.info("pay_with_stripe link_target context: ")
            logging.info(link_target.get_span_context())

            with tracer.start_as_current_span("process_with_payment_first_link",
                                              kind=trace.SpanKind.CONSUMER) as first_link:
                order_data = firestore.collection('orders').document(order_id).get().to_dict()
                amount = order_data.get('amount')
                email = order_data.get('shipping').get('email')

                try:
                    # charge = stripe.Charge.create(
                    #     # For US Dollars, Stripe use Cent as the unit
                    #     amount=int(amount * 100),
                    #     currency='usd',
                    #     description='Example charge',
                    #     source=token
                    # )
                    order_data['status'] = 'payment_processed'
                    event_type = 'payment_processed'

                except stripe.error.StripeError as err:
                    logging.error(err)
                    order_data['status'] = 'payment_failed'
                    event_type = 'payment_failed'
            
                firestore.collection('orders').document(order_id).set(order_data)
                logging.info("pay_with_stripe updated order in firestore!")
                logging.info("process_with_payment_first_link context: ")
                logging.info(first_link.get_span_context())
                # child_ctx = baggage.set_baggage("current_context", "child")
                first_link.add_event(name="update firestore")

            with tracer.start_as_current_span("process_with_payment_second_link",
                                              kind=trace.SpanKind.CONSUMER) as second_link:
                carrier = dict()
                carrier['uid'] = userToken
                TraceContextTextMapPropagator().inject(carrier=carrier)

                stream_event(
                    topic_name=PUBSUB_TOPIC_PAYMENT_COMPLETION,
                    event_type=event_type,
                    event_context={
                        'order_id': order_id,
                        'email': email,
                        'order': order_data
                    },
                    carrier=carrier
                )
                logging.info("pay_with_stripe published payment completed event!")
                second_link.add_event(name="publish payment completed event")
                logging.info("process_with_payment_second_link context: ")
                logging.info(second_link.get_span_context())

    return ''

def stream_event(topic_name, event_type, event_context, carrier):
    topic_path = publisher.topic_path(GCP_PROJECT, topic_name)
    request = {
        'event_type': event_type,
        'created_time': str(int(time.time())),
        'event_context': event_context,
        'carrier': carrier
    }
    data = json.dumps(request).encode()
    publisher.publish(topic_path, data)
