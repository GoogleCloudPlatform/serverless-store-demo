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
A collection of helper functions for order related operations.
"""


from dataclasses import asdict
import uuid

from google.cloud import firestore

from .data_classes import Order

firestore = firestore.Client()

def add_order(order):
    """
    Helper function for adding an order.

    Parameters:
       order (Order): An Order object.

    Output:
       The ID of the order.
    """

    order_id = uuid.uuid4().hex
    firestore.collection('orders').document(order_id).set(asdict(order))
    return order_id


def get_order(order_id):
    """
    Helper function for getting an order.

    Parameters:
       order_id (str): The ID of the order.

    Output:
       An Order object.
    """

    order_data = firestore.collection('orders').document(order_id).get()
    return Order.deserialize(order_data)
