# Recommendation Service

The recommendation service provides a simple API to retrieve a list of recommended products
based on recommendations manually configured via a Google Sheet.

## Usage

### Request

The productID querystring parameter expects a list of products using querystring array notation.

```
GET https://[CLOUD_FUNCTION_DOMAIN]/recommend?productId[]=blanket&productId[]=shoe
```

### Response: Success (200 OK)

```
{
  "data": [
    "pillow",
    "socks"
  ]
}
```

### Recommendation Data (Sheet Schema)

The recommendation logic is a simple mapping of products in the request to recommended companion products. Un-validated identifiers can be any string.

| Request Product ID | Recommended Product |
+--------------------+---------------------+
|  `[PRODUCT_ID_1]`  |  `[PRODUCT_ID_5]`   |
|      blanket       |        pillow       |
|    binoculars      |        ⛺           |
|         *          |        socks        |

The asterisk (`*`) under "Request Product ID" is a wildcard mapping. If a product is not otherwise mapped to a recommendation, it will default to the wildcard recommendation.

## Deployment

### Setting Up

* Create a new Google Sheet, note the ID of the sheet and the tab.
* Share the sheet with read-only access to the Cloud Functions service account. For example, `[PROJECT_NAME]@appspot.gserviceaccount.com`. This allows sidestepping most authentication code in the Cloud Function.

### Ship the Code

```
gcloud functions deploy recommendation \
  --runtime=nodejs8 \
  --region=us-central1 \
  --trigger-http \
  --set-env-vars=GOOGLE_SHEET_ID=[GOOGLE_SHEET_ID]
```

### Configuration

* **`GOOGLE_SHEET_ID`**: [required] Unique identifier of the Google Sheet.
* **`GOOGLE_SHEET_TAB_ID`**: [default=`Recommend`] Name of the worksheet tab from which to pull the data.
* **`CACHE_TTL_SECONDS`**: [default=`3`] Length of time the sheet data is cached in the function.
