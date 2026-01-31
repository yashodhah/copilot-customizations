# Copilot Context Engineering for Large SVN SQL Repos

This folder contains a working example of how to build **Copilot-friendly context engineering** for a large SVN-based SQL patch repository. The goal is to **improve context quality**, reduce noise, and keep Copilot’s search and analysis bounded to relevant modules.

## Idea Summary

Large SVN repositories often exceed Copilot’s indexing limits and lack Git-native metadata. This approach addresses that by:

1. **Explicit ignore control** with `.copilotignore`
2. **Structured domain context** with `.copilot-context.md`
3. **Module-scoped search strategy** baked into skills and prompts
4. **Human-in-the-loop workflows** for change intake and impact analysis

## Key Files

| File | Purpose |
|------|---------|
| [.copilotignore](.copilotignore) | Central ignore patterns to reduce index noise |
| [.copilot-context.md](.copilot-context.md) | Repository manifest (modules, naming, critical tables) |
| [templates/module-copilotignore.md](templates/module-copilotignore.md) | Per-module ignore templates |
| [skills/sql-impact-analysis/SKILL.md](skills/sql-impact-analysis/SKILL.md) | Skill router with large-repo search strategy |
| [prompts/saveImpactReport.prompt.md](prompts/saveImpactReport.prompt.md) | Export CSV + Excel-skill handoff |

## How It Works

### 1. Scope the Search

Use module-specific `includePattern` values instead of searching the full repo:

- Claims: `patches/claims/**/*.sql`
- Policies: `patches/policies/**/*.sql`
- Payments: `patches/payments/**/*.sql`
- Shared: `patches/shared/**/*.sql`

### 2. Load Domain Context

Reference the manifest in prompts:

`#file:.copilot-context.md`

This gives the model the repository map, naming conventions, and critical table list.

### 3. Reduce Noise

Use `.copilotignore` to exclude archives, test data, generated files, and SVN metadata.

### 4. Run the Workflow

- `@db-change-intake` → guided intake and save change request
- `@sql-impact` → scoped dependency analysis + severity scoring
- `/saveImpactReport` → save CSV/markdown and hand off to Excel skill

## Structure

```
copilot_client/
├── .copilotignore
├── .copilot-context.md
├── templates/
│   └── module-copilotignore.md
├── agents/
├── prompts/
├── skills/
└── change-requests/
```

## Notes for Prompt/Skill Authors

- **Never search root** (`**/*.sql`) on large repos
- **Prefer regex + `grep_search`** over semantic search unless indexed
- **Use module scoping** as the first step in every analysis
- **Document new modules** in `.copilot-context.md` as they’re added

### Customize change request template

Edit `prompts/saveChangeRequest.prompt.md`:
- Add company-specific fields
- Modify approval workflow
- Adjust checklist items
