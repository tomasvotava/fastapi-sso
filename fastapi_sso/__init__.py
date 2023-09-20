"""FastAPI plugin to enable SSO to most common providers
(such as Facebook login, Google login and login via Microsoft Office 365 account)

## Example

#### `example.py`

```python
\"""This is an example usage of fastapi-sso.
\"""

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO

app = FastAPI()

google_sso = GoogleSSO("my-client-id", "my-client-secret", "https://my.awesome-web.com/google/callback")


@app.get("/google/login")
async def google_login():
    \"""Generate login url and redirect\"""
    return await google_sso.get_login_redirect()


@app.get("/google/callback")
async def google_callback(request: Request):
    \"""Process login response from Google and return user info\"""
    user = await google_sso.verify_and_process(request)
    if user is None:
        raise HTTPException(401, "Failed to fetch user information")
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }

```
"""

from .sso.base import OpenID, SSOBase, SSOLoginError
from .sso.facebook import FacebookSSO
from .sso.fitbit import FitbitSSO
from .sso.generic import create_provider
from .sso.github import GithubSSO
from .sso.gitlab import GitlabSSO
from .sso.google import GoogleSSO
from .sso.kakao import KakaoSSO
from .sso.microsoft import MicrosoftSSO
from .sso.naver import NaverSSO
from .sso.spotify import SpotifySSO
