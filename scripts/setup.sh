set  -e
set -x

echo "setting up project"
rm -rf .venv
# shellcheck disable=SC2046
poetry env use $(which python)
poetry config --list
poetry install -vv --no-interaction --no-ansi --with dev
