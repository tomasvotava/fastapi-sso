# FastAPI SSO

![Supported Python Versions](https://img.shields.io/pypi/pyversions/fastapi-sso)
![Test Coverage](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgist.githubusercontent.com%2Ftomasvotava%2F328acf6207500c2e836b1c68b5c910f7%2Fraw%2Fe0d04f38af03ec982a695b2438b37e22013edf8d%2Fcoverage.json&query=total&suffix=%25&logo=pytest&label=coverage&color=blue
)
![Tests Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/test.yml?label=tests)
![Pylint Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=pylint)
![Mypy Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=mypy)
![Black Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=black)
![CodeQL Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/codeql-analysis.yml?label=CodeQL)
![PyPi weekly downloads](https://img.shields.io/pypi/dw/fastapi-sso)
![Project License](https://img.shields.io/github/license/tomasvotava/fastapi-sso)
![PyPi Version](https://img.shields.io/pypi/v/fastapi-sso)

FastAPI plugin to enable SSO to most common providers (such as Facebook login, Google login and login via Microsoft Office 365 account).

This allows you to implement the famous `Login with Google/Facebook/Microsoft` buttons functionality on your backend very easily.

## Security warning

Please note that versions preceding `0.7.0` had a security vulnerability.
The SSO instance could share state between requests, which could lead to security issues. **Please update to `0.7.0` or newer**.

Also, the preferred way of using the SSO instances is to use `with` statement, which will ensure the state is cleared.
See example below.

## Support this project

If you'd like to support this project, consider [buying me a coffee ☕](https://www.buymeacoffee.com/tomas.votava).
I tend to process Pull Requests faster when properly caffeinated 😉.

<a href="https://www.buymeacoffee.com/tomas.votava" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Supported login providers

### Official

- Google
- Microsoft
- Facebook
- Spotify
- Fitbit
- Github (credits to [Brandl](https://github.com/Brandl) for hint using `accept` header)
- generic (see [docs](https://tomasvotava.github.io/fastapi-sso/sso/generic.html))

### Contributed

- Kakao (by Jae-Baek Song - [thdwoqor](https://github.com/thdwoqor))
- Naver (by 1tang2bang92) - [1tang2bang92](https://github.com/1tang2bang92)
- Gitlab (by Alessandro Pischedda) - [Cereal84](https://github.com/Cereal84)

See [Contributing](#contributing) for a guide on how to contribute your own login provider.

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
    with google_sso:
        return await google_sso.get_login_redirect()


@app.get("/google/callback")
async def google_callback(request: Request):
    """Process login response from Google and return user info"""
    with google_sso:
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
async def google_login(request: Request):
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

State is useful if you want the server to return something back to you to help you understand in what
context the authentication was initiated. It is mostly used to store the url you want your user to be redirected
to after successful login. You may use `.state` property to get the state returned from the server.

Example:

```python
from fastapi import Request
from fastapi.responses import RedirectResponse

# E.g. https://example.com/auth/login?return_url=https://example.com/welcome
async def google_login(return_url: str):
    google_sso = GoogleSOO("client-id", "client-secret")
    # Send return_url to Google as a state so that Google knows to return it back to us
    return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"), state=return_url)

async def google_callback(request: Request):
    google_sso = GoogleSOO("client-id", "client-secret")
    user = await google_sso.verify_and_process(request)
    # google_sso.state now holds your return_url (https://example.com/welcome)
    return RedirectResponse(google_sso.state)

```

**Deprecation Warning**: legacy `use_state` argument in `SSOBase` constructor is deprecated and will be removed.

## Contributing

If you'd like to contribute and add your specific login provider, please see [CONTRIBUTING.md](CONTRIBUTING.md) file.
