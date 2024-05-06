#!/bin/sh

set -e
set -x

PREFIX_CMD='poetry run'


${PREFIX_CMD} coverage run -m pytest tests