# Skill: Setup — Generate config.json from BRIEF.md

## Purpose
Read `BRIEF.md`, propose a `config.json` tailored to the project, wait for user confirmation, then write it.

## Trigger
User says something like: "run setup", "generate config", "set up todos", or asks you to read the brief.

## Steps

### 1. Read both files
- Read `todos/BRIEF.md`
- Read `todos/config.json` (if it exists — to show what will change)

### 2. Generate proposed config
From the brief, infer:

**projectName** — the project name as written.

**groups** — work domains that make sense for the tech stack described.
Default fallback if nothing specific: `["Backend", "Frontend", "Design", "DevOps", "Research", "General"]`
Match to what was described — e.g. a mobile app might have `"iOS"` and `"Android"` instead of `"Flutter"`.

**roles** — user types mentioned. If none are mentioned, use `[]`. Do not force roles.
Examples: `["admin", "editor"]` / `["developer", "designer"]` / `[]`

**statuses** — ordered list of workflow states. Suggest a sensible default based on the project type:
`["todo", "in_progress", "decision", "futuristic", "done", "superseded"]`
If the brief suggests a simpler workflow (solo project, quick scripts), offer a shorter set:
`["todo", "in_progress", "done"]`

**terminalStatuses** — which statuses mean "closed". Typically the last one or two. Always a subset of `statuses`.

### 3. Present the proposal
Show the proposed config as a formatted JSON block. Explain each field in one sentence.
Ask: "Does this look right? Edit anything you like, then say 'confirm' to write it — or tell me what to change."

### 4. Wait for confirmation
Do not write anything until the user explicitly confirms. If they request changes, update the proposal and re-present.

### 5. Write config.json
Once confirmed, write the final JSON to `todos/config.json`.

### 6. Report
Tell the user:
- `config.json` written
- Remind them that `todos.html` reads config on load — no manual steps needed
- Suggest they open `todos.html` and pick `tasks.json` to verify
