# Skill: Process Inbox

## Purpose
Read `INBOX.md`, parse all todo items, group them into tasks, and append them to `tasks.json`. Clear the inbox when done.

## Trigger
User says something like: "process inbox", "sort inbox", "import todos", or asks you to read/group the inbox.

## Steps

### 1. Read config and data files
- Read `todos/config.json` — this defines the valid `groups`, `roles`, and `statuses` for this project
- Read `todos/INBOX.md` (raw dump)
- Read `todos/tasks.json` (existing tasks — needed to avoid duplicates and to determine the next ID)

If `config.json` does not exist, use these fallback defaults:
- groups: `["General"]`
- roles: `[]`
- statuses: `["todo", "in_progress", "done"]`

### 2. Determine the next task ID
- Find the highest existing numeric ID (e.g. if `t-007` exists, next is `t-008`)
- If no tasks exist, start from `t-001`

### 3. Parse inbox items
The inbox is free-form. Items may be:
- Bullet points (`-` or `*`)
- Numbered lists
- All-caps sentences (treat as a task)
- Paragraphs (one paragraph = one task)
- Sections under a `## Header` (header becomes the group hint)
- Any language — preserve as-is in the description

Parse rules:
- Short standalone lines → title candidate + empty description
- Long blocks of text → first sentence = title, rest = description
- All-caps text → normalize to title case for `title`, keep original in `description`
- Code blocks or multi-line commands → treat as a single task, keep full text in `description`

### 4. Assign groups and roles
Use the groups defined in `config.json`. Use judgment to assign the best-fitting group.
If no groups are defined, use `"General"` for everything.

Use the roles defined in `config.json`. Assign roles that the task is relevant to.
Use `[]` for infrastructure, tooling, or tasks with no specific user-facing role.
If no roles are defined in config, always use `[]`.

### 5. Build new task objects
For each parsed item, create:
```json
{
  "id": "t-NNN",
  "title": "Short descriptive title (max ~60 chars)",
  "description": "Full original text preserved here",
  "group": "<one of the groups from config.json>",
  "roles": ["<zero or more roles from config.json>"],
  "status": "<first non-terminal status from config.json, or 'todo' as fallback>",
  "statusNote": "",
  "createdAt": "YYYY-MM-DD",
  "updatedAt": "YYYY-MM-DD"
}
```

Use today's date for `createdAt` and `updatedAt`.

**Choosing status:**
- Default to the first non-terminal status in `config.statuses` for actionable items
- If the item is a question, architectural decision, or choice to be resolved: use `"decision"` if it exists in config, otherwise use the default
- If the item is a future idea or vague vision with no immediate action: use `"futuristic"` if it exists in config, otherwise use the default

### 6. Deduplication
Before adding, check if a task with a very similar title already exists in `tasks.json`. If yes, skip it and note it to the user.

### 7. Write tasks.json
Append new tasks to the `tasks` array. Write the full updated JSON back to `todos/tasks.json`.

### 8. Clear INBOX.md
Replace the content of `todos/INBOX.md` with the clean template:

```markdown
# Inbox

Drop new todos here in any format — bullets, paragraphs, headers, free text.
When ready, ask Claude to process the inbox.

---

```

### 9. Report to user
Summarize:
- How many tasks were added and to which groups
- Any items that were skipped (duplicates or unparseable)
- Remind them to open `todos/todos.html` to review
