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
