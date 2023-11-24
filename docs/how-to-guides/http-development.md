# HTTP and development

!!! danger "You should always use `https` in production"

In case you need to test on `localhost` and do not want to
use a self-signed certificate, make sure you set up redirect uri within your SSO provider to `http://localhost:{port}`
and then add this to your environment:

!!! info "Since `0.8.0` OAUTHLIB_INSECURE_TRANSPORT is set to `1` automatically if `allow_insecure_http` is `True` and this is not needed anymore."

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
