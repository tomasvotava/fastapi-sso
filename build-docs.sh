#!/bin/bash

rm -rf ./docs/
pdoc3 --html -o ./docs/ fastapi_sso
mv ./docs/fastapi_sso/* ./docs/
rm -rf ./docs/fastapi_sso
