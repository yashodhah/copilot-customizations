# SQL Impact Analysis for Large Repositories

A Copilot-powered workflow for analyzing database schema changes in large SQL repositories.

---

## Quick Start

### Choose Your Entry Point

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINTS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📝 GUIDED INTAKE                    ⚡ QUICK PROMPTS                        │
│  ─────────────────                   ─────────────────                       │
│  @db-change-intake                   /addColumn                              │
│  → For new change requests           /dropColumn                             │
│  → Asks structured questions         /editColumn                             │
│  → Saves CR document                 /renameColumn                           │
│  → Hands off to @sql-impact          → For quick, focused analysis           │
│                                                                              │
│  🔍 DIRECT ANALYSIS                  📊 REPORTING                            │
│  ─────────────────                   ─────────────────                       │
│  @sql-impact                         /saveImpactReport                       │
│  → Full impact analysis              → Export CSV + Markdown                 │
│  → Risk classification               /generateImpactExcel                    │
│  → Severity scoring                  → Business-friendly Excel               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Options

### Option 1: Full Guided Workflow (Recommended for New Users)

```
@db-change-intake  →  @sql-impact  →  /saveImpactReport  →  /generateImpactExcel
     │                    │                   │                      │
     ▼                    ▼                   ▼                      ▼
 Gather info         Find risks          Save files           Excel for
 Save CR doc         Score severity      CSV + Markdown       business
```

**Step-by-step:**
1. `@db-change-intake` - "I need to drop the legacy_flag column from customers"
2. Agent asks clarifying questions, saves change request document
3. `@sql-impact analyze customers.legacy_flag` - Finds all dependencies
4. Review results with risk classification (🔴 Risk / 🟡 Review / 🟢 Safe)
5. `/saveImpactReport` - Export for team review
6. `/generateImpactExcel` - Create Excel for business stakeholders

### Option 2: Quick Analysis (For Experienced Users)

Use quick prompts for common operations:

| Prompt | Use When |
|--------|----------|
| `/addColumn` | Adding a new column |
| `/dropColumn` | Removing a column (destructive!) |
| `/editColumn` | Changing type, size, or constraints |
| `/renameColumn` | Renaming a column (breaking change) |

**Example:**
```
/dropColumn customers.fax_number
```

### Option 3: Direct Analysis

Skip the prompts and talk directly to the agent:

```
@sql-impact What's the impact of renaming policies.policy_id to policy_number?
```

---

## Understanding the Output

### Risk Classification

Not all matches are risks. The agent classifies each match:

| Icon | Level | Meaning | Action |
|------|-------|---------|--------|
| 🔴 | **Risk** | Will break or fail | Must fix before change |
| 🟡 | **Review** | May be affected | Human decision needed |
| 🟢 | **Safe** | Found reference, no impact | Informational only |

### Example: Adding a Column

| Pattern Found | Risk Level | Why |
|---------------|------------|-----|
| `INSERT INTO table VALUES (...)` | 🔴 Risk | Column count mismatch |
| `SELECT * FROM table` | 🟡 Review | Returns new column |
| `INSERT INTO table (col1, col2)` | 🟢 Safe | Explicit columns |

### Output Thresholds

The agent manages output based on result count:

| Matches | What You See |
|---------|--------------|
| 1-25 | Full table + CSV in chat |
| 26-50 | Top 25 + CSV in chat |
| 51-99 | Top 10 only → use `/saveImpactReport` |
| 100-499 | Summary only → CSV auto-saved |
| **500+** | **STOP** → Rethink the change |

---

## Key Files

| File | Purpose |
|------|---------|
| **Agents** | |
| [agents/sql-impact.agent.md](agents/sql-impact.agent.md) | Main analysis agent |
| [agents/db-change-intake.agent.md](agents/db-change-intake.agent.md) | Guided intake workflow |
| **Quick Prompts** | |
| [prompts/addColumn.prompt.md](prompts/addColumn.prompt.md) | Add column analysis |
| [prompts/dropColumn.prompt.md](prompts/dropColumn.prompt.md) | Drop column analysis |
| [prompts/editColumn.prompt.md](prompts/editColumn.prompt.md) | Modify column analysis |
| [prompts/renameColumn.prompt.md](prompts/renameColumn.prompt.md) | Rename column analysis |
| **Reporting** | |
| [prompts/saveImpactReport.prompt.md](prompts/saveImpactReport.prompt.md) | Export CSV + Markdown |
| [prompts/generateImpactExcel.prompt.md](prompts/generateImpactExcel.prompt.md) | Business Excel report |
| **Skill (Source of Truth)** | |
| [skills/sql-impact-analysis/SKILL.md](skills/sql-impact-analysis/SKILL.md) | Patterns, scoring, risk classification |
| **Context** | |
| [.copilot-context.md](.copilot-context.md) | Repository manifest |
| [.copilotignore](.copilotignore) | Ignore patterns |

---

## Repository Context Setup

### The Manifest (.copilot-context.md)

This file tells the agent about your repository structure:

```markdown
## Module Map
| Module | Path | Owner |
|--------|------|-------|
| claims | patches/claims/ | Claims Team |
| policies | patches/policies/ | Policy Team |

## Critical Tables
- customers (PII)
- policies (core business)
- claims (financial)

## Table → Module Mapping
| Table | Module |
|-------|--------|
| customers | shared |
| policies | policies |
```

**Keep this updated!** The agent uses it to:
- Scope searches to relevant modules
- Calculate severity (critical tables = higher score)
- Coordinate cross-module impacts

### Ignore Patterns (.copilotignore)

Reduce noise by excluding:
- Archive folders
- Test data
- Generated files
- SVN metadata

---

## Large Result Handling

### Sub-Agent Pattern (100+ matches)

When results exceed 100, the agent uses a sub-agent:

1. **You see immediately**: First 10 results + severity assessment
2. **Background**: Sub-agent collects ALL matches
3. **Saved automatically**: `copilot_impact_analysis/{object}-{date}.csv`
4. **Generate report**: Run `/generateImpactExcel` for business review

### 500+ Files Gate

If a change affects 500+ files, the agent **stops** and asks you to:
- Rethink the approach
- Scope down to one module
- Consider a phased migration

This prevents catastrophic changes from proceeding without proper review.

---

## Customization

### Add New Modules

1. Edit `.copilot-context.md` - add to Module Map
2. Add table→module mappings
3. Mark critical tables if applicable

### Modify Risk Classification

Edit the reference files in `skills/sql-impact-analysis/references/tables/`:
- `add-column.md`
- `drop-column.md`
- `rename-column.md`
- `modify-column.md`

### Customize Change Request Template

Edit `prompts/saveChangeRequest.prompt.md` to add:
- Company-specific fields
- Approval workflow
- Checklist items

---

## Tips

1. **Start scoped** - Always let the agent search within the module first
2. **Trust the gates** - When the agent pauses at 25+, 100+, or 500+, take a moment to review
3. **Use risk levels** - Focus on 🔴 Risks first, then 🟡 Review items
4. **Export for team** - Use `/generateImpactExcel` for stakeholder meetings
5. **Keep manifest updated** - The agent is only as good as its context
