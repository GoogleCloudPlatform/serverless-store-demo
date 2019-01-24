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
A collection of helper functions for cart related operations.
"""


from dataclasses import asdict
import time

from google.cloud import firestore

from .data_classes import CartItem

firestore_client = firestore.Client()


def get_cart(uid):
    """
    Helper function for getting all items in a cart.

    Parameters:
       uid (str): The unique ID of an user.

    Output:
       A list of CartItem.
    """

    cart = []
    query_results = firestore_client.collection('carts').where('uid', '==', uid).order_by('modify_time', direction=firestore.Query.DESCENDING).get()
    for result in query_results:
        item = CartItem.deserialize(result)
        cart.append(item)
    return cart


def add_to_cart(uid, item_id):
    """
    Helper function for adding an item to a cart.

    Parameters:
       uid (str): The unique ID of an user.
       item_id (str): The ID of an item.

    Output:
       None.
    """

    item = CartItem(
        uid=uid,
        item_id=item_id,
        modify_time=int(time.time()))

    firestore_client.collection('carts').document().set(asdict(item))


def remove_from_cart(uid, item_id):
    """
    Helper function for deleting an item from a cart.

    Parameters:
       uid (str): The unique ID of an user.
       item_id (str): The ID of an item.

    Output:
       None.
    """

    transaction = firestore_client.transaction()

    @firestore.transactional
    def transactional_remove_from_cart(transaction, uid, item_id):
        query_results = firestore_client.collection('carts').where('uid', '==', uid).where('item_id', '==', item_id).get()
        for result in query_results:
            reference = firestore_client.collection('carts').document(result.id)
            transaction.delete(reference)

    transactional_remove_from_cart(transaction, uid, item_id)
