# todos

A lightweight, portable AI-agent task management system for software projects.
No server, no database, no dependencies — just files and a browser.

---

## What it does

- You write tasks in plain language into `INBOX.md`
- An AI agent (Claude) parses them, assigns groups/roles/statuses, and writes structured JSON
- A self-contained HTML file gives you a fast UI to view, filter, and move tasks

Everything is driven by `config.json` — groups, roles, and statuses are all yours to define.

---

## Files

| File | Purpose |
|------|---------|
| `INBOX.md` | Drop new todos here in any format |
| `tasks.json` | The task store (auto-managed, human-readable JSON) |
| `todos.html` | Browser UI — open this locally, no server needed |
| `config.json` | Your project's groups, roles, and statuses |
| `BRIEF.md` | Describe your project so the setup skill can generate config |
| `SETUP.md` | AI skill: reads BRIEF.md and writes config.json |
| `SKILL.md` | AI skill: parses INBOX.md and writes tasks.json |
| `WORKFLOW.md` | Documents the full agent pipeline |

---

## Getting started in a new project

### 1. Install into your project

**Via pip** (from GitHub):
```bash
pip install git+https://github.com/viperciyes/todosrepo.git
cd your-project
todos-init
```

**Or manually** — copy this folder into your project:
```
your-project/
└── todos/
    ├── INBOX.md
    ├── BRIEF.md
    ├── SETUP.md
    ├── SKILL.md
    ├── WORKFLOW.md
    ├── todos.html
    └── tasks.json   ← starts empty: {"version":1,"tasks":[]}
```

### 2. Fill in BRIEF.md

Answer the prompts in plain language:
- Project name
- What it does
- Who uses it (these become your roles)
- Tech areas or domains (these become your groups)

### 3. Run the setup skill

Tell your AI agent:

> "Run setup" or "Generate config from the brief"

The agent reads `BRIEF.md`, proposes a `config.json`, waits for your confirmation, then writes it.

### 4. Open todos.html in your browser

- Click **⚙ Config** and pick `config.json`
- Click **Open tasks.json** and pick `tasks.json`
- Both handles are remembered — they auto-load on every future visit

### 5. Add tasks and process the inbox

Write anything into `INBOX.md`, then tell the agent:

> "Process inbox"

The agent parses your items, assigns them to groups and roles from your config, and appends them to `tasks.json`. The UI reflects changes on the next reload.

---

## config.json reference

```json
{
  "projectName": "my-app",
  "groups": ["Backend", "Frontend", "DevOps", "Research", "General"],
  "roles": ["admin", "editor"],
  "statuses": ["todo", "in_progress", "decision", "done", "superseded"],
  "terminalStatuses": ["done", "superseded"]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `projectName` | yes | Shown in the UI header and page title |
| `groups` | yes | Work domains — at least one. Order matters (sidebar display order) |
| `roles` | no | User types. Use `[]` or omit if your project has no role distinction |
| `statuses` | yes | Workflow states, in display order |
| `terminalStatuses` | yes | Subset of `statuses` — these are styled as "closed" in the UI |

Groups are assigned colours automatically from a built-in palette. No colour config needed.

---

## Using it as a git repo

This folder is self-contained and has no dependencies on the parent project.
To use it across multiple projects, host it as its own repo and copy or submodule it in.

```bash
git init
git add .
git commit -m "init"
gh repo create todosrepo --public --push --source=.
```

Each project keeps its own `config.json`, `tasks.json`, and `INBOX.md` — all gitignored from the parent if you prefer, or committed alongside the code.
