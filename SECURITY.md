# Security Policy

## Overview

`fastapi-sso` handles logins, so a bug here can become someone else's account takeover. Security reports are the most
useful thing you can send me, and they get priority over everything else in the tracker.

## Supported Versions

Fixes ship in a new release built from `master`. There are no maintenance branches and no backports, so only the
latest release receives security fixes.

| Version        | Supported          |
| -------------- | ------------------ |
| Latest release | :white_check_mark: |
| Anything older | :x:                |

Upgrade to the latest release before reporting, so we don't spend time on something already fixed.

## Reporting a Vulnerability

**Report privately, not in the public issue tracker.**

Use GitHub's private vulnerability reporting, which is enabled on this repository:

1. Open [Report a vulnerability](https://github.com/tomasvotava/fastapi-sso/security/advisories/new).
2. Describe the issue, the version you tested against, and the impact you think it has.
3. Include steps to reproduce, ideally a short runnable snippet.
4. Suggest a severity if you have one in mind. I may end up disagreeing, and that is a normal part of triage.

Only you and the maintainers can see the report. It stays private until an advisory is published.

If you have already opened a public issue before reading this, don't worry about it. Say so in the private report and
I will handle the cleanup.

## What to Expect

- An acknowledgement that I received the report.
- Triage, where I confirm or dispute the finding and we agree on severity.
- A fix, released as a new version.
- A published GitHub Security Advisory naming you as the reporter, unless you would rather stay anonymous.
- A CVE, requested through GitHub, for anything that affects users on the default configuration.

This is a side project maintained by one person, so response times depend on what else my week looks like. I would
rather tell you that up front than promise a turnaround I cannot keep.

## Disclosure Policy

Disclosure is coordinated. The advisory goes public once the fixed version is on PyPI, so that everyone reading it has
somewhere to upgrade to. Please hold off on publishing details until then.

If a fix is taking unreasonably long, tell me. Agreeing on a disclosure date is fair, going around me without saying
anything is not.

## Non-Security Issues

Everything that is not a vulnerability belongs in the [issue tracker](https://github.com/tomasvotava/fastapi-sso/issues),
including things you are annoyed about. If there is something concerning `fastapi-sso` you would like to bitch about,
let me know and we'll bitch about it together.

## Thank You

Reporting takes real effort and I appreciate every report I get, including the ones that turn out to be false alarms.
