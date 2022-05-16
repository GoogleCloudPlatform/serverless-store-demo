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
Cloud Function for performing AutoML Vision predictions.
"""


import base64
import json
import os

from google.cloud import automl_v1beta1
from google.cloud import firestore
from google.cloud import storage

AUTOML_MODEL_ID = os.environ.get('AUTOML_MODEL_ID')
AUTOML_PROJECT = os.environ.get('AUTOML_PROJECT')
if not AUTOML_PROJECT:
    AUTOML_PROJECT = os.environ.get('GCP_PROJECT')
BUCKET = os.environ.get('GCS_BUCKET')

automl_predict_client = automl_v1beta1.PredictionServiceClient()
firestore_client = firestore.Client()
storage_client = storage.Client()

def automl(data, context):
    if 'data' in data:
        request_json = base64.b64decode(data.get('data')).decode()
        request = json.loads(request_json)
        product_id = request.get('event_context').get('product_id')
        # product_image = request.get('event_context').get('product_image')

        # bucket = storage_client.get_bucket(BUCKET)
        # blob = bucket.blob(f'{product_image}.png')
        # image_data = blob.download_as_string()

        # model_name = f'projects/{AUTOML_PROJECT}/locations/us-central1/models/{AUTOML_MODEL_ID}'
        # payload = {
        #     'image': {
        #         'image_bytes': image_data
        #     }
        # }
        # response = automl_predict_client.predict(model_name, payload)
        # top_result = response.payload[0]
        # label = top_result.display_name
        # score = top_result.classification.score

        firestore_client.collection('promos').document(product_id).set({
            # 'label': label,
            # 'score': score
            'label': "label",
            'score': "score"
        })

    return ''
