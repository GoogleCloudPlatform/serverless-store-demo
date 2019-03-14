# Serverless Store: Google Cloud Platform Serverless Demo Application

Serverless Store is a Google-provided web e-commerce demo app where users
can list, browse and purchase items. It is designed to showcase serverless
solutions on Google Cloud Platform, including
[Google App Engine](https://cloud.google.com/appengine/),
[Google Cloud Functions](https://cloud.google.com/functions/),
[Google Cloud Pub/Sub](https://cloud.google.com/pubsub/) and many more.

**Serverless Store is not an official Google product.**

The project features:

* Fully Serverless Architecture

    The Serverless Store demo is built completely on Google-managed
    services, from app deployment to the database backend. It scales
    automatically, requires no server management at all, and costs only when
    you use it.

* Event-Driven Design:

    Many workloads in the Serverless Store demo are triggered by events, such
    as user actions (e.g. submitting an order) and system notifications,
    delivered via Cloud Pub/Sub. This design makes workflow automation easier
    than ever, and enables auto-entry, persistent logging, and many more
    features in the app. 

This project integrates the following Google products/services:

| Category | Product/Service | Description |
|----------|-----------------|-------------|
| Serverless Computing | Google App Engine | App-based fully managed serverless platform |
| Serverless Computing | Google Cloud Functions | Function-based event-driven serverless platform |
| Storage | Google Cloud Firestore | Fully managed serverless NoSQL document database |
| Storage | Google Cloud Storage | Object stroage with global edge-caching |
| App Solution | Google Firebase | Mobile/Web development platform |
| Data Analytics | Google Cloud Pub/Sub | Scalable data/event ingestion service |
| Data Analytics | Google BigQuery | Fully managed scalable data warehouse with built-in machine learning support |
| Data Analytics | Google Data Studio | Data visualization tool |
| AI and Machine Learing | Google Cloud AutoML | Custom machine learning model training service that requires no machine learning expertise |
| AI and Machine Learing | Google Cloud Vision | Pretrained machine learning model for image insights |
| AI and Machine Learing | DialogFlow | Human-computer natural language conversation solution |
| Management Tools | Google Stackdriver Logging | Logging solution for applications everywhere |
| Management Tools | Google Stackdriver Monitoring | Monitoring solution for applications and services |
| Management Tools | Google Stackdriver Tracing | Performance bottleneck discovery tool |
| Management Tools | Google Stackdriver Error Reporting | Error identification and reporting tool |
| Developer Tools | Google Cloud Build | CI/CD solution |
| Smart Home | Google Assistant | AI-powered virtual assistant |
| Business & Collaboration | Google Sheets | Collaborative, extensible online spreadsheets for home and enterprise users. |

## Architecture Overview

![Architecture](/docs/architecture.png)

## Setup

💡 [Serverless on GCP: an Introduction with Serverless Store](https://medium.com/@ratrosy/serverless-on-google-cloud-platform-an-introduction-with-serverless-store-demo-41992dec085) is
a step-by-step guide for setting up this demo.

## Screenshots

![Screenshot](/docs/screenshot.png)

## Conferences featuring Serverless Store

[Google Cloud Global Digital Conference 2019](https://cloudonair.withgoogle.com/events/app-dev).
