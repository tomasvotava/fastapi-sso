"""This is an example usage of fastapi-sso."""

from typing import Any, Union
from httpx import AsyncClient
import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from fastapi_sso.sso.base import DiscoveryDocument, OpenID
from fastapi_sso.sso.generic import create_provider

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


def convert_openid(response: dict[str, Any], _client: Union[AsyncClient, None]) -> OpenID:
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
    async with sso:
        return await sso.get_login_redirect()


@app.get("/callback")
async def sso_callback(request: Request):
    """Process login response from OIDC and return user info"""
    async with sso:
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
    uvicorn.run(app="examples.generic:app", host="127.0.0.1", port=8080)
