## Create a docker image

`docker build -t gcr.io/ubc-serverless-compliance/frontend:latest .`

## Push image

`docker push gcr.io/ubc-serverless-compliance/frontend:latest`

## Deploy image to Cloud Run

```bash
gcloud beta run deploy frontend --image=gcr.io/ubc-serverless-compliance/frontend:latest \
    --set-env-vars GCP_PROJECT=ubc-serverless-compliance \
    --set-env-vars PUBSUB_TOPIC_NEW_PRODUCT=new-product \
    --set-env-vars PUBSUB_TOPIC_PAYMENT_PROCESS=payment-process \
    --set-env-vars GCS_BUCKET=serverless-store-bucket-2-gokce \
    --set-env-vars FIREBASE_CONFIG=firebase_config.json
```
