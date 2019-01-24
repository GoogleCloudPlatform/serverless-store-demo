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
This module is the Flask blueprint for the checkout page (/checkout).
"""


from flask import Blueprint, redirect, render_template, request, url_for

from helpers import carts, product_catalog
from middlewares.auth import auth_optional
from middlewares.form_validation import CheckOutForm

checkout_page = Blueprint("checkout_page", __name__)


@checkout_page.route('/checkout')
@auth_optional
def display(auth_context):
    """
    View function for displaying the checkout page.

    Parameters:
       auth_context (dict): The authentication context of request.
                            See middlewares/auth.py for more information.
    Output:
       Rendered HTML page.
    """

    products = []
    # Prepares the checkout form.
    # See middlewares/form_validation.py for more information.
    form = CheckOutForm()
    product_id = request.args.get('id')
    from_cart = request.args.get('from_cart')
    # Checkout one single item if parameter id presents in the URL query string.
    # Checkout all the items in the user's cart if parameter from_cart presents
    # in the URL query string and parameter id is absent.
    if product_id:
        product = product_catalog.get_product(product_id)
        products.append(product)
    elif from_cart:
        uid = auth_context.get('uid')
        cart = carts.get_cart(uid)
        for item in cart:
            product = product_catalog.get_product(item.item_id)
            products.append(product)

    if products:
        return render_template('checkout.html',
                               products=products,
                               auth_context=auth_context,
                               form=form,
                               bucket=product_catalog.BUCKET)

    return redirect(url_for('product_catalog_page.display'))
