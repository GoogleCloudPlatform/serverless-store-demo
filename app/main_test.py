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
System tests.
"""


import os
from unittest.mock import MagicMock

import pytest

TEST_UID = os.environ.get('TEST_UID')
TEST_PRODUCT_ID = os.environ.get('TEST_PRODUCT_ID')
TEST_PRODUCT_NAME = os.environ.get('TEST_PRODUCT_NAME')


@pytest.fixture
def client():
    """
    Gets a Flask Test Client with authentication disabled.
    """
    # Disable auth
    import middlewares.auth
    middlewares.auth.verify_firebase_id_token = MagicMock()
    middlewares.auth.verify_firebase_id_token.return_value = {
        'uid': TEST_UID,
        'username': 'user',
        'email': 'user@example.com'
    }

    import main
    main.app.testing = True
    client = main.app.test_client()
    client.set_cookie('localhost', 'firebase_id_token', '*')
    return client


def test_product_catalog(client):
    """
    Should display the product catalog page.
    """
    r = client.get('/')
    assert r.status_code == 200
    assert 'Serverless Store' in str(r.data)


def test_cart(client):
    """
    Should display the cart page.
    """
    r = client.get('/cart')
    assert r.status_code == 200
    assert 'Shopping Cart' in str(r.data)


def test_checkout_single_product(client):
    """
    Should display the checkout page (single item).
    """
    r = client.get(f'/checkout?id={TEST_PRODUCT_ID}')
    assert r.status_code == 200
    assert f'{TEST_PRODUCT_NAME}' in str(r.data)


def test_checkout_cart(client):
    """
    Should display the checkout page (cart).
    """
    r = client.get('/checkout?from_cart=1')
    assert r.status_code == 200
    assert f'{TEST_PRODUCT_NAME}' in str(r.data)


def test_sell(client):
    """
    Should display the sell page.
    """
    r = client.get('/sell')
    assert r.status_code == 200
    assert 'Join the marketplace' in str(r.data)


def test_signin(client):
    """
    Should display the sell page.
    """
    r = client.get('/signin')
    assert r.status_code == 200
