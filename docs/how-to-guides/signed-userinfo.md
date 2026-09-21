# Verify a signed UserInfo response

!!! info "Added in `0.23.0`"

OpenID Connect Core 1.0
([section 5.3.2](https://openid.net/specs/openid-connect-core-1_0.html#UserInfoResponse))
allows a provider to sign its UserInfo response. In that case the claims are returned as a
JWT with an `application/jwt` content type instead of a plain JSON body, and the client
**must** verify the signature before trusting the claims.

`fastapi-sso` handles that case automatically: the content type of the response selects
the parsing path — `application/json` is read as plain JSON, `application/jwt` is verified
against the provider's JWKS and decoded. Providers do not always set an accurate content
type, so when it is missing or unknown the body is inspected: a JWT is verified, anything
else is parsed as JSON. Plain JSON responses keep working exactly as before, so no
configuration is needed.

```python
# Nothing to change: the same code handles both cases.
async with sso:
    user = await sso.verify_and_process(request)
```

!!! warning "Extra dependency"
    Verifying a JWS requires `cryptography`, which is not installed by default:

    ```console
    pip install fastapi-sso[crypto]
    ```

    Only the asymmetric algorithms listed in `userinfo_signing_algorithms` are accepted,
    so a token signed with a shared secret (`HS256`, …) can never be mistaken for a valid
    response, even if the provider serves one.

## What is checked

1. The `kid` of the JWT header selects the matching key in the provider JWKS
   (`jwks_uri` from the discovery document).
2. The signature is verified against that key — asymmetric algorithms only.
3. `aud` must match the `client_id`.
4. The resulting claims are then passed to `openid_from_response`, as usual.

Any failure raises an `SSOLoginError` with a `401` status code.

## Restricting the accepted algorithms

If your provider only ever signs with a subset of the algorithms, narrow the list on your
provider subclass:

```python
class MyProvider(GenericSSO):
    # Only accept what the provider actually uses.
    userinfo_signing_algorithms = ["ES256"]
```
