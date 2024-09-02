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
