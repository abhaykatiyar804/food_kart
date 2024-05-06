#!/usr/bin/env bash

set -e
set -x

PREFIX_CMD="poetry run"

${PREFIX_CMD} ruff check src tests scripts
