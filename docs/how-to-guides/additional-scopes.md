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
