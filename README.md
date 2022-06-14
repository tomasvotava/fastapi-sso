# FastAPI SSO

FastAPI plugin to enable SSO to most common providers (such as Facebook login, Google login and login via Microsoft Office 365 account).

This allows you to implement the famous `Login with Google/Facebook/Microsoft` buttons functionality on your backend very easily.

## Installation

### Install using `pip`

```console
pip install fastapi-sso
```

### Install using `poetry`

```console
poetry add fastapi-sso
```

## Example

For more examples, see [`examples`](/examples/) directory.

### `example.py`

```python
"""This is an example usage of fastapi-sso.
"""

from fastapi import FastAPI
from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO

app = FastAPI()

google_sso = GoogleSSO("my-client-id", "my-client-secret", "https://my.awesome-web.com/google/callback")

@app.get("/google/login")
async def google_login():
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()


@app.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    user = await google_sso.verify_and_process(request)
    return {
        "id": user.id,
        "picture": user.picture,
        "display_name": user.display_name,
        "email": user.email,
        "provider": user.provider,
    }
```

Run using `uvicorn example:app`.

### Specify `redirect_uri` on request time

In scenarios you cannot provide the `redirect_uri` upon the SSO class initialization, you may simply omit
the parameter and provide it when calling `get_login_redirect` method.

```python
...

google_sso = GoogleSSO("my-client-id", "my-client-secret")

@app.get("/google/login")
async def google_login(request: Request):
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"))

@app.get("/google/callback")
async def google_callback(request: Request):
    ...
```

### Specify scope

Since `0.4.0` you may specify `scope` when initializing the SSO class.

```python
from fastapi_sso.sso.microsoft import MicrosoftSSO

sso = MicrosoftSSO(client_id="client-id", client_secret="client-secret", scope=["openid", "email"])
```

### Additional query parameters

Since `0.4.0` you may provide additional query parameters to be
sent to the login screen.

E.g. sometimes you want to specify `access_type=offline` or `prompt=consent` in order for
Google to return `refresh_token`.

```python
async def google_login():
    return await google_sso.get_login_redirect(
        redirect_uri=request.url_for("google_callback"),
        params={"prompt": "consent", "access_type": "offline"}
        )

```

## HTTP and development

**You should always use `https` in production**. But in case you need to test on `localhost` and do not want to
use self-signed certificate, make sure you set up redirect uri within your SSO provider to `http://localhost:{port}`
and then add this to your environment:

```bash
OAUTHLIB_INSECURE_TRANSPORT=1
```

And make sure you pass `allow_insecure_http = True` to SSO class' constructor, such as:

```python
google_sso = GoogleSSO("client-id", "client-secret", allow_insecure_http=True)
```

See [this issue](https://github.com/tomasvotava/fastapi-sso/issues/2) for more information.

## State

State is used in OAuth to make sure server is responding to the request we send. It may cause you trouble
as `fastsapi-sso` actually saves the state content as a cookie and attempts reading upon callback and this may
fail (e.g. when loging in from different domain then the callback is landing on). If this is your case,
you may want to disable state checking by passing `use_state = False` in SSO class's constructor, such as:

```python
google_sso = GoogleSSO("client-id", "client-secret", use_state=False)
```

See more on state [here](https://auth0.com/docs/configure/attack-protection/state-parameters).

## Supported login providers

### Official

- Google
- Microsoft
- Facebook
- Spotify

### Contributed

- Kakao (by Jae-Baek Song - [thdwoqor](https://github.com/thdwoqor))

## Contributing

If you'd like to contribute and add your specific login provider, please see [CONTRIBUTING.md](CONTRIBUTING.md) file.
