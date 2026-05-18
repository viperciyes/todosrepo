import shutil
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent / "templates"

def main():
    target = Path.cwd()
    todos_dir = target / "todos"

    if todos_dir.exists():
        print(f"Error: {todos_dir} already exists")
        sys.exit(1)

    todos_dir.mkdir(parents=True)
    for f in TEMPLATES.iterdir():
        shutil.copy2(f, todos_dir / f.name)

    tasks_json = todos_dir / "tasks.json"
    tasks_json.write_text('{\n  "version": 1,\n  "tasks": []\n}\n')

    config_json = todos_dir / "config.json"
    config_json.write_text(
        '{\n  "projectName": "",\n  "groups": ["General"],\n  "roles": [],\n'
        '  "statuses": ["todo", "in_progress", "done"],\n'
        '  "terminalStatuses": ["done"]\n}\n'
    )

    print(f"todos installed into {todos_dir}")
    print("")
    print("Next steps:")
    print("  1. Edit todos/BRIEF.md with your project details")
    print('  2. Tell your AI agent: "Run setup"')
    print("  3. Open todos/todos.html in your browser")
    print('  4. Add tasks to todos/INBOX.md, then tell agent: "Process inbox"')
