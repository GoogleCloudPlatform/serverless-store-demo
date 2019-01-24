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


# This module is the Flask blueprint for the sign-in page (/signin).


from flask import Blueprint, render_template

signin_page = Blueprint('signin_page', __name__)


@signin_page.route('/signin')
def display():
    """
    View function for displaying the sign-in page.

    Parameters:
       None
    Output:
       Rendered HTML page.
    """
    return render_template("signin.html")

