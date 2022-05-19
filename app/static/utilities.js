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

// A collection of scripts for common operations.

const addToCartURL = `/cart`;
const deleteFromCartURL = `/cart`;
var provider = new firebase.auth.GoogleAuthProvider();

async function addToCartRequest(id, update, restore) {
  try {
    await fetch(addToCartURL, {
      method: 'POST',
      mode: 'same-origin',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      redirect: 'error',
      referrer: 'no-referrer',
      body: `id=${id}`,
    });
    update();
  } catch (error) {
    console.log(error);
    restore();
  }
}

function addToCartInProductCatalog(button) {
  const id = button.attributes.getNamedItem(`data-product-id`).value;
  button.innerText = `Processing`;
  button.attributes.onclick = ``;
  function updateButton() {
    button.attributes.onclick = `removeFromCartInProductCatalog(this)`;
    button.innerText = `Remove`;
  }
  function restoreButton() {
    button.innerText = `Add to Cart`;
    button.attributes.onclick = `addToCartInProductCatalog(this)`;
  }
  addToCartRequest(id, updateButton, restoreButton);
}

function getCookie(name) {
  let cookie = {};
  document.cookie.split(';').forEach(function (el) {
    let [k, v] = el.split('=');
    cookie[k.trim()] = v;
  });
  return cookie[name];
}

async function removeFromCartRequest(id, update, restore) {
  try {
    await fetch(deleteFromCartURL, {
      method: 'DELETE',
      mode: 'same-origin',
      cache: 'no-cache',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      redirect: 'error',
      referrer: 'no-referrer',
      body: `id=${id}`,
    });
    update();
  } catch (error) {
    console.log(error);
    restore();
  }
}

function removeFromCartInProductCatalog(button) {
  const id = button.attributes.getNamedItem(`data-product-id`).value;
  button.innerText = `Processing`;
  button.attributes.onclick = ``;
  function updateButton() {
    button.attributes.onclick = `addToCartInProductCatalog(this)`;
    button.innerText = `Add to Cart`;
  }
  function restoreButton() {
    button.innerText = `Remove`;
    button.attributes.onclick = `removeFromCartInProductCatalog(this)`;
  }
  removeFromCartRequest(id, updateButton, restoreButton);
}

function removeFromCartInCart(button) {
  const id = button.attributes.getNamedItem(`data-product-id`).value;
  button.attributes.innerHTML = `Processing`;
  button.attributes.onclick = ``;
  function updateSection() {
    document.getElementById(`section-${id}`).remove();
  }
  function restoreButton() {
    button.attributes.class = `button`;
    button.attributes.onclick = `removeFromCartInProductCatalog(this)`;
    button.innerHTML = `<i class="fas fa-trash"></i>`;
  }
  removeFromCartRequest(id, updateSection, restoreButton);
}

function submitSellForm() {
  let name = document.getElementById('name-input').value;
  let description = document.getElementById('description-input').value;
  let price = document.getElementById('price-input').value;
  let image = document.getElementById('image').value;
  if (!name || !description || !price || !parseFloat(price) || !image) {
    return alert(
      `Some fields might be empty or incorrect. Please make ` +
        `sure that all the required fields have been completed ` +
        `correctly, and an image has been uploaded.`
    );
  }
  document.getElementById('name').value = name;
  document.getElementById('description').value = description;
  document.getElementById('price').value = price;
  document.getElementById('sell-form').submit();
}
