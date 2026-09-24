#!/usr/bin/env bash
# Copies agents/ and skills/ into ~/.claude so they are available in every project.
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
dst="$HOME/.claude"

mkdir -p "$dst/agents" "$dst/skills"
cp "$src"/agents/*.md "$dst/agents/"
for d in "$src"/skills/*/; do
  cp -r "$d" "$dst/skills/"
done

echo "Installed to $dst"
echo "Agents: $(ls "$src/agents" | sed 's/\.md$//' | tr '\n' ' ')"
echo "Skills: $(ls "$src/skills" | tr '\n' ' ')"
