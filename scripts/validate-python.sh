#!/bin/sh
# Managed by Python Agent Forge.
set -eu
uv pip install -r requirements.txt
uv run python -m compileall .
