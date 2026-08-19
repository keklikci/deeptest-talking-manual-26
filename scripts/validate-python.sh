#!/bin/sh
# Managed by Python Agent Forge.
set -eu
uv sync --locked
uv run python -m compileall .
