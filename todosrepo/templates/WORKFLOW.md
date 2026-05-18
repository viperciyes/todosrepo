# Todo Workflow

## How it works

You write todos in plain language into `INBOX.md`. Agents handle the rest.

---

## The Files

| File | Purpose |
|------|---------|
| `INBOX.md` | Drop raw todos here, any format |
| `config.json` | Groups, roles, and statuses for your project |
| `tasks.json` | Structured task store |
| `todos.html` | Browser UI |

---

## The Agent Pipeline

### 1. Setup (invoke "Run setup")
Reads `BRIEF.md`, proposes a `config.json`, waits for your confirmation, then writes it.

### 2. Process Inbox (invoke "Process inbox")
Reads `INBOX.md`, categorizes each item, appends to `tasks.json` with the correct group/role/status, clears the inbox.

---

## Rules

- Use `INBOX.md` to add new tasks — let the agent process them.
- Open `todos.html` in your browser to view, filter, and manage tasks.
- Update `BRIEF.md` and re-run setup if your project's groups/roles change.
