#!/bin/bash

COMMIT_MSG="${1:-bump}" # COMMIT_MSG = arg1 ? arg1 : "bump"

RED='\033[0;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
GRAY='\033[0;37m'
C='\033[0m'

echo

# build
echo -e "${CYAN}    ----    Starting build...    ----    \n${C}"
if ! python3 build_js.py; then
    echo -e "${RED}\n\n    Build failed!\n\n${C}"
    exit 1
fi



# changes ? commit : no
echo
if git diff-index --quiet HEAD --; then
    echo -e "${GRAY}    ----    No changes to commit.    ----    ${C}"
else
    echo -e "${CYAN}    ----    Changes detected, committing...    ----    \n${C}"
    git add . && \
    git commit -m "$COMMIT_MSG"
fi

# Push either way
echo -e "\n${CYAN}    ----    Pushing to GitHub...    ----    ${C}\n"
if ! git push origin main; then
    echo -e "\n\n${RED}    ----    Failed to push to GitHub!    ----    ${C}"
    exit 1
fi

echo -e "${GREEN}\n\n    ----    Deployment completed successfully! Haven gice done    ----    \n\n${C}"


read -p "[press any to close] " -n1 -s
