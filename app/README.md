# Converting to Cloud Run

For Cloud Run, all we need is a container. To get a container
we need a Dockerfile (which is in this app directory).

## Create a docker image

Assuming you have docker installed locally

`docker build -t gcr.io/PROJECT_ID/frontend:latest .`

## Push image

`docker push gcr.io/PROJECT_ID/frontend:latest`

## Deploy image to Cloud Run

Replace placeholder values with your own.

```bash
gcloud beta run deploy frontend --region=us-central1 \
    --image=gcr.io/PROJECT_ID/frontend:latest \
    --set-env-vars GCP_PROJECT=PROJECT_ID,PUBSUB_TOPIC_NEW_PRODUCT=new-product,\
    PUBSUB_TOPIC_PAYMENT_PROCESS=payment-process,\
    GCS_BUCKET=GCS_BUCKET,\
    FIREBASE_CONFIG=firebase_config.json

```
