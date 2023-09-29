# How-To Guides

## Installation

### Install using `poetry`

```console
poetry add fastapi-sso
```

### Install using `pip`

```console
pip install fastapi-sso
```

## Specify `redirect_uri` at request time

In scenarios when you cannot provide the `redirect_uri` upon the SSO class initialization, you may simply omit
the parameter and provide it when calling `get_login_redirect` method.

```python
# ... other imports and code ...

google_sso = GoogleSSO("my-client-id", "my-client-secret")

@app.get("/google/login")
async def google_login(request: Request):
    """Dynamically generate login url and return redirect"""
    with google_sso:
        return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"))

@app.get("/google/callback")
async def google_callback(request: Request):
    # ... handle callback ...

```

## Request additional scopes

!!! info "Added in `0.4.0`"

You may specify `scope` when initializing the SSO class.
This is useful when you need to request additional scopes from the user.
The access token returned after verification will contain all the scopes
and you may use it to access the user's data.

```python
# ... other imports and code ...

sso = GoogleSSO(client_id="client-id", client_secret="client-secret", scope=["openid", "email", "https://www.googleapis.com/auth/calendar"])

@app.get("/google/login")
async def google_login():
    with sso:
        return await sso.get_login_redirect(redirect_uri=request.url_for("google_callback"))

@app.get("/google/callback")
async def google_callback(request: Request):
    with sso:
        await sso.verify_and_process(request)
    # you may now use sso.access_token to access user's Google calendar
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers={"Authorization": f"Bearer {sso.access_token}"}
        )
    return response.json()
```

## Additional query parameters

!!! info "Added in `0.4.0`"

You may provide additional query parameters to be sent to the login screen.

E.g. sometimes you want to specify `access_type=offline` or `prompt=consent` in order for Google to return `refresh_token`.

```python
# ... other imports and code ...

@app.get("/google/login")
async def google_login(request: Request):
    with google_sso:
        return await google_sso.get_login_redirect(
            redirect_uri=request.url_for("google_callback"),
            params={"prompt": "consent", "access_type": "offline"}
            )

@app.get("/google/callback")
async def google_callback(request: Request):
    with google_sso:
        user = await google_sso.verify_and_process(request)
    # you may now use google_sso.refresh_token to refresh the access token
```

## HTTP and development

!!! danger "You should always use `https` in production"

In case you need to test on `localhost` and do not want to
use a self-signed certificate, make sure you set up redirect uri within your SSO provider to `http://localhost:{port}`
and then add this to your environment:

```bash
OAUTHLIB_INSECURE_TRANSPORT=1
```

And make sure you pass `allow_insecure_http = True` to SSO class' constructor, such as:

```python
import os
from fastapi_sso.sso.google import GoogleSSO

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

google_sso = GoogleSSO("client-id", "client-secret", allow_insecure_http=True)
```

See [this issue](https://github.com/tomasvotava/fastapi-sso/issues/2) for more information.

## State and return url

State is useful if you want the server to return something back to you to help you understand in what
context the authentication was initiated. It is mostly used to store the url you want your user to be redirected
to after successful login. You may use `.state` property to get the state returned from the server.

Example:

```python

from fastapi import Request
from fastapi.responses import RedirectResponse

google_sso = GoogleSSO("client-id", "client-secret")

# E.g. https://example.com/auth/login?return_url=https://example.com/welcome
async def google_login(return_url: str):
    with google_sso:
        # Send return_url to Google as a state so that Google knows to return it back to us
        return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"), state=return_url)

async def google_callback(request: Request):
    with google_sso:
        user = await google_sso.verify_and_process(request)
        # google_sso.state now holds your return_url (https://example.com/welcome)
        return RedirectResponse(google_sso.state)
```
