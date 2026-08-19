#!/bin/sh
# Managed by Python Agent Forge.
set -eu
uv sync
uv run python -m compileall .
