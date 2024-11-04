"""Github Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.gitlab import GitlabSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
BASE_ENDPOINT_URL = os.environ.get("GITLAB_ENDPOINT_URL", "https://gitlab.com")

app = FastAPI()

sso = GitlabSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    base_endpoint_url=BASE_ENDPOINT_URL,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
        return user


if __name__ == "__main__":
    uvicorn.run(app="examples.gitlab:app", host="127.0.0.1", port=5000)
