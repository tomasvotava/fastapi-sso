
===== FILE: docs/contributing.md =====

# Contributing

In order to add a new login provider, please make sure to adhere to the following guidelines to the best
of your abilities and possibilities.

## Dependencies management

Seeing the file `poetry.lock` you may have guessed this project relies on [Poetry](https://python-poetry.org/)
to manage dependencies.

If there is a need for a 3rd party dependency in order to integrate login provider, please try to make
use of [extras](https://python-poetry.org/docs/pyproject/#extras) in order not to make `fastapi-sso`
any heavier. Any dependency apart from the ones listed in `tool.poetry.dependencies` in
[`pyproject.toml`](https://github.com/tomasvotava/fastapi-sso/tree/master/pyproject.toml)
should be an extra along with it being optional. If you are not shure how to do this, let me know
the dependency in PR and I will add it before merging your code.

Also, **please strictly separate runtime dependencies from dev dependencies**.

## Provide examples

Please, try to provide examples for the login provider in the
[`examples/`](https://github.com/tomasvotava/fastapi-sso/tree/master/examples) directory.
**Always make sure your code contains no credentials before submitting the PR**.

## Code quality

I am myself rather a dirty programmer and so it feels a little out of place for me to talk about
code quality, but let's keep the code up to at least some standards.

### Formatting

As visible in `pyproject.toml`, I use `black` as a formatter with all the default settings except for
the `line_length` parameter. As seen in the file, I set it to 120 characters. Please try to keep
the code formatted this way.

It is easy to reformat the code by calling `black` from the repository root:

```console
$ poe black

All done! ✨ 🍰 ✨
13 files left unchanged.
```

### Linting

I use `ruff`. Detailed configuration is to be found in `pyproject.toml` file.

Check your code by calling:

```console
$ poe ruff

Poe => ruff check fastapi_sso
All checks passed!
```

If your code doesn't pass and you feel you have a good reason for it not to be, you may use
`noqa: ...` magic comments throughout the code, but please expect me to ask about it
when you submit the PR.

### Typechecking

Try to keep the code statically typechecked using `mypy`. Check that everything is alright by running:

```console
$ poe mypy

Success: no issues found in 13 source files
```

### Pre-commit

I use `pre-commit` to run all the above checks before committing. You can install it by calling:

```console
$ poe pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

### Tests

I use `pytest` for testing. Please try to provide tests for your code. If you are not sure how to
do it, let me know in the PR and I'll try to help you.

Run the tests by calling:

```console
poe test
```

## Documentation

Please try to provide documentation for your code. I use `mkdocs` to generate the documentation.
In most cases, it should be enough to use docstrings and to provide
examples in the aforementioned `examples/` directory.

===== FILE: docs/examples.md =====

# Examples

## Bitbucket

```python
"""BitBucket Login Example
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.bitbucket import BitbucketSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = BitbucketSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.bitbucket:app", host="127.0.0.1", port=5000)

```

## Discord

```python
"""Discord Login Example
"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.discord import DiscordSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = DiscordSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.discord:app", host="127.0.0.1", port=5000)

```

## Facebook

```python
"""Facebook Login Example"""

import os

import uvicorn
from fastapi import FastAPI, Request

from fastapi_sso.sso.facebook import FacebookSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = FacebookSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.facebook:app", host="127.0.0.1", port=5000)

```

## Fitbit

```python
"""Fitbit Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.fitbit import FitbitSSO

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
    async with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        return await sso.verify_and_process(request)


if __name__ == "__main__":
    uvicorn.run(app="examples.fitbit:app", host="127.0.0.1", port=3000)

```

## Generic

```python
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

```

## Github

```python
"""Github Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.github import GithubSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = GithubSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
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
    uvicorn.run(app="examples.github:app", host="127.0.0.1", port=5000)

```

## Gitlab

```python
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

```

## Google

```python
"""Google Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.google import GoogleSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.google:app", host="127.0.0.1", port=5000)

```

## Kakao

```python
"""Kakao Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.kakao import KakaoSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = KakaoSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
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
        return await sso.verify_and_process(request, params={"client_secret": CLIENT_SECRET})


if __name__ == "__main__":
    uvicorn.run(app="examples.kakao:app", host="127.0.0.1", port=5000, reload=True)

```

## Line

```python
"""Line Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.line import LineSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = LineSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect(state="randomstate")


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.line:app", host="127.0.0.1", port=5000)

```

## Linkedin

```python
"""Github Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.linkedin import LinkedInSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = LinkedInSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5050/auth/callback",
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
    uvicorn.run(app="examples.linkedin:app", host="127.0.0.1", port=5050)

```

## Microsoft

```python
"""Microsoft Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.microsoft import MicrosoftSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
TENANT = os.environ["TENANT"]

app = FastAPI()

sso = MicrosoftSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    tenant=TENANT,
    redirect_uri="http://localhost:8080/auth/callback",
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
        return await sso.verify_and_process(request)


if __name__ == "__main__":
    uvicorn.run(app="examples.microsoft:app", host="127.0.0.1", port=8080)

```

## Naver

```python
"""Naver Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.naver import NaverSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = NaverSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://127.0.0.1:5000/auth/callback",
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
        return await sso.verify_and_process(request, params={"client_secret": CLIENT_SECRET})


if __name__ == "__main__":
    uvicorn.run(app="examples.naver:app", host="127.0.0.1", port=5000, reload=True)

```

## Notion

```python
"""Github Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.notion import NotionSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = NotionSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:3000/oauth2/callback",
    allow_insecure_http=True,
)


@app.get("/oauth2/login")
async def auth_init():
    """Initialize auth and redirect"""
    async with sso:
        return await sso.get_login_redirect()


@app.get("/oauth2/callback")
async def auth_callback(request: Request):
    """Verify login"""
    async with sso:
        user = await sso.verify_and_process(request)
        return user


if __name__ == "__main__":
    uvicorn.run(app="examples.notion:app", host="127.0.0.1", port=3000)

```

## Seznam

```python
"""Seznam Login Example"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi import Request

from fastapi_sso.sso.seznam import SeznamSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = SeznamSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:5000/auth/callback",
    allow_insecure_http=True,
)


@app.get("/auth/login")
async def auth_init():
    """Initialize auth and redirect"""
    with sso:
        return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verify login"""
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": CLIENT_SECRET})  # <- "client_secret" parameter is needed!
    return user


if __name__ == "__main__":
    uvicorn.run(app="examples.seznam:app", host="127.0.0.1", port=5000)

```

## Twitter

```python
"""Twitter (X) Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.twitter import TwitterSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = TwitterSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://127.0.0.1:5000/auth/callback",
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
    uvicorn.run(app="examples.twitter:app", host="127.0.0.1", port=5000)

```

## Yandex

```python
"""Yandex Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.yandex import YandexSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = YandexSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
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
    uvicorn.run(app="examples.yandex:app", host="127.0.0.1", port=5000)

```


===== FILE: docs/how-to-guides/00-installation.md =====

# Installation

## Install using `poetry`

```console
poetry add fastapi-sso
```

## Install using `pip`

```console
pip install fastapi-sso
```

===== FILE: docs/how-to-guides/additional-query-params.md =====

# Additional query parameters

!!! info "Added in `0.4.0`"

You may provide additional query parameters to be sent to the login screen.

E.g. sometimes you want to specify `access_type=offline` or `prompt=consent` in order for Google to return `refresh_token`.

```python
# ... other imports and code ...

@app.get("/google/login")
async def google_login(request: Request):
    async with google_sso:
        return await google_sso.get_login_redirect(
            redirect_uri=request.url_for("google_callback"),
            params={"prompt": "consent", "access_type": "offline"}
            )

@app.get("/google/callback")
async def google_callback(request: Request):
    async with google_sso:
        user = await google_sso.verify_and_process(request)
    # you may now use google_sso.refresh_token to refresh the access token
```

===== FILE: docs/how-to-guides/additional-scopes.md =====

# Request additional scopes

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
    async with sso:
        return await sso.get_login_redirect(redirect_uri=request.url_for("google_callback"))

@app.get("/google/callback")
async def google_callback(request: Request):
    async with sso:
        await sso.verify_and_process(request)
    # you may now use sso.access_token to access user's Google calendar
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList",
            headers={"Authorization": f"Bearer {sso.access_token}"}
        )
    return response.json()
```

===== FILE: docs/how-to-guides/http-development.md =====

# HTTP and development

!!! danger "You should always use `https` in production"

In case you need to test on `localhost` and do not want to
use a self-signed certificate, make sure you set up redirect uri within your SSO provider to `http://localhost:{port}`
and then add this to your environment:

!!! info "Since `0.9.0` OAUTHLIB_INSECURE_TRANSPORT is set to `1` automatically if `allow_insecure_http` is `True` and this is not needed anymore."

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

===== FILE: docs/how-to-guides/key-error.md =====

# `KeyError` and missing keys in response

As seen in quite a lot of issues ([#81](https://github.com/tomasvotava/fastapi-sso/issues/81),
[#54](https://github.com/tomasvotava/fastapi-sso/issues/54),
[#51](https://github.com/tomasvotava/fastapi-sso/issues/51),
[#32](https://github.com/tomasvotava/fastapi-sso/issues/32)), some SSO providers misbehave and either
change the response from time to time or return incomplete data.

In some cases this may be overcome by using the `scope` parameter to request additional scopes
([see how to do it](./additional-scopes.md)).

For example, if you are using Microsoft SSO within your organization, you may require the `User.Read.All` scope
or `email` scope to get the user's email address.

!!! info "`email` was added in `0.8.0` as the default scope for Microsoft SSO."

===== FILE: docs/how-to-guides/redirect-uri-request-time.md =====

# Specify `redirect_uri` at request time

In scenarios when you cannot provide the `redirect_uri` upon the SSO class initialization, you may simply omit
the parameter and provide it when calling `get_login_redirect` method.

```python
# ... other imports and code ...

google_sso = GoogleSSO("my-client-id", "my-client-secret")

@app.get("/google/login")
async def google_login(request: Request):
    """Dynamically generate login url and return redirect"""
    async with google_sso:
        return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"))

@app.get("/google/callback")
async def google_callback(request: Request):
    # ... handle callback ...

```

===== FILE: docs/how-to-guides/state-return-url.md =====

# State and return url

!!! warning "About `state`"
    The `state` parameter is a **security mechanism**, not a generic data transport.

    Its primary purpose is to protect against CSRF attacks by allowing the client to
    verify that the authorization response belongs to an authentication request it
    previously initiated. To achieve this securely, the `state` value **must** be
    cryptographically random, stored server-side, and verified when the provider
    redirects the user back.

    If you do **not** pass a `state` explicitly, `fastapi-sso` will generate, store,
    and validate a secure random state for you.

    Using `state` to carry arbitrary user-controlled data (such as return URLs)
    **without validation** is unsafe and can lead to critical vulnerabilities
    (see [#266](https://github.com/tomasvotava/fastapi-sso/issues/266)).

    If you need to preserve contextual data across the login flow (e.g. a return URL),
    the recommended solution is to store that data in a server-side session and use
    `state` **only** for request verification.

    The example below demonstrates a commonly seen pattern, but it is **not
    recommended** and is shown only for completeness and compatibility with existing
    implementations.

State is useful if you want the server to return something back to you to help you understand in what
context the authentication was initiated. It is mostly used to store the url you want your user to be redirected
to after successful login. You may use `.state` property to get the state returned from the server or access
it from the `state` parameter in the callback function.

Example:

```python

from fastapi import Request
from fastapi.responses import RedirectResponse

google_sso = GoogleSSO("client-id", "client-secret")

# E.g. https://example.com/auth/login?return_url=https://example.com/welcome
async def google_login(return_url: str):
    async with google_sso:
        # Send return_url to Google as a state so that Google knows to return it back to us
        return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"), state=return_url)

async def google_callback(request: Request, state: str | None = None):
    async with google_sso:
        user = await google_sso.verify_and_process(request)
        if state is not None:
            return RedirectResponse(state)
        else:
            return user
```

===== FILE: docs/how-to-guides/use-with-fastapi-security.md =====

# Using with fastapi's Security

Even though `fastapi-sso` does not try to solve login and authentication, it is clear that you
will probably mostly use it to protect your endpoints. This is why it is important to know how
to use it with fastapi's security.

You were asking how to put the lock 🔒 icon to your Swagger docs
in [this issue](https://github.com/tomasvotava/fastapi-sso/issues/33). This is how you do it.

## Requirements

- `fastapi` - obviously
- `fastapi-sso` - duh
- `python-jose[cryptography]` - to sign and verify our JWTs

## Explanation

Fastapi-SSO is here to arrange the communication between your app and the login provider (such as Google).
It does not store any state of this communication and so it is up to you to make sure you don't have to
ask the user to login again and again.

There are millions of ways how to do this, but the most common one is to use JWTs. You can read more about
them [here](https://jwt.io/introduction/). In short, JWT is a token that contains some data and is signed
by a secret key. This means that you can verify that the token was created by you and that the data inside
the token was not changed.

This makes JWTs very helpful, because it's the thing that comes from the user that you can actually trust.

In this example, we will save the JWT into a cookie so that the user sends it with every request. We will
also use fastapi's `Depends` to make sure that the user is authenticated before accessing the endpoint.

## Example

```python
import datetime  # to calculate expiration of the JWT
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyCookie  # this is the part that puts the lock icon to the docs
from fastapi_sso.sso.google import GoogleSSO  # pip install fastapi-sso
from fastapi_sso.sso.base import OpenID

from jose import jwt  # pip install python-jose[cryptography]

SECRET_KEY = "this-is-very-secret"  # used to sign JWTs, make sure it is really secret
CLIENT_ID = "your-client-id"  # your Google OAuth2 client ID
CLIENT_SECRET = "your-client-secret"  # your Google OAuth2 client secret

sso = GoogleSSO(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri="http://127.0.0.1:5000/auth/callback")

app = FastAPI()


async def get_logged_user(cookie: str = Security(APIKeyCookie(name="token"))) -> OpenID:
    """Get user's JWT stored in cookie 'token', parse it and return the user's OpenID."""
    try:
        claims = jwt.decode(cookie, key=SECRET_KEY, algorithms=["HS256"])
        return OpenID(**claims["pld"])
    except Exception as error:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from error


@app.get("/protected")
async def protected_endpoint(user: OpenID = Depends(get_logged_user)):
    """This endpoint will say hello to the logged user.
    If the user is not logged, it will return a 401 error from `get_logged_user`."""
    return {
        "message": f"You are very welcome, {user.email}!",
    }


@app.get("/auth/login")
async def login():
    """Redirect the user to the Google login page."""
    async with sso:
        return await sso.get_login_redirect()


@app.get("/auth/logout")
async def logout():
    """Forget the user's session."""
    response = RedirectResponse(url="/protected")
    response.delete_cookie(key="token")
    return response


@app.get("/auth/callback")
async def login_callback(request: Request):
    """Process login and redirect the user to the protected endpoint."""
    async with sso:
        openid = await sso.verify_and_process(request)
        if not openid:
            raise HTTPException(status_code=401, detail="Authentication failed")
    # Create a JWT with the user's OpenID
    expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
    token = jwt.encode({"pld": openid.dict(), "exp": expiration, "sub": openid.id}, key=SECRET_KEY, algorithm="HS256")
    response = RedirectResponse(url="/protected")
    response.set_cookie(
        key="token", value=token, expires=expiration
    )  # This cookie will make sure /protected knows the user
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
```

## Result

### Docs now show the lock icon

Visit [`http://127.0.0.1:5000/docs/`](http://127.0.0.1:5000/docs/)

![Swagger docs with lock icon](./fastapi-security.png)

### Accessing the `/protected` endpoint before login

Try visiting [`http://127.0.0.1:5000/protected`](http://127.0.0.1:5000/protected). You will get a 401 error.

```json
{
    "detail": "Not authenticated"
}
```

### Accessing the `/protected` endpoint after login

First visit [`http://127.0.0.1:5000/auth/login`](http://127.0.0.1:5000/auth/login) to login with Google.
Then visit [`http://127.0.0.1:5000/protected`](http://127.0.0.1:5000/protected).

```json
{
    "message": "You are very welcome, ijustfarted@example.com"
}
```

If you want to retry everything, either delete the cookie from your browser or visit
[`http://127.0.0.1:5000/auth/logout`](http://127.0.0.1:5000/auth/logout).

===== FILE: docs/index.md =====

{!../README.md!}

===== FILE: docs/reference/__init__.md =====

::: fastapi_sso

===== FILE: docs/reference/pkce.md =====

::: fastapi_sso.pkce

===== FILE: docs/reference/sso.base.md =====

::: fastapi_sso.sso.base

===== FILE: docs/reference/sso.bitbucket.md =====

::: fastapi_sso.sso.bitbucket

===== FILE: docs/reference/sso.discord.md =====

::: fastapi_sso.sso.discord

===== FILE: docs/reference/sso.facebook.md =====

::: fastapi_sso.sso.facebook

===== FILE: docs/reference/sso.fitbit.md =====

::: fastapi_sso.sso.fitbit

===== FILE: docs/reference/sso.generic.md =====

::: fastapi_sso.sso.generic

===== FILE: docs/reference/sso.github.md =====

::: fastapi_sso.sso.github

===== FILE: docs/reference/sso.gitlab.md =====

::: fastapi_sso.sso.gitlab

===== FILE: docs/reference/sso.google.md =====

::: fastapi_sso.sso.google

===== FILE: docs/reference/sso.__init__.md =====

::: fastapi_sso.sso

===== FILE: docs/reference/sso.kakao.md =====

::: fastapi_sso.sso.kakao

===== FILE: docs/reference/sso.line.md =====

::: fastapi_sso.sso.line

===== FILE: docs/reference/sso.linkedin.md =====

::: fastapi_sso.sso.linkedin

===== FILE: docs/reference/sso.microsoft.md =====

::: fastapi_sso.sso.microsoft

===== FILE: docs/reference/sso.naver.md =====

::: fastapi_sso.sso.naver

===== FILE: docs/reference/sso.notion.md =====

::: fastapi_sso.sso.notion

===== FILE: docs/reference/sso.seznam.md =====

::: fastapi_sso.sso.seznam

===== FILE: docs/reference/sso.spotify.md =====

::: fastapi_sso.sso.spotify

===== FILE: docs/reference/sso.twitter.md =====

::: fastapi_sso.sso.twitter

===== FILE: docs/reference/sso.yandex.md =====

::: fastapi_sso.sso.yandex

===== FILE: docs/reference/state.md =====

::: fastapi_sso.state

===== FILE: docs/tutorials.md =====

# Tutorials

## A minimal example

In order to make the following code work, you need to create a Google
OAuth2 client and set up the redirect URI to `http://localhost:3000/google/callback`.

Visit [Google Cloud Platform Console Credentials page](https://console.cloud.google.com/apis/credentials),
create a project, if you don't have one already, and create a new OAuth2 client.

Fill in the `Authorized redirect URIs` field with `http://localhost:3000/google/callback`.

Then, copy the `Client ID` and `Client secret` and paste them into the following code:

```python
from fastapi import FastAPI
from starlette.requests import Request
from fastapi_sso.sso.google import GoogleSSO

app = FastAPI()

CLIENT_ID = "your-google-client-id"  # <-- paste your client id here
CLIENT_SECRET = "your-google-client-secret" # <-- paste your client secret here

google_sso = GoogleSSO(CLIENT_ID, CLIENT_SECRET, "http://localhost:3000/google/callback")

@app.get("/google/login")
async def google_login():
    async with google_sso:
        return await google_sso.get_login_redirect()

@app.get("/google/callback")
async def google_callback(request: Request):
    async with google_sso:
        user = await google_sso.verify_and_process(request)
    return user
```

Save the file as `example.py` and run it using `uvicorn example:app`.

Now, visit [http://localhost:3000/google/login](http://localhost:3000/google/login).

!!! note "Does it work?"
    You should be redirected to Google login page. After successful login, you should be redirected back to
    `http://localhost:3000/google/callback` and see a JSON response containing your user data.

## Using SSO as a dependency

You may use SSO as a dependency in your FastAPI application.
This is useful if you want to use the same SSO instance in multiple endpoints and make sure the state is cleared after
the request is processed. You may even omit the `with` statement in this case.

```python
from fastapi import Depends, FastAPI, Request
from fastapi_sso.sso.google import GoogleSSO

app = FastAPI()

CLIENT_ID = "your-google-client-id"  # <-- paste your client id here
CLIENT_SECRET = "your-google-client-secret" # <-- paste your client secret here

def get_google_sso() -> GoogleSSO:
    return GoogleSSO(CLIENT_ID, CLIENT_SECRET, redirect_uri="http://localhost:3000/google/callback")

@app.get("/google/login")
async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
    return await google_sso.get_login_redirect()

@app.get("/google/callback")
async def google_callback(request: Request, google_sso: GoogleSSO = Depends(get_google_sso)):
    user = await google_sso.verify_and_process(request)
    return user
```
