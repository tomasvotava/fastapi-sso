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

## Soundcloud

```python
"""Soundcloud Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.soundcloud import SoundcloudSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = SoundcloudSSO(
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
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": CLIENT_SECRET})  # <- "client_secret" parameter is needed!
        return user


if __name__ == "__main__":
    uvicorn.run(app="examples.soundcloud:app", host="127.0.0.1", port=5000)

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

## Soundcloud

```python
"""Soundcloud Login Example"""

import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi_sso.sso.soundcloud import SoundcloudSSO

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

app = FastAPI()

sso = SoundcloudSSO(
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
    with sso:
        user = await sso.verify_and_process(request, params={"client_secret": CLIENT_SECRET})  # <- "client_secret" parameter is needed!
        return user


if __name__ == "__main__":
    uvicorn.run(app="examples.soundcloud:app", host="127.0.0.1", port=5000)

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

