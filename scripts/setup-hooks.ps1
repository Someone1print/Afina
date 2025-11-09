# PowerShell script to setup git hooks on Windows
# Run this once after cloning the repository

if (-not (Test-Path ".git/hooks")) {
    Write-Host "Error: .git/hooks directory not found. Are you in a git repository?" -ForegroundColor Red
    exit 1
}

# Copy pre-commit hook
if (Test-Path ".githooks/pre-commit") {
    Copy-Item ".githooks/pre-commit" ".git/hooks/pre-commit" -Force
    Write-Host "✓ Pre-commit hook installed successfully" -ForegroundColor Green
} else {
    Write-Host "Error: .githooks/pre-commit not found" -ForegroundColor Red
    exit 1
}

