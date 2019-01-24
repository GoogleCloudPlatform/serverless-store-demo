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

// Cloud Function for streaming events to BigQuery.
// See https://cloud.google.com/bigquery/streaming-data-into-bigquery for
// more information.

const {BigQuery} = require(`@google-cloud/bigquery`);

const DATASET = process.env.BIGQUERY_DATASET;
const TABLE = process.env.BIGQUERY_TABLE;

const bigquery = new BigQuery();
const dataset = bigquery.dataset(DATASET);
const table = dataset.table(TABLE);

exports.streamEvents = async (req, res) => {
    const messageString = Buffer.from(req.body.message.data, 'base64').toString();
    const message = JSON.parse(messageString);

    try{
        await table.insert({
            eventType: message.event_type,
            createdTime: message.created_time,
            context: JSON.stringify(mesage.event_context)
        })
    } catch (error) {
        console.log(error);
    }
}
