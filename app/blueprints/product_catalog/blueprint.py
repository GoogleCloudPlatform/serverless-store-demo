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
This module is the Flask blueprint for the product catalog page (/).
"""


from flask import Blueprint, render_template

from helpers import product_catalog
from middlewares.auth import auth_optional

product_catalog_page = Blueprint('product_catalog_page', __name__)


@product_catalog_page.route('/')
@auth_optional
def display(auth_context):
    """
    View function for displaying the product catalog.

    Parameters:
       auth_context (dict): The authentication context of request.
                            See middlewares/auth.py for more information.
    Output:
       Rendered HTML page.
    """

    products = product_catalog.list_products()
    # Get promoted products recommended by the AutoML model.
    promos = product_catalog.get_promos()
    return render_template('product_catalog.html',
                           products=products,
                           promos=promos,
                           auth_context=auth_context,
                           bucket=product_catalog.BUCKET)
