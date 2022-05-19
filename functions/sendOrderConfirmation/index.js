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

// Cloud Function for sending order confirmations.

const Firestore = require(`@google-cloud/firestore`);
const pug = require(`pug`);
const SendGrid = require(`@sendgrid/mail`);

const firestore = new Firestore();

SendGrid.setApiKey(process.env.SENDGRID_API_KEY);

async function prepareOrderConfirmation(type, context) {
  var emailTemplateDocument = await firestore
    .collection(`emails`)
    .doc(type)
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
    pugSource = emailTemplate.template;
  }
  var compile = pug.compile(pugSource);

  return {
    to: context.email,
    from: from,
    subject: subject,
    html: compile(context)
  };
}

/* eslint-disable no-unused-vars */
exports.sendOrderConfirmation = async (data, context) => {
  console.log('sendOrderConfirmation received message: ', data.data)
  const messageString = Buffer.from(data.data, `base64`).toString();
  console.log('sendOrderConfirmation received message string: ', messageString)
  const message = JSON.parse(messageString);
  console.log('sendOrderConfirmation parsed message: ', message)
  const eventType = message.event_type;
  const eventContext = message.event_context;

  try {
    var mail = await prepareOrderConfirmation(eventType, eventContext);
    console.log('sendOrderConfirmation created mail: ', mail)
    await SendGrid.send(mail)
    console.log('sendOrderConfirmation successfully sent mail: ', mail);
  } catch (error) {
    console.log('sendOrderConfirmation error: ', error);
  }
};
