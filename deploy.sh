#!/bin/bash
# deploy.sh

# Use provided commit message or default to bump
COMMIT_MSG="${1:-bump}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[1;32m'
C='\033[0m'

echo

if ! python3 build_js.py; then
    echo -e "${RED}\n\n     Build failed!\n\n${C}"
    exit 1
fi

if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    echo "Changes detected, committing..."
    git add . && \
    git commit -m "$COMMIT_MSG"
fi

# Push either way
echo -e "\nPushing to GitHub..."
if ! git push origin main; then
    echo -e "${RED}\n\n     Failed to push to GitHub!${C}"
    exit 1
fi

echo -e "${GREEN}\n\n       Deployment completed successfully!\n\n${C}"
