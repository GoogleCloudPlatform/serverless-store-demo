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
Data class for products.
"""


from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    """
    Data class for products.
    """
    name: str
    description: str
    image: str
    labels: List[str]
    price: float
    created_at: int
    id: str = None


    @staticmethod
    def deserialize(document):
        """
        Helper function for parsing a Firestore document to a Product object.

        Parameters:
           document (DocumentSnapshot): A snapshot of Firestore document.

        Output:
           A Product object.
        """
        data = document.to_dict()
        if data:
            return Product(
                id=document.id,
                name=data.get('name'),
                description=data.get('description'),
                image=data.get('image'),
                labels=data.get('labels'),
                price=data.get('price'),
                created_at=data.get('created_at')
            )

        return None


@dataclass
class PromoEntry:
    """
    Data class for promotions.
    """
    label: str
    score: float
    id: str = None


    @staticmethod
    def deserialize(document):
        """
        Helper function for parsing a Firestore document to a PromoEntry object.

        Parameters:
           document (DocumentSnapshot): A snapshot of Firestore document.

        Output:
           A PromoEntry object.
        """
        data = document.to_dict()
        if data:
            return PromoEntry(
                id=document.id,
                label=data.get('label'),
                score=data.get('score')
            )

        return None
