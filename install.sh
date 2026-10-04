#!/usr/bin/env bash
# Copies agents/ and skills/ (and thesis-writing/agents, thesis-writing/skills) into ~/.claude
# so they are available in every project.
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
dst="$HOME/.claude"

mkdir -p "$dst/agents" "$dst/skills"
agents=(); skills=()
for r in "$src" "$src/thesis-writing"; do
  if [ -d "$r/agents" ]; then
    cp "$r"/agents/*.md "$dst/agents/"
    for f in "$r"/agents/*.md; do agents+=("$(basename "$f" .md)"); done
  fi
  if [ -d "$r/skills" ]; then
    for d in "$r"/skills/*/; do
      cp -r "$d" "$dst/skills/"
      skills+=("$(basename "$d")")
    done
  fi
done

echo "Installed to $dst"
echo "Agents: $(printf '%s\n' "${agents[@]}" | sort | tr '\n' ' ')"
echo "Skills: $(printf '%s\n' "${skills[@]}" | sort | tr '\n' ' ')"
