#!/usr/bin/env bash
set -euo pipefail

# Usage: ./git-acp.sh "your commit message"
msg="${1:-}"
if [[ -z "$msg" ]]; then
  echo "Usage: $0 \"commit message\"" >&2
  exit 1
fi

repo_dir="/Users/matthijsnuus/Desktop/FS-C/model/injection_model"

cd "$repo_dir"

# Make sure it's a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $repo_dir is not a Git repository." >&2
  exit 1
fi

git add -A

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

git commit -m "$msg"

# Push (set upstream if needed)
if git rev-parse --abbrev-ref "@{u}" >/dev/null 2>&1; then
  git push
else
  git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
fi

echo "Pushed ✔ from $repo_dir"
