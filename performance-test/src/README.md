# K6 tests for _Anonymizer_ project

[k6](https://k6.io/) is a load testing tool. 👀 See [here](https://k6.io/docs/get-started/installation/) to install it.

  - [01. Anonymizer](#01-anonymizer)

This is a set of [k6](https://k6.io) tests related to the _Anonymizer_ initiative.

To invoke k6 test passing parameter use -e (or --env) flag:

```
-e MY_VARIABLE=MY_VALUE
```

## 01. Anonymizer

Call to test the Anonymizer:

```
k6 run --env VARS=local.environment.json --env TEST_TYPE=./test-types/load.json --env SUBSCRIPTION_KEY=<your-subscription-key>
```

where the mean of the environment variables is:

```json
{
  "environment": [
    {
      "env": "dev",
      "anonymizeUri": "https://api.dev.platform.pagopa.it/shared/anonymizer/v1/anonymize"
    }
  ]
}  
```

`anonymizeUri`: Anonymizer url to access the Anonymizer REST API