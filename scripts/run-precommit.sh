#!/usr/bin/env bash
# Helper script to run pre-commit with correct PyPI configuration
# Usage: ./scripts/run-precommit.sh [args]

set -e

# Change to project root
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Set PyPI index to avoid authentication issues with custom repositories
export PIP_INDEX_URL=https://pypi.org/simple/

# Run pre-commit with all provided arguments
pre-commit "$@"
