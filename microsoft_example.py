"""This is an example usage of fastapi-sso.
"""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.requests import Request

from fastapi_sso.sso.microsoft import MicrosoftSSO

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

load_dotenv(verbose=True)
app = FastAPI()

microsoft_sso = MicrosoftSSO(
    client_id=os.getenv("MY_CLIENT_ID"),
    client_secret=os.getenv("MY_CLIENT_SECRET"),
    client_tenant=os.getenv("MY_CLIENT_TENANT"),
    redirect_uri=os.getenv("REDIRECT_URL"),
    allow_insecure_http=True,
    use_state=False,
)


@app.get("/microsoft/login")
async def microsoft_login():
    """Generate login url and redirect"""
    return await microsoft_sso.get_login_redirect()


@app.get("/microsoft/callback")
async def microsoft_callback(request: Request):
    """Process login response from Microsoft and return user info"""
    user = await microsoft_sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="microsoft_example:app", host="0.0.0.0", port=8000, reload=True)
