#!/bin/sh
# Setup script to install git hooks
# Run this once after cloning the repository

if [ ! -d ".git/hooks" ]; then
    echo "Error: .git/hooks directory not found. Are you in a git repository?"
    exit 1
fi

# Copy pre-commit hook
if [ -f ".githooks/pre-commit" ]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✓ Pre-commit hook installed successfully"
else
    echo "Error: .githooks/pre-commit not found"
    exit 1
fi

