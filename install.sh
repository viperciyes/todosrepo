#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$TARGET" = "." ]; then
  TARGET="$(pwd)"
fi

if [ ! -d "$TARGET" ]; then
  echo "Error: target directory '$TARGET' does not exist"
  echo "Usage: ./install.sh [path/to/project]"
  exit 1
fi

TODOS_DIR="$TARGET/todos"

if [ -d "$TODOS_DIR" ]; then
  echo "Error: '$TODOS_DIR' already exists"
  exit 1
fi

mkdir -p "$TODOS_DIR"

cp "$SCRIPT_DIR/INBOX.md" "$TODOS_DIR/"
cp "$SCRIPT_DIR/BRIEF.md" "$TODOS_DIR/"
cp "$SCRIPT_DIR/SETUP.md" "$TODOS_DIR/"
cp "$SCRIPT_DIR/SKILL.md" "$TODOS_DIR/"
cp "$SCRIPT_DIR/WORKFLOW.md" "$TODOS_DIR/"
cp "$SCRIPT_DIR/todos.html" "$TODOS_DIR/"
cp "$SCRIPT_DIR/README.md" "$TODOS_DIR/"

cat > "$TODOS_DIR/tasks.json" <<- JSON
{
  "version": 1,
  "tasks": []
}
JSON

cat > "$TODOS_DIR/config.json" <<- JSON
{
  "projectName": "",
  "groups": ["General"],
  "roles": [],
  "statuses": ["todo", "in_progress", "done"],
  "terminalStatuses": ["done"]
}
JSON

echo "✓ todos installed into $TODOS_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit todos/BRIEF.md with your project details"
echo "  2. Tell your AI agent: \"Run setup\""
echo "  3. Open todos/todos.html in your browser"
echo "  4. Add tasks to todos/INBOX.md, then tell agent: \"Process inbox\""
