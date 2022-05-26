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
import time
import datetime

from google.cloud import firestore
from google.cloud import pubsub_v1
from opencensus.trace.tracer import Tracer
from opencensus.ext.stackdriver import trace_exporter as stackdriver_exporter
from opencensus.trace.samplers import AlwaysOnSampler
# from opencensus.trace.exporters.transports.background_thread import BackgroundThreadTransport
from opencensus.trace import time_event
import stripe

import logging

API_KEY = os.environ.get('STRIPE_API_KEY')
GCP_PROJECT = os.environ.get('GCP_PROJECT')
PUBSUB_TOPIC_PAYMENT_COMPLETION = os.environ.get('PUBSUB_TOPIC_PAYMENT_COMPLETION')

firestore = firestore.Client()
publisher = pubsub_v1.PublisherClient()
sde = stackdriver_exporter.StackdriverExporter(project_id="ubc-serverless-compliance")
stripe.api_key = API_KEY


def pay_with_stripe(data, context):
    tracer = Tracer(exporter=sde, sampler=AlwaysOnSampler())

    logging.info("pay_with_stripe span context: ")
    logging.info(tracer.span_context)
    logging.info("pay_with_stripe trace id: ")
    logging.info(tracer.span_context.trace_id)
    logging.info("pay_with_stripe span id: ")
    logging.info(tracer.span_context.span_id)


    if 'data' in data:
        payment_request_json = base64.b64decode(data.get('data')).decode()
        payment_request = json.loads(payment_request_json)
        token = payment_request.get('event_context').get('token')
        order_id = payment_request.get('event_context').get('order_id')
        trace_id = payment_request.get('event_context').get('trace_id')
        tracer.span_context.trace_id = trace_id
        logging.info("pay_with_stripe event context: ")
        logging.info(payment_request.get('event_context'))
        logging.info("pay_with_stripe new span context: ") 
        logging.info(tracer.span_context)
        logging.info("pay_with_stripe new trace id: ")
        logging.info(tracer.span_context.trace_id)

        with tracer.span(name="process_payment") as span_process_payment:

            clientEvent = time_event.MessageEvent(timestamp=datetime.datetime.utcnow(),
                                                  id="EGYgJNh4JmOVWOC1yS4pnsK0GfF2",
                                                  type=time_event.Type.RECEIVED, uncompressed_size_bytes=1024,
                                                  compressed_size_bytes=512)
            span_process_payment.add_message_event(clientEvent)
            span_process_payment.add_annotation(description="span process payment receive description")

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
                # span.status = Status(0, "payment_processed")
                # span_process_payment.add_annotation("payment is processed!")
                
            except stripe.error.StripeError as err:
                logging.error(err)
                order_data['status'] = 'payment_failed'
                event_type = 'payment_failed'
                # span.status = Status(1, "payment_failed")
                # span_process_payment.add_annotation("payment process failed!")
            
            firestore.collection('orders').document(order_id).set(order_data)
            # logger.log_text("pay_with_stripe updated order in firestore!")
            logging.info("pay_with_stripe updated order in firestore!")
            stream_event(
                topic_name=PUBSUB_TOPIC_PAYMENT_COMPLETION,
                event_type=event_type,
                event_context={
                    'order_id': order_id,
                    'email': email,
                    'order': order_data
                }
            )
            logging.info("pay_with_stripe published payment completed event!")
            serverEvent = time_event.MessageEvent(timestamp=datetime.datetime.utcnow(),
                                                  id="EGYgJNh4JmOVWOC1yS4pnsK0GfF2",
                                                  type=time_event.Type.SENT, uncompressed_size_bytes=1024,
                                                  compressed_size_bytes=512)
            span_process_payment.add_message_event(serverEvent)
            span_process_payment.add_annotation(description="span process payment send description")

    return ''

def stream_event(topic_name, event_type, event_context):
    topic_path = publisher.topic_path(GCP_PROJECT, topic_name)
    request = {
        'event_type': event_type,
        'created_time': str(int(time.time())),
        'event_context': event_context
    }
    data = json.dumps(request).encode()
    publisher.publish(topic_path, data)
