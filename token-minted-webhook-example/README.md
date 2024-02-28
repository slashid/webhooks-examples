# Example

This example sets up a local webhook for hooking authentication attempts synchronously.

## Prerequisites

 - Python 3.6+
 - ngrok with an account: https://ngrok.com/download 
 - FastAPI, UVicorn, PyJWT: `pip install -r requirements.txt`

## Org parameters

You can retrieve the organization key and api key from the [SlashID dashboard](https://console.slashid.dev/).

## Running

### Serve webhook locally
 - `ngrok http 8001`: create local tunnel; please take note of the ngrok-provided URL in ngrok's output, you'll need to set it as the webhook's base `target_url`
 - `ORG_ID=[/id Org ID] API_KEY=[/id API key] uvicorn webhook:app --port 8001 --reload`: serve the webhook locally

> NOTE: Make sure that the port is not used by any other service

### Setup webhook in /id
 - Define the webhook:
    ```
    curl -L -X POST 'https://api.slashid.com/organizations/webhooks' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -H 'SlashID-OrgID: <SlashID Org ID>' \
    -H 'SlashID-API-Key: <SlashID API key>' \
    --data-raw '{"name": "Pre-auth user check", "target_url": "<ngrok's target URL>/user-auth-hook", "timeout": "10s"}'
    ```
    Please take note of the `id` of the newly-created webhook in the response, you'll need it next to attach a trigger to it.

 - Define a `sync_hook` trigger for the newly-created webhook:
    ```
    curl -L -X POST 'https://api.slashid.com/organizations/webhooks/<Webhook ID from previous step>/triggers' \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -H 'SlashID-OrgID: d9d06869-b2ad-321f-1a8a-1c0ce27fd6e8' \
    -H 'SlashID-API-Key: M8S70wB05-MaXY7pM6FHVsVwf0TB' \
    --data-raw '{"trigger_type": "sync_hook", "trigger_name": "token_minted"}'
    ```
    On success the output is empty (`{}`). At this point every time a user attempts to authenticate your webhook will be called first.

### Running 
If everything is setup correctly when a user logs in for that organization the server will print something along these lines: 

```
INFO:     Application startup complete.
{'aud': 'e2c8a069-7e89-cc7e-b161-3f02681c6804', 'exp': 1697652845, 'iat': 1697652545, 'iss': 'https://api.slashid.com', 'jti': '2479ec0e-aad5-47ca-a12b-214ddaf7fc85', 'sub': '065301f4-1c74-7636-ad00-da1923dc00f9', 'target_url': 'https://7b9c-206-71-251-221.ngrok.io/pre-auth-user-check', 'trigger_content': {'aud': 'e2c8a069-7e89-cc7e-b161-3f02681c6804', 'authentications': [{'handle': {'type': 'email_address', 'value': 'vincenzo@slashid.dev'}, 'method': 'oidc', 'timestamp': '2023-10-18T18:08:57.9002598Z'}], 'first_token': True, 'groups_claim_name': 'groups', 'iss': 'https://api.slashid.com', 'region': 'europe-belgium', 'request_metadata': {'client_ip_address': '206.71.251.221', 'origin': 'http://localhost:8080', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}, 'sub': '065158a6-33f2-725e-a208-9d773600513a'}, 'trigger_name': 'token_minted', 'trigger_type': 'sync_hook', 'webhook_id': '065301dd-b26d-7d7e-b500-6a7f180b2cdb'}
INFO:     35.193.131.141:0 - "POST /pre-auth-user-check HTTP/1.1" 200 OK

```