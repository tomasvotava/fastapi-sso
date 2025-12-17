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

⚠️ The following example demonstrates an unsafe pattern and must not be used in production. It will be removed from
future releases of docs.

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
