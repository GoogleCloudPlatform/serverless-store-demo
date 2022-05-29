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

// App Engine service for streaming events to BigQuery.
// See https://cloud.google.com/bigquery/streaming-data-into-bigquery for
// more information.

const { BigQuery } = require(`@google-cloud/bigquery`);
// const { Logging } = require('@google-cloud/logging');
const express = require(`express`);

const DATASET = process.env.BIGQUERY_DATASET;
const TABLE = process.env.BIGQUERY_TABLE;

const bigquery = new BigQuery();
const dataset = bigquery.dataset(DATASET);
const table = dataset.table(TABLE);

const tracing = require('@opencensus/nodejs');
const {
  StackdriverTraceExporter,
} = require('@opencensus/exporter-stackdriver');

// Add your project id to the Stackdriver options
const exporter = new StackdriverTraceExporter({
  projectId: 'ubc-serverless-compliance',
});

tracing.registerExporter(exporter).start();

const app = express();
app.use(express.json());

const tracer = tracing.start({ samplingRate: 1 }).tracer;

app.get(`/`, (req, res) => {
  res.send(200);
});

app.post(`/stream`, async (req, res) => {
  const span = tracer.startChildSpan('stream events app');
  span.start();

  console.log('streamEvents received buffer: ', req.body.message.data);
  const messageString = Buffer.from(req.body.message.data, `base64`).toString();
  console.log('streamEvents received string: ', messageString);
  const message = JSON.parse(messageString);
  console.log('streamEvents parsed string: ', message);

  try {
    await table.insert({
      eventType: message.event_type,
      createdTime: message.created_time,
      context: JSON.stringify(message.event_context),
    });
    console.log('streamEvents successfully saved: ', message);
    span.addAnnotation('streamEvents succeeded!');
    span.end();
    res.send(200);
  } catch (error) {
    console.log('streamEvents error: ', error);
    span.addAnnotation('streamEvents failed!');
    span.end();
    res.send(500, `Failed to stream the event to BigQuery.`);
  }
});

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
