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
Data class for orders.
"""


from dataclasses import dataclass
from typing import List


@dataclass
class Shipping:
    """
    Data class for shipping information.
    """
    address_1: str
    address_2: str
    city: str
    state: str
    zip_code: str
    email: str
    mobile: str


    @staticmethod
    def deserialize(data):
        """
        Helper function for parsing a dict of shipping data to a Shipping object.

        Parameters:
           data (dict): A dict of shipping data.

        Output:
           A Shipping object.
        """
        if data:
            return Shipping(
                address_1=data.get('address_1'),
                address_2=data.get('address_2'),
                city=data.get('city'),
                state=data.get('state'),
                zip_code=data.get('zip_code'),
                email=data.get('email'),
                mobile=data.get('mobile')
            )

        return None


@dataclass
class Order:
    """
    Data class for orders.
    """
    amount: float
    shipping: Shipping
    status: str
    items: List[str]
    id: str = None


    @staticmethod
    def deserialize(document):
        """
        Helper function for parsing a Firestore document to an Order object.

        Parameters:
          document (DocumentSnapshot): A snapshot of Firestore document.

        Output:
          An Order object.
        """
        data = document.to_dict()
        if data:
            return Order(
                id=document.id,
                amount=data.get('amount'),
                shipping=Shipping.deserialize(data.get('shipping')),
                status=data.get('status'),
                items=data.get('items')
            )

        return None
