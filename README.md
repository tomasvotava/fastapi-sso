# FastAPI SSO

![Supported Python Versions](https://img.shields.io/pypi/pyversions/fastapi-sso)
[![Test coverage](https://codecov.io/gh/tomasvotava/fastapi-sso/graph/badge.svg?token=SIFCTVSSOS)](https://codecov.io/gh/tomasvotava/fastapi-sso)
![Tests Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/test.yml?label=tests)
![Lint Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=ruff)
![Mypy Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=mypy)
![Black Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/lint.yml?label=black)
![CodeQL Workflow Status](https://img.shields.io/github/actions/workflow/status/tomasvotava/fastapi-sso/codeql-analysis.yml?label=CodeQL)
![PyPi weekly downloads](https://img.shields.io/pypi/dw/fastapi-sso)
![Project License](https://img.shields.io/github/license/tomasvotava/fastapi-sso)
![PyPi Version](https://img.shields.io/pypi/v/fastapi-sso)

FastAPI plugin to enable SSO to most common providers (such as Facebook login, Google login and login via
Microsoft Office 365 account).

This allows you to implement the famous `Login with Google/Facebook/Microsoft` buttons functionality on your
backend very easily.

**Documentation**: [https://tomasvotava.github.io/fastapi-sso/](https://tomasvotava.github.io/fastapi-sso/)

**Source Code**: [https://github.com/tomasvotava/fastapi-sso](https://github.com/tomasvotava/fastapi-sso/)

## Demo site

An awesome demo site was created and is maintained by even awesomer
[Chris Karvouniaris (@chrisK824)](https://github.com/chrisK824). Chris has also posted multiple
Medium articles about FastAPI and FastAPI SSO.

Be sure to see his tutorials, follow him and show him some appreciation!

Please see his [announcement](https://github.com/tomasvotava/fastapi-sso/discussions/150) with all the links.

Quick links for the eager ones:

- [Demo site](https://fastapi-sso-example.vercel.app/)
- [Medium articles](https://medium.com/@christos.karvouniaris247)

## Security warning

Please note that versions preceding `0.7.0` had a security vulnerability.
The SSO instance could share state between requests, which could lead to security issues.
**Please update to `0.7.0` or newer**.

Also, the preferred way of using the SSO instances is to use `with` statement, which will ensure the state is cleared.
See example below.

## Support this project

If you'd like to support this project, consider [buying me a coffee ☕](https://www.buymeacoffee.com/tomas.votava).
I tend to process Pull Requests faster when properly caffeinated 😉.

<a href="https://www.buymeacoffee.com/tomas.votava" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
    alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Supported login providers

### Official

- Google
- Microsoft
- Facebook
- Spotify
- Fitbit
- Github (credits to [Brandl](https://github.com/Brandl) for hint using `accept` header)
- generic (see [docs](https://tomasvotava.github.io/fastapi-sso/reference/sso.generic/))
- Notion
- Twitter (X)

### Contributed

- Kakao (by Jae-Baek Song - [thdwoqor](https://github.com/thdwoqor))
- Naver (by 1tang2bang92) - [1tang2bang92](https://github.com/1tang2bang92)
- Gitlab (by Alessandro Pischedda) - [Cereal84](https://github.com/Cereal84)
- Line (by Jimmy Yeh) - [jimmyyyeh](https://github.com/jimmyyyeh)
- LinkedIn (by Alessandro Pischedda) - [Cereal84](https://github.com/Cereal84)
- Yandex (by Akim Faskhutdinov) – [akimrx](https://github.com/akimrx)

See [Contributing](#contributing) for a guide on how to contribute your own login provider.

## Installation

### Install using `pip`

```console
pip install fastapi-sso
```

### Install using `poetry`

```console
poetry add fastapi-sso
```

## Contributing

If you'd like to contribute and add your specific login provider, please see
[Contributing](https://tomasvotava.github.io/fastapi-sso/contributing) file.
