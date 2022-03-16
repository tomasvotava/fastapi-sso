# FastAPI Microsoft SSO
<a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white"/></a>
<a href="https://fastapi.tiangolo.com/ko/"><img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"/></a>
## Installation

### Install using `pip`

```console
pip install fastapi-sso

pip install -r requirements.txt

echo "MY_CLIENT_ID=[<b>MY_CLIENT_ID</b>]" >> .env
echo "MY_CLIENT_SECRET=[<b>MY_CLIENT_SECRET</b>]" >> .env
echo "MY_CLIENT_TENANT=[<b>MY_CLIENT_TENANT</b>]" >> .env
echo "REDIRECT_URL=[<b>REDIRECT_URL</b>]" >> .env
```

## Microsoft Example

### `microsoft_example.py`

```python
#This is an example usage of fastapi-microsoft-sso.

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

```

Run using `uvicorn microsoft_example:app`.

## HTTP and development

**You should always use `https` in production**. But in case you need to test on `localhost` and do not want to
use self-signed certificate, make sure you set up redirect uri within your SSO provider to `http://localhost:{port}`
and then add this to your environment:

```bash
OAUTHLIB_INSECURE_TRANSPORT=1
```

And make sure you pass `allow_insecure_http = True` to SSO class' constructor, such as:

```python
google_sso = GoogleSSO("client-id", "client-secret", "callback-url", allow_insecure_http=True)
```

See [this issue](https://github.com/tomasvotava/fastapi-sso/issues/2) for more information.

## State

State is used in OAuth to make sure server is responding to the request we send. It may cause you trouble
as `fastsapi-sso` actually saves the state content as a cookie and attempts reading upon callback and this may
fail (e.g. when loging in from different domain then the callback is landing on). If this is your case,
you may want to disable state checking by passing `use_state = False` in SSO class's constructor, such as:

```python
google_sso = GoogleSSO("client-id", "client-secret", "callback-url", use_state=False)
```

See more on state [here](https://auth0.com/docs/configure/attack-protection/state-parameters).
