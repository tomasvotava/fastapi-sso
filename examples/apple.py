"""Apple Login Example.

Setup:
- `CLIENT_ID`: Apple Services ID identifier for Sign in with Apple (web).
- `CLIENT_SECRET`: Apple client secret JWT (ES256) for that Services ID.
- `REDIRECT_URI`: Callback URL registered in Apple Developer, e.g. `https://<public-host>/auth/callback`.

Notes:
- Apple web callbacks must be public HTTPS. For local testing, use a tunnel (for example ngrok).
- Register the tunnel domain in "Domains and Subdomains" and the exact callback in "Return URLs".

Run:
    $CLIENT_ID = "<services-id>"
    $CLIENT_SECRET = "<apple-client-secret-jwt>"
    $REDIRECT_URI = "https://<public-host>/auth/callback"
    python examples/apple.py
"""

import os

import uvicorn
from fastapi import FastAPI, Request

from fastapi_sso.sso.apple import AppleSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("REDIRECT_URI")

app = FastAPI()

sso = AppleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect."""
    async with sso:
        return await sso.get_login_redirect()


@app.api_route("/auth/callback", methods=["GET", "POST"])
async def auth_callback(request: Request):
    """Verify login."""
    async with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.apple:app", host="127.0.0.1", port=5000)
