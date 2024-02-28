import os
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
import jwt
import json

###
# Webhook payload signature verification
###

# Initialize JWKS client
jwks_client = jwt.PyJWKClient(
    "https://api.slashid.com/organizations/webhooks/verification-jwks",
    headers={"SlashID-OrgID": os.environ["ORG_ID"]}
)

def verify_extract_token(token):
    """
    Verifies JWT token from request data using JWKS from provided endpoint.

    :param token: Incoming request object.
    :return: Decoded token if valid.
    :raises: HTTPException with status 401 if token is invalid.
    """
    try:
        # Get unverified header from JWT
        header = jwt.get_unverified_header(token)

        # Fetch the signing key from JWKS using the 'kid' claim from the JWT header
        key = jwks_client.get_signing_key(header["kid"]).key

        # Decode the JWT using the fetched signing key
        verified_token = jwt.decode(token, key, audience=os.environ["ORG_ID"], algorithms=["ES256"])

        # NOTE: In production make sure to also verify the origin of the request in the future
        # if verified_token['target_url'] != webhookURL: 
        #     raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail=f"Token {token} is invalid: {e}",
        # )

        # Return decoded token
        return verified_token


    except Exception as e:
        # Raise exception if JWT is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token {token} is invalid: {e}",
        )

###
# Webhook endpoint
###

app = FastAPI()

@app.post("/user-auth-hook")
async def hook_function(request: Request):

    request_body = await request.body()

    # Now the request has been validated
    token = verify_extract_token(request_body)

    print(json.dumps(token, indent=4))

    #extract the email address of the user
    handle = token['trigger_content']['authentications'][0]['handle']['value']
    ip_address = token['trigger_content']['request_metadata']['client_ip_address']

    print(f"User handle {handle} and IP address {ip_address}\n")

    if handle == "alex.singh@acme.com":
        in_office = False
        if ip_address == "10.20.30.40":
            in_office = True

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "department": "R&D",
            "name": "Alex Singh",
            "in_office": in_office
        })
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={})