# Instructions for deploying Serverless Store without using Cloud Build

Note: The following instructions help you deploy Serverless Store demo
components one by one using a local installation of Cloud SDK. It is advised
that you use Cloud Build to deploy all the components at once instead; for
more information, see [Set up Serverless Store: Part 3](https://medium.com/@ratrosy/set-up-serverless-store-part-3-computing-cron-jobs-and-management-tools-34d51475df70).

## Deploy to App Engine

1. Edit `app/app.yaml` and replace `YOUR-PROJECT`, `YOUR-NEW-PRODUCT-TOPIC`,
`YOUR-GCS-BUCKET`, and `YOUR-PAYMENT-TOPIC` with values of your own. `app.yaml`
is the App Engine configuration file. If you have followed the naming in this
setup guide, your `app.yaml` should look this after editing:

    ```
    runtime: python37

    env_variables:
    GCP_PROJECT: "my-project"
    PUBSUB_TOPIC_NEW_PRODUCT: "new-product"
    PUBSUB_TOPIC_PAYMENT_PROCESS: "payment-process"
    GCS_BUCKET: "my-gcs-bucket"
    FIREBASE_CONFIG: "firebase_config.json"

    handlers:
    - url: /static
        static_dir: static
    ```

2. Open a terminal and switch to the `app/` directory. If you have never used
App Engine before in the project, run the command below and follow the prompts
on screen to create an App Engine app:

    `gcloud app create`

3. After creating the app, deploy the code with:

    `gcloud app deploy`

4. Aside from the main app, the project also requires a separate App Engine
service for streaming events to BigQuery. Switch to `extras/streamEventsApp/`,
and edit the `app.yaml` file. Replace `YOUR-DATASET` and `YOUR-TABLE` with
values of your own; if you have followed the naming in this setup guide,
the two values should be `sample_data` and `sample_table` respectively.
Then run command:

    `gcloud app deploy`

    The App Engine service is available at `stream-events-dot-YOUR-PROJECT-ID.appspot.com`.
    Any event pushed to the `/stream` endpoint via HTTP will be streamed to
    BigQuery.

# Deploy to Cloud Functions

1. Open a terminal and switch to directory `functions/automl`. This is the
Cloud Function for calling the Cloud AutoML Vision model. Run command:

    ```
    # Replace YOUR-NEW-PRODUCT-TOPIC, YOUR-MODEL-ID, and YOUR-BUCKET with
    # values of your own. If you have followed the naming in this setup
    # guide, YOUR-NEW-PRODUCT-TOPIC should be new-product.
    #
    gcloud beta functions deploy automl \
                                --runtime python37 \
                                --trigger-topic YOUR-NEW-PRODUCT-TOPIC \
                                --set-env-vars AUTOML_MODEL_ID=YOUR-MODEL-ID,GCS_BUCKET=YOUR-BUCKET
    ```

2. Switch to directory `functions/detect_labels`. This is the Cloud Function
for calling the Cloud Vision API. Run command:

    ```
    # Replace YOUR-NEW-PRODUCT-TOPIC and YOUR-BUCKET with values of your own.
    # If you have followed the naming in this setup guide, YOUR-NEW-PRODUCT-TOPIC
    # should be new-product.
    #
    gcloud beta functions deploy detect_labels \
                                --runtime python37 \
                                --trigger-topic YOUR-NEW-PRODUCT-TOPIC \
                                --set-env-vars GCS_BUCKET=YOUR-BUCKET
    ```

3. Switch to directory `functions/pay_with_stripe`. This is the Cloud Function
for calling the Stripe API. Run command:

    ```
    # Replace YOUR-PAYMENT-TOPIC, YOUR-STRIPE-API-KEY, and YOUR-PAYMENT-COMPLETION-TOPIC
    # with values of your own. If you have followed the naming in this setup guide,
    # YOUR-PAYMENT-TOPIC and YOUR-PAYMENT-COMPLETION-TOPIC should be payment-process
    # and payment-completion respectively.
    #
    gcloud beta functions deploy pay_with_stripe \
                        --runtime python37 \
                        --trigger-topic YOUR-PAYMENT-TOPIC \
                        --set-env-vars STRIPE_API_KEY=YOUR-STRIPE-API-KEY,PUBSUB_TOPIC_PAYMENT_COMPLETION=YOUR-PAYMENT-COMPLETION-TOPIC

    ```

4. Switch to directory `functions/sendOrderConfirmation`. This is the Cloud
Function for calling the SendGrid API. Run command:

    ```
    # Replace YOUR-SENDGRID-API-KEY, and YOUR-PAYMENT-COMPLETION-TOPIC with values of
    # your own. If you have followed the naming in this setup guide,
    # YOUR-PAYMENT-COMPLETION-TOPIC should be payment-completion.
    #
    gcloud beta functions deploy sendOrderConfirmation \
                                --runtime nodejs8 \
                                --trigger-topic YOUR-PAYMENT-COMPLETION-TOPIC \
                                --set-env-vars SENDGRID_API_KEY=YOUR-SENDGRID-API-KEY
    ```

5. Switch to directory `functions/upload_image`. This is the Cloud Function
for saving uploaded images to Cloud Storage. Run command:

    ```
    # Replace YOUR-BUCKET with the value of your own.
    #
    gcloud beta functions deploy upload_image \
                                --runtime python37 \
                                --trigger-http \
                                --set-env-vars GCS_BUCKET=YOUR-BUCKET
    view raw
    ```

Your app is now available at `YOUR-PROJECT-ID.appspot.com`. You can view all
the App Engine services via [App Engine Services page](https://pantheon.corp.google.com/appengine/services)
in Google Cloud Console. Before you open the app, there is two more things to do:

1. Open [Firebase Console](https://console.firebase.google.com/) and go to
your project.
2. Go to the **Authentication** page.
3. Go to the **Sign-in** method tab.
4. Click **Add domain** and whitelist `YOUR-PROJECT-ID.appspot.com`.
5. Open the [Cloud Pub/Sub page](https://console.cloud.google.com/cloudpubsub) in Google Cloud Console.
6. Click the `new-product` Pub/Sub topic.
7. Click **Create Subscription**.
8. Type in the name of the subscription.
9. Pick the **Push into an endpoint URL** delivery type.
10. Use the URL `stream-events-dot-YOUR-PROJECT-ID.appspot.com/stream` as the
URL. Replace `YOUR-PROJECT-ID` with the value of your own.
11. Click **Create**. The App Engine service you deploy earlier is now a
subscriber of the `new-product` topic and will stream all the incoming events
to Google BigQuery.
12. Repeat the steps above for topics `payment-process` and `payment-completion`.

Now, open the app and try signing in with your Google account,
adding some items, purchasing an item, and watch the events flow via
Google Data Studio.
