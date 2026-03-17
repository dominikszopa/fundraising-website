#!/usr/bin/env bash
# Start the Django dev server for Playwright tests.
#
# Uses the active virtualenv's python3 when Django is already importable
# (no poetry overhead), otherwise falls back to `poetry run` so it works
# without an activated shell.
export PLAYWRIGHT_TESTING=true

if python3 -c "import django" 2>/dev/null; then
    exec python3 manage.py runserver --noreload 127.0.0.1:8000
else
    # Prefer $VIRTUAL_ENV (instant) over `poetry env info --path` (~1s)
    VENV_PATH="${VIRTUAL_ENV:-$(poetry env info --path 2>/dev/null)}"
    if [ -n "$VENV_PATH" ] && [ -x "$VENV_PATH/bin/python3" ]; then
        exec "$VENV_PATH/bin/python3" manage.py runserver --noreload 127.0.0.1:8000
    else
        exec poetry run python3 manage.py runserver --noreload 127.0.0.1:8000
    fi
fi
