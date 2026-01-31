# Copilot Customizations

Custom skills, agents, and prompts for SQL impact analysis and database change management.

## Quick Start

| Task | Command |
|------|---------|
| Start a change request | `@db-change-intake` |
| Analyze impact of a change | `@sql-impact analyze {object}` |
| Save impact report | `/saveImpactReport` |
| Save change request | `/saveChangeRequest` |

## Context Engineering (Large SVN Repos)

This repository includes context engineering for large SVN-based SQL repositories.

### Key Files

| File | Purpose |
|------|---------|
| `.copilotignore` | Excludes irrelevant files from Copilot indexing |
| `.copilot-context.md` | Repository manifest with module structure, naming conventions, critical tables |
| `templates/module-copilotignore.md` | Per-module ignore templates |

### Usage

1. **Reference context in prompts**: Use `#file:.copilot-context.md` to load domain knowledge
2. **Scope searches by module**: Always use `includePattern: "patches/{module}/**/*.sql"`
3. **Customize ignores**: Add `.copilotignore` files per module directory

### Search Strategy for Large Repos

```
# GOOD - Scoped to module
grep_search: "FROM\s+claim"
includePattern: "patches/claims/**/*.sql"

# BAD - Too broad
grep_search: "FROM\s+claim"
includePattern: "**/*.sql"
```

## Structure

```
copilot_client/
├── .copilotignore            # Root-level ignore patterns
├── .copilot-context.md       # Repository context manifest
├── templates/
│   └── module-copilotignore.md  # Per-module ignore templates
├── agents/
│   ├── sql-impact.agent.md       # Read-only impact analysis
│   └── db-change-intake.agent.md # Guided change request intake
├── prompts/
│   ├── saveImpactReport.prompt.md   # Save analysis as CSV/markdown
│   └── saveChangeRequest.prompt.md  # Save change request document
├── skills/
│   └── sql-impact-analysis/
│       ├── SKILL.md              # Router to reference files
│       └── references/
│           ├── severity-criteria.md  # Impact scoring
│           ├── tables/               # Column/table change patterns
│           │   ├── add-column.md
│           │   ├── modify-column.md
│           │   ├── drop-column.md
│           │   ├── rename-column.md
│           │   ├── add-table.md
│           │   └── drop-table.md
│           ├── procedures/           # Stored procedure patterns
│           │   └── patterns.md
│           ├── functions/            # Function patterns
│           │   └── patterns.md
│           ├── triggers/             # Trigger patterns
│           │   └── patterns.md
│           ├── views/                # View patterns
│           │   └── patterns.md
│           ├── indexes/              # Index patterns
│           │   └── patterns.md
│           ├── sequences/            # Sequence patterns
│           │   └── patterns.md
│           └── patches/              # Patch ordering
│               └── ordering.md
└── change-requests/              # Saved change request documents
    └── README.md
```

## Workflow

### 1. Intake (Human-in-the-Loop)

```
@db-change-intake → Guided questions → Save document → Human review
```

The intake agent collects:
- Object details (table, column, procedure, etc.)
- Business context (ticket, requester, timeline)
- Risk factors (critical table, existing data, etc.)

### 2. Impact Analysis

```
@sql-impact analyze {OBJECT_NAME}
```

The analysis agent:
- Loads appropriate reference file for change type
- Searches SQL files for dependencies
- Calculates severity score
- Generates markdown + CSV report

### 3. Review & Approval

Change request documents saved to `change-requests/` include:
- Technical specification
- Risk assessment
- Pre-deployment checklist
- Approval tracking table
- Placeholder for impact analysis results

### 4. Save Reports

```
/saveImpactReport   → CSV + markdown to reports/
/saveChangeRequest  → Document to change-requests/
```

## Agents

### `@sql-impact`

**Tools**: `search`, `read` (read-only)

Performs dependency analysis without making changes. Outputs:
- Markdown summary with severity indicator
- CSV data for Excel import

### `@db-change-intake`

**Tools**: `search`, `read`, `edit`

Guided workflow that:
- Asks structured questions
- Validates change details
- Creates change request document
- Hands off for human review

## Reference Files

Each reference file contains:
- **Risk level** for that change type
- **Patterns to search** (regex for grep_search)
- **Severity factors** (score contributors)
- **Pre-change checklist**
- **Migration strategies**

### By Change Type

| Change | Reference |
|--------|-----------|
| Add column | `tables/add-column.md` |
| Modify column | `tables/modify-column.md` |
| Drop column | `tables/drop-column.md` |
| Rename column | `tables/rename-column.md` |
| Add table | `tables/add-table.md` |
| Drop table | `tables/drop-table.md` |
| Procedure changes | `procedures/patterns.md` |
| Function changes | `functions/patterns.md` |
| Trigger changes | `triggers/patterns.md` |
| View changes | `views/patterns.md` |
| Index changes | `indexes/patterns.md` |
| Sequence changes | `sequences/patterns.md` |
| Patch ordering | `patches/ordering.md` |

## Severity Scoring

See `severity-criteria.md` for the full scoring system:

| Level | Score | Meaning |
|-------|-------|---------|
| 🟢 Low | 0-3 | Safe, standard deployment |
| 🟡 Medium | 4-6 | Needs review, test on staging |
| 🟠 High | 7-9 | Requires DBA approval, maintenance window |
| 🔴 Critical | 10+ | Executive approval, full rollback plan |

## Customization

### Add new object type patterns

1. Create `references/{object-type}/patterns.md`
2. Add entry to SKILL.md router table
3. Include search patterns, severity factors, checklist

### Modify severity criteria

Edit `references/severity-criteria.md`:
- Adjust base scores per change type
- Add/modify score modifiers
- Update critical tables list

### Customize change request template

Edit `prompts/saveChangeRequest.prompt.md`:
- Add company-specific fields
- Modify approval workflow
- Adjust checklist items
