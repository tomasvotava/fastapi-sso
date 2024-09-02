# State and return url

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
    async with google_sso:
        # Send return_url to Google as a state so that Google knows to return it back to us
        return await google_sso.get_login_redirect(redirect_uri=request.url_for("google_callback"), state=return_url)

async def google_callback(request: Request):
    async with google_sso:
        user = await google_sso.verify_and_process(request)
        # google_sso.state now holds your return_url (https://example.com/welcome)
        return RedirectResponse(google_sso.state)
```
