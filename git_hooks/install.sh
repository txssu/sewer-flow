#!/bin/bash

# Script to install git hooks

set -e

HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "Installing git hooks..."
echo ""

# Counter for installed hooks
INSTALLED_COUNT=0

# Find and install all hooks (excluding install.sh itself)
for hook_file in "$HOOKS_DIR"/*; do
    # Skip if it's a directory or install.sh itself
    if [ -d "$hook_file" ] || [ "$(basename "$hook_file")" = "install.sh" ]; then
        continue
    fi

    # Skip hidden files
    if [[ "$(basename "$hook_file")" == .* ]]; then
        continue
    fi

    hook_name=$(basename "$hook_file")

    # Copy hook and make it executable
    cp "$hook_file" "$GIT_HOOKS_DIR/$hook_name"
    chmod +x "$GIT_HOOKS_DIR/$hook_name"
    echo "✓ Installed $hook_name"

    ((INSTALLED_COUNT++))
done

echo ""
if [ $INSTALLED_COUNT -eq 0 ]; then
    echo "⚠️  No hooks found to install"
    exit 0
fi

echo "✅ Successfully installed $INSTALLED_COUNT hook(s)!"
