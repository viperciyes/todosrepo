# Plan: defvault-todos Obsidian Plugin

**Goal:** Replace `todos.html` + `server.py` with a native Obsidian plugin that renders
the same todos board (role strip, status tabs, card grid, right panel) as a workspace
view. No server, no browser tab, no file picker — opens from Obsidian's ribbon or
command palette, reads and writes `tasks.json` / `config.json` directly via the vault API.

---

## Decision: File Location

Obsidian plugins read vault files via `app.vault` — which only covers files *inside* the
vault root. Currently `tasks.json` and `config.json` live at `defvault/todos/` which is
**outside** the vault (`defvault/defvault/`).

Two options:

1. **Move files into the vault** — put them at `defvault/defvault/todos/tasks.json` etc.
   Clean, idiomatic. The vault path is configurable in plugin settings.

2. **Use Node `fs` directly** — Obsidian desktop plugins have access to Node.js, so
   `require('fs')` works. Lets the files stay where they are. Less clean.

**Recommended: option 1.** Move `tasks.json` and `config.json` into the vault at
`todos/tasks.json` and `todos/config.json` (relative to vault root). Update `todosRepo`
as the canonical template too. The `server.py` + `serve.sh` can stay for standalone use.

---

## Repo Structure

Create a new directory: `defvault/obsidian-plugin/` (inside the defvault git repo, NOT
inside the vault — it's the plugin source). Build output gets copied into the vault.

```
defvault/obsidian-plugin/
├── manifest.json          # Plugin metadata (id, name, version, minAppVersion)
├── package.json           # obsidian (peer), esbuild, typescript (devDeps only)
├── tsconfig.json
├── esbuild.config.mjs     # Bundles src/main.ts → dist/main.js
├── src/
│   ├── main.ts            # Plugin class — registers view, ribbon icon, commands
│   ├── TodosView.ts       # ItemView subclass — mounts and tears down the board
│   ├── FileStore.ts       # All vault I/O: load config, load tasks, save tasks
│   ├── types.ts           # Task and Config TypeScript interfaces
│   └── ui/
│       ├── board.ts       # renderAll, renderSidebar, renderMain — ported from todos.html
│       ├── panel.ts       # openPanel, closePanel, actionButtons — ported from todos.html
│       ├── mutations.ts   # setStatus, updateNote, changeGroup — ported from todos.html
│       └── styles.ts      # The full CSS block from todos.html, injected as a <style> tag
└── dist/
    └── main.js            # esbuild output — this is what Obsidian loads
```

Install location inside the vault:
```
defvault/defvault/.obsidian/plugins/defvault-todos/
    main.js        ← copy of dist/main.js
    manifest.json  ← copy of manifest.json
```

---

## Implementation Steps

### Step 1 — Scaffold
- `manifest.json`: id `defvault-todos`, name `Todos`, version `0.1.0`, minAppVersion `1.4.0`
- `package.json`: devDeps `obsidian`, `esbuild`, `typescript`, `@types/node`
- `tsconfig.json`: target ES2018, moduleResolution node, strict true
- `esbuild.config.mjs`: bundle `src/main.ts` → `dist/main.js`, external `obsidian`, platform node, format cjs

### Step 2 — Types (`src/types.ts`)
```ts
export interface Task {
  id: string;
  title: string;
  description: string;
  group: string;
  roles: string[];
  status: string;
  statusNote: string;
  createdAt: string;
  updatedAt: string;
}

export interface Config {
  projectName: string;
  groups: string[];
  roles: string[];
  statuses: string[];
  terminalStatuses: string[];
}

export interface TasksFile {
  version: number;
  tasks: Task[];
}
```

### Step 3 — FileStore (`src/FileStore.ts`)
```ts
// Wraps app.vault for tasks.json and config.json.
// Paths are relative to vault root, set in plugin settings.
class FileStore {
  constructor(private app: App, private tasksPath: string, private configPath: string)
  async loadConfig(): Promise<Config>
  async loadTasks(): Promise<Task[]>
  async saveTasks(tasks: Task[]): Promise<void>
  // Watch for external changes (e.g. inbox processor writing tasks.json)
  watchTasks(onChange: (tasks: Task[]) => void): () => void  // returns unsubscribe fn
}
```

`saveTasks` uses `app.vault.adapter.write(path, JSON.stringify(...))` — bypasses
`TFile` cache and writes atomically. `loadConfig` / `loadTasks` use
`app.vault.adapter.read(path)`.

`watchTasks` uses `app.vault.on('modify', file => { if file.path === tasksPath ... })`.

### Step 4 — TodosView (`src/TodosView.ts`)
```ts
export const VIEW_TYPE = 'defvault-todos';

export class TodosView extends ItemView {
  private store: FileStore;
  private tasks: Task[] = [];
  private cfg: Config;
  // ... state matching todos.html: activeTab, selectedId, activeRole, etc.

  getViewType() { return VIEW_TYPE; }
  getDisplayText() { return 'Todos'; }
  getIcon() { return 'check-square'; }  // Obsidian built-in icon

  async onOpen() {
    // 1. Inject styles into containerEl
    // 2. Build HTML skeleton (header, sidebar, main, panel) — same structure as todos.html
    // 3. Load config + tasks from FileStore
    // 4. applyConfig(cfg)
    // 5. renderAll()
    // 6. Subscribe to file watcher for live reload
  }

  async onClose() {
    // Unsubscribe file watcher, clean up DOM
  }
}
```

### Step 5 — UI Port (`src/ui/`)

The JS in `todos.html` splits cleanly across three files. Key changes from the HTML version:

| todos.html | plugin equivalent |
|---|---|
| `fetch('./config.json')` | `store.loadConfig()` |
| `fetch('./tasks.json')` | `store.loadTasks()` |
| `fetch('/save', POST)` | `store.saveTasks(tasks)` |
| `document.getElementById(...)` | `this.containerEl.querySelector(...)` |
| `boot()` | called from `onOpen()` |
| `IndexedDB` / `dirHandle` | removed entirely |

Everything else — `applyConfig`, `renderAll`, `renderSidebar`, `renderMain`, `cardHTML`,
`openPanel`, `actionButtons`, `setStatus`, `updateNote`, `changeGroup`, the save
debounce — ports verbatim or near-verbatim.

### Step 6 — Main Plugin (`src/main.ts`)
```ts
export default class TodosPlugin extends Plugin {
  settings: { tasksPath: string; configPath: string };

  async onload() {
    await this.loadSettings();
    this.registerView(VIEW_TYPE, leaf => new TodosView(leaf, this));
    this.addRibbonIcon('check-square', 'Open Todos', () => this.activateView());
    this.addCommand({ id: 'open-todos', name: 'Open Todos board', callback: () => this.activateView() });
    this.addSettingTab(new TodosSettingTab(this.app, this));
  }

  async activateView() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE)[0];
    if (!leaf) {
      leaf = workspace.getLeaf('tab');  // opens in a new tab
      await leaf.setViewState({ type: VIEW_TYPE, active: true });
    }
    workspace.revealLeaf(leaf);
  }
}
```

### Step 7 — Settings Tab (`src/main.ts` or separate file)
Two text inputs:
- **Tasks file** (default: `todos/tasks.json`)
- **Config file** (default: `todos/config.json`)

On change: reload FileStore paths and re-render.

### Step 8 — Build & Install script
Add to `package.json`:
```json
"scripts": {
  "build": "node esbuild.config.mjs",
  "deploy": "node esbuild.config.mjs && cp dist/main.js manifest.json ../defvault/.obsidian/plugins/defvault-todos/"
}
```
`npm run deploy` builds and installs in one step. After first install, enable the plugin
in Obsidian → Settings → Community plugins.

---

## What Does NOT Change

- `tasks.json` schema — identical, plugin reads the same format
- `config.json` schema — identical
- The inbox processor (`SKILL.md`) — still works, just writes to the vault path
- `todosRepo` — stays as the standalone HTML template for non-Obsidian use

---

## Open Questions for Implementation Session

1. **Vault root path** — need to confirm where `defvault/defvault/` actually sits on
   disk and verify `.obsidian/` exists there before writing the plugin dir.

2. **tasks.json migration** — move from `defvault/todos/tasks.json` to
   `defvault/defvault/todos/tasks.json`. Simple file copy, update plugin default path.

3. **Save-ind CSS** — the `.save-ind` styles are in the HTML's `<style>` block.
   Confirm they're included in `styles.ts`.

4. **Obsidian version** — check `minAppVersion` against the installed version
   (Settings → About). Target 1.4.0 is safe for most installs.

---

## Effort Estimate

| Step | Effort |
|---|---|
| Scaffold + types + FileStore | ~30 min |
| TodosView skeleton + styles | ~20 min |
| UI port (board + panel + mutations) | ~45 min |
| Main plugin + settings | ~20 min |
| Build setup + deploy + test | ~20 min |
| **Total** | **~2.5 hours** |

---

## Starting Point for Next Session

1. Read this file.
2. Read `defvault/CLAUDE.md` (safety rules).
3. Read `defvault/todos/tasks.json` and `config.json` (confirm current schema).
4. Check vault root: `ls defvault/defvault/.obsidian/` — confirm plugins dir exists.
5. Create checkpoint commit: `git add -A && git commit -m "checkpoint: before obsidian plugin"`
6. Create `defvault/obsidian-plugin/` and begin Step 1.
