"""Fitbit Login Example
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.fitbit import FitbitSSO

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = FitbitSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:3000/auth/callback",
    allow_insecure_http=True,
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
    uvicorn.run(app="examples.fitbit:app", host="127.0.0.1", port=3000)
