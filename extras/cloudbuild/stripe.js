// Copyright 2018 Google LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Script for configuring Stripe.js.
// See https://stripe.com/docs for more information.

var stripe = Stripe('');
var elements = stripe.elements();
var style = {
  base: {
    color: '#32325d',
    lineHeight: '18px',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
      color: '#aab7c4',
    },
  },
  invalid: {
    color: '#fa755a',
    iconColor: '#fa755a',
  },
};

var card = elements.create('card', { style: style });
card.mount('#card-element');

card.addEventListener('change', function (event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

function stripePayButtonClicked() {
  stripe.createToken(card).then(function (result) {
    if (result.error) {
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      stripeTokenHandler(result.token);
    }
  });
}

function stripeTokenHandler(token) {
  let addressA = document.getElementById('address_1_input').value;
  let addressB = document.getElementById('address_2_input').value;
  let city = document.getElementById('city_input').value;
  let state = document.getElementById('state_input').value;
  let zipCode = document.getElementById('zip_code_input').value;
  let email = document.getElementById('email_input').value;
  let mobile = document.getElementById('mobile_input').value;

  if (!addressA || !city || !state || !zipCode || !email || !mobile) {
    return alert(
      `Some fields might be empty or incorrect. Please make ` +
        `sure that all the required fields have been completed correctly.`
    );
  }

  var paymentForm = document.getElementById('payment-form');
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'stripeToken');
  hiddenInput.setAttribute('value', token.id);
  paymentForm.appendChild(hiddenInput);

  document.getElementById('address_1').value = addressA;
  document.getElementById('address_2').value = addressB;
  document.getElementById('city').value = city;
  document.getElementById('state').value = state;
  document.getElementById('zip_code').value = zipCode;
  document.getElementById('email').value = email;
  document.getElementById('mobile').value = mobile;

  paymentForm.submit();
}
