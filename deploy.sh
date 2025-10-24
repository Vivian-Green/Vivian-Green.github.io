#!/bin/bash
# deploy.sh

# Use provided commit message or default to "bump"
COMMIT_MSG="${1:-bump}"

python3 build_js.py && \
git add . && \
git commit -m "$COMMIT_MSG" && \
git push origin main
