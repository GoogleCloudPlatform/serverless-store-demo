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
This module is the main flask application.
"""


import firebase_admin
from flask import Flask

from blueprints import *


# Initialize Firebase Admin SDK.
# See https://firebase.google.com/docs/admin/setup for more information.
firebase = firebase_admin.initialize_app()


# Enable Google Cloud Debugger
# See https://cloud.google.com/debugger/docs/setup/python for more information.
try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass


app = Flask(__name__)
app.secret_key = b'A Super Secret Key'


app.register_blueprint(cart_page)
app.register_blueprint(charge_page)
app.register_blueprint(checkout_page)
app.register_blueprint(product_catalog_page)
app.register_blueprint(sell_page)
app.register_blueprint(signin_page)


if __name__ == '__main__':
    app.run(debug=True)
