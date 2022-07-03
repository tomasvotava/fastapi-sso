"""This is an example usage of fastapi-sso.
"""

import os
from typing import Any, Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from fastapi_sso.sso.base import DiscoveryDocument, OpenID
from fastapi_sso.sso.generic import create_provider

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = FastAPI()

# Try running:
# docker run \
#   -p 9090:9090 \
#   -e PORT=9090 \
#   -e HOST=localhost \
#   -e CLIENT_ID=test \
#   -e CLIENT_SECRET=secret \
#   -e CLIENT_REDIRECT_URI=http://localhost:8080/callback \
#   -e CLIENT_LOGOUT_REDIRECT_URI=http://localhost:8080 \
#   quay.io/appvia/mock-oidc-user-server:v0.0.2
# and then python examples/generic.py


def convert_openid(response: Dict[str, Any]) -> OpenID:
    """Convert user information returned by OIDC"""
    print(response)
    return OpenID(display_name=response["sub"])


discovery_document: DiscoveryDocument = {
    "authorization_endpoint": "http://localhost:9090/auth",
    "token_endpoint": "http://localhost:9090/token",
    "userinfo_endpoint": "http://localhost:9090/me",
}

GenericSSO = create_provider(name="oidc", discovery_document=discovery_document, response_convertor=convert_openid)

sso = GenericSSO(
    client_id="test", client_secret="secret", redirect_uri="http://localhost:8080/callback", allow_insecure_http=True
)


@app.get("/login")
async def sso_login():
    """Generate login url and redirect"""
    return await sso.get_login_redirect()


@app.get("/callback")
async def sso_callback(request: Request):
    """Process login response from OIDC and return user info"""
    user = await sso.verify_and_process(request)
    if user is None:
        raise HTTPException(401, "Failed to fetch user information")
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }


if __name__ == "__main__":
    try:
        uvicorn.run(app="examples.generic:app", host="127.0.0.1", port=8080)
    except KeyboardInterrupt:
        pass
