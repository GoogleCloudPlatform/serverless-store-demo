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

// Cloud Function for sending reminders of forgotten cart items.
// This Cloud Function is for demo purposes only. For production apps, you
// should use a more efficient solution ready for long time tasks.

const firebaseAdmin = require(`firebase-admin`);
const Firestore = require(`@google-cloud/firestore`);
const pug = require(`pug`);
const SendGrid = require(`@sendgrid/mail`);

const TIME_LIMIT = 7 * 24 * 3600;

firebaseAdmin.initializeApp();
const firestore = new Firestore();
SendGrid.setApiKey(process.env.SENDGRID_API_KEY);

/* eslint-disable no-unused-vars */
exports.sendReminder = async (req, res) => {
  // Query forgotten cart items
  var carts = new Map();
  var queryResults = await firestore
    .collection(`carts`)
    .where(`modify_time`, "<=", Math.round(Date.now() / 1000) - TIME_LIMIT)
    .get();
  queryResults.forEach(document => {
    var data = document.data();
    var cart = carts.get(data.uid);
    if (!cart) {
      cart = [data.item_id];
    } else {
      cart.push(data.item_id);
    }
    carts.set(data.uid, cart);
  });

  // Prepare the reminder email
  var emailTemplateDocument = await firestore
    .collection(`emails`)
    .doc(`cart_item_reminder`)
    .get();

  var subject;
  var from;
  var pugSource;
  if (!emailTemplateDocument.exists) {
    throw new Error(`Invalid template type.`);
  } else {
    var emailTemplate = emailTemplateDocument.data();
    subject = emailTemplate.subject;
    from = emailTemplate.from;
    pugSource = emailTemplate.pug_source;
  }
  var compile = pug.compile(pugSource);

  // Send the reminder email
  for (const [uid, cart] of carts) {
    const user = await firebaseAdmin.auth().getUser(uid);
    const to = user.email;
    await SendGrid.send({
      to: to,
      from: from,
      subject: subject,
      html: compile(cart)
    });
  }
};
