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
Cloud Function for performing Cloud Vision image labeling.
"""


import base64
import json
import os

from google.cloud import firestore
from google.cloud import vision

vision_client = vision.ImageAnnotatorClient()
firestore_client = firestore.Client()

GCS_BUCKET = os.environ.get('GCS_BUCKET')

def detect_labels(data, context):
    if 'data' in data:
        request_json = base64.b64decode(data.get('data')).decode()
        request = json.loads(request_json)
        product_id = request.get('event_context').get('product_id')
        product_image = request.get('event_context').get('product_image')

        image = vision.types.Image()
        image.source.image_uri = 'gs://{}/{}.png'.format(GCS_BUCKET, product_image)
        response = vision_client.label_detection(image=image)
        labels = response.label_annotations
        top_labels = [ label.description for label in labels[:3] ]

        product_data = firestore_client.collection('products').document(product_id).get().to_dict()
        product_data['labels'] = top_labels
        firestore_client.collection('products').document(product_id).set(product_data)
    
    return ''