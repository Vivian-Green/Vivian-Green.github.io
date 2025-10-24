#!/bin/bash
# deploy.sh

# Use provided commit message or default to "bump"
COMMIT_MSG="${1:-bump}"

# Run the build script
python3 build_js.py

# Check if there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    echo "Changes detected, committing..."
    git add . && \
    git commit -m "$COMMIT_MSG"
fi

# Push regardless (in case there are commits that haven't been pushed yet)
echo "Pushing to origin/main..."
git push origin main
