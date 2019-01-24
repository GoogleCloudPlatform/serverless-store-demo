# Cloud Function for Event Streaming

This function is provided as an alternative to the streamEvents App Engine
Service (`/extras/streamEvents`). To use this function, set up [Firebase Hosting
with Cloud Functions](https://firebase.google.com/docs/hosting/functions)
using your domain, whitelist your domain in Google Cloud Platform,
and create Pub/Sub subscriptions with the URL.

See [Configuring HTTP Endpoints](https://cloud.google.com/pubsub/docs/push#configuring-http-endpoints)
for more information.
