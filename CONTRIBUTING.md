# Contributing

In order to add a new login provider, please make sure to adhere to the following guidelines to the best
of your abilities and possibilities.

## Dependencies management

Seeing the file `poetry.lock` you may have guessed this project relies on [Poetry](https://python-poetry.org/)
to manage dependencies.

If there is a need for a 3rd party dependency in order to integrate login provider, please try to make
use of [extras](https://python-poetry.org/docs/pyproject/#extras) in order not to make `fastapi-sso`
any heavier. Any dependency apart from the ones listed in `tool.poetry.dependencies` in
[`pyproject.toml`](https://github.com/tomasvotava/fastapi-sso/tree/master/pyproject.toml)
should be an extra along with it being optional. If you are not shure how to do this, let me know
the dependency in PR and I will add it before merging your code.

Also, **please strictly separate runtime dependencies from dev dependencies**.

## Provide examples

Please, try to provide examples for the login provider in the
[`examples/`](https://github.com/tomasvotava/fastapi-sso/tree/master/examples) directory.
**Always make sure your code contains no credentials before submitting the PR**.

## Code quality

I am myself rather a dirty programmer and so it feels a little out of place for me to talk about
code quality, but let's keep the code up to at least some standards.

### Formatting

As visible in `pyproject.toml`, I use `black` as a formatter with all the default settings except for
the `line_length` parameter. As seen in the file, I set it to 120 characters. Please try to keep
the code formatted this way.

It is easy to reformat the code by calling `black` from the repository root:

```console
$ poe black

All done! ✨ 🍰 ✨
13 files left unchanged.
```

### Linting

I use `pylint`. Detailed configuration is to be found in `.pylintrc` file.

Check your code by calling:

```console
$ poe pylint

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

If the code isn't 10/10 and you feel you have a good reason for it not to be, you may use
`pylint: disable=...` magic comments throughout the code, but please expect me to ask about it
when you submit the PR.

### Typechecking

Try to keep the code statically typechecked using `mypy`. Check that everything is alright by running:

```console
$ poe mypy

Success: no issues found in 13 source files
```

### Pre-commit

I use `pre-commit` to run all the above checks before committing. You can install it by calling:

```console
$ poe pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

### Tests

I use `pytest` for testing. Please try to provide tests for your code. If you are not sure how to
do it, let me know in the PR and I'll try to help you.

Run the tests by calling:

```console
poe test
```

Or using `tox`:

```console
tox
```

## Documentation

Please try to provide documentation for your code. I use `mkdocs` to generate the documentation.
In most cases, it should be enough to use docstrings (`pylint` will complain if you don't) and to provide
examples in the aforementioned `examples/` directory.
