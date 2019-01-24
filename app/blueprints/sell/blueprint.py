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
This module is the Flask blueprint for the sell page (/sell).
"""


import os
import time

from flask import Blueprint, redirect, render_template, url_for

from helpers import eventing, product_catalog
from middlewares.auth import auth_required
from middlewares.form_validation import SellForm, sell_form_validation_required

PUBSUB_TOPIC_NEW_PRODUCT = os.environ.get('PUBSUB_TOPIC_NEW_PRODUCT')

sell_page = Blueprint('sell_page', __name__)


@sell_page.route('/sell', methods=['GET'])
@auth_required
def display(auth_context):
    """
    View function for displaying the sell page.

    Parameters:
       auth_context (dict): The authentication context of request.
                            See middlewares/auth.py for more information.
    Output:
       Rendered HTML page.
    """

    # Prepares the sell form.
    # See middlewares/form_validation.py for more information.
    form = SellForm()
    return render_template('sell.html', auth_context=auth_context, form=form)


@sell_page.route('/sell', methods=['POST'])
@auth_required
@sell_form_validation_required
def process(auth_context, form):
    """
    View function for processing sell requests.

    Parameters:
       auth_context (dict): The authentication context of request.
                            See middlewares/auth.py for more information.
       form (SellForm): A validated sell form.
                        See middlewares/form_validation.py for more
                        information.
    Output:
       Rendered HTML page.
    """

    product = product_catalog.Product(name=form.name.data,
                                      description=form.description.data,
                                      image=form.image.data,
                                      labels=[],
                                      price=form.price.data,
                                      created_at=int(time.time()))
    product_id = product_catalog.add_product(product)
    # Publish an event to the topic for new products.
    # Cloud Function detect_labels subscribes to the topic and labels the
    # product using Cloud Vision API upon arrival of new events.
    # Cloud Function streamEvents (or App Engine service stream-event)
    # subscribes to the topic and saves the event to BigQuery for
    # data analytics upon arrival of new events.
    eventing.stream_event(
        topic_name=PUBSUB_TOPIC_NEW_PRODUCT,
        event_type='label_detection',
        event_context={
            'product_id': product_id,
            'product_image': product.image
        })

    return redirect(url_for('product_catalog_page.display'))
