"""Microsoft Login Example
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.microsoft import MicrosoftSSO

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
TENANT = os.environ["TENANT"]

app = FastAPI()

sso = MicrosoftSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    tenant=TENANT,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
    use_state=False,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    return await sso.verify_and_process(request)


if __name__ == "__main__":
    uvicorn.run(app="examples.microsoft:app", host="127.0.0.1", port=5000)
