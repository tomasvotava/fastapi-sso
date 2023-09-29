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
    with google_sso:
        return await google_sso.get_login_redirect()

@app.get("/google/callback")
async def google_callback(request: Request):
    with google_sso:
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
