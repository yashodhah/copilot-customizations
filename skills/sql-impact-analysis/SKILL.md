---
name: sql-impact-analysis
description: 'Analyze database schema changes for impact and risk. Use for: SQL dependency mapping, finding affected queries/procedures/views/triggers, assessing change severity, identifying breaking changes before deployment, database migration and patch risk assessment.'
---

# SQL Impact Analysis

## Repository Context

> **Important**: Load the repository context first for domain knowledge.
> Reference: `#file:.copilot-context.md`

This skill analyzes a **large SVN-based SQL patch repository** for an insurance company.

## When to Use
- Before modifying tables, columns, procedures, functions, views, triggers
- Evaluating migration/patch deployment risk
- Finding dependencies between database objects in SQL files

## Large Repository Search Strategy

> ⚠️ This is a large repository. Always constrain searches to avoid timeouts.

### Module-Scoped Searching

**ALWAYS use `includePattern` to limit search scope:**

| If analyzing... | Use includePattern |
|-----------------|-------------------|
| Claims objects | `patches/claims/**/*.sql` |
| Policies objects | `patches/policies/**/*.sql` |
| Payments objects | `patches/payments/**/*.sql` |
| Shared utilities | `patches/shared/**/*.sql` |
| Cross-module | `patches/{module1,module2}/**/*.sql` |

**Search Order (narrow → wide):**
1. **Same module first**: Search within the object's module
2. **Shared second**: Search `patches/shared/**/*.sql`
3. **Dependent modules**: Based on module dependencies
4. **Never search root**: Avoid `**/*.sql` on full repo

### Example Constrained Search

```
# GOOD - Scoped to module
grep_search: "FROM\s+claim"
isRegexp: true
includePattern: "patches/claims/**/*.sql"

# BAD - Too broad, will timeout
grep_search: "FROM\s+claim"
isRegexp: true
includePattern: "**/*.sql"
```

### Semantic Search Limitations

> ⚠️ Semantic search may not be indexed for large repos (>2,500 files).
> Prefer `grep_search` with patterns from reference files.

### grep_search Limitations

> ⚠️ `grep_search` has hard limits: **200 matches max**, **20-second timeout**.
> See `#file:research/grep-search-limitations.md` for details.
> Use `#skill:python-grep-search` when limit hit (returns exactly 200 results).

---

## Quick Reference - Load the Right File

Based on the change type, load the appropriate reference file:

### Table/Column Changes

| Change Type | Reference File |
|-------------|----------------|
| Add column | [tables/add-column.md](./references/tables/add-column.md) |
| Modify column (type, constraints) | [tables/modify-column.md](./references/tables/modify-column.md) |
| Drop column | [tables/drop-column.md](./references/tables/drop-column.md) |
| Rename column | [tables/rename-column.md](./references/tables/rename-column.md) |
| Add table | [tables/add-table.md](./references/tables/add-table.md) |
| Drop table | [tables/drop-table.md](./references/tables/drop-table.md) |

### Database Objects

| Object Type | Reference File |
|-------------|----------------|
| Procedures | [procedures/patterns.md](./references/procedures/patterns.md) |
| Functions | [functions/patterns.md](./references/functions/patterns.md) |
| Triggers | [triggers/patterns.md](./references/triggers/patterns.md) |
| Views | [views/patterns.md](./references/views/patterns.md) |
| Indexes | [indexes/patterns.md](./references/indexes/patterns.md) |
| Sequences | [sequences/patterns.md](./references/sequences/patterns.md) |

### Patch Management

| Task | Reference File |
|------|----------------|
| Patch ordering & dependencies | [patches/ordering.md](./references/patches/ordering.md) |

### Always Load
- [severity-criteria.md](./references/severity-criteria.md) - Impact classification and scoring

---

## Procedure

### 1. Identify Change Type

Ask the user:
- **Object type**: table, column, procedure, function, view, trigger, index?
- **Operation**: add, modify, drop, rename?
- **Specific object**: name of table/column/procedure being changed?

### 2. Load Relevant Reference File

Based on change type, read the appropriate reference file from the table above.

### 3. Run Searches

Using patterns from the reference file:

**Step 3a: Determine Module Scope**

Identify which module the object belongs to:
- Claims module: `includePattern: "patches/claims/**/*.sql"`
- Policies module: `includePattern: "patches/policies/**/*.sql"`
- Payments module: `includePattern: "patches/payments/**/*.sql"`
- Shared module: `includePattern: "patches/shared/**/*.sql"`
- Unknown: Ask user which module

**Step 3b: Direct Pattern Search (Scoped)**
```
grep_search with isRegexp: true
includePattern: "patches/{MODULE}/**/*.sql"
```

**Step 3c: Expand to Shared (if needed)**
```
grep_search with isRegexp: true
includePattern: "patches/shared/**/*.sql"
```

**Step 3d: Semantic Search (Optional)**
> Only if repo is indexed (<2,500 files)
```
semantic_search: "SQL that uses {OBJECT}"
```

### 4. Assess Severity

Load and apply [severity-criteria.md](./references/severity-criteria.md):
- Calculate base score from change type
- Add modifiers based on findings
- Determine severity level

### 5. Generate Report

> **This is the canonical output format.** All entry points (agent, prompts) must produce this format.

---

## Risk Classification

> **Not all dependencies are risks.** Classification depends on change type.

### Risk Levels

| Level | Icon | Meaning | Action Required |
|-------|------|---------|----------------|
| **Risk** | 🔴 | Will break, fail, or cause data issues | Must fix before change |
| **Review** | 🟡 | May be affected, needs human judgment | Review and decide |
| **Safe** | 🟢 | Found reference, no impact for this change | Informational only |

### Risk by Change Type

Load the appropriate reference file - each contains detailed risk classification:

| Change Type | 🔴 Risk (Will Break) | 🟡 Review | 🟢 Safe |
|-------------|---------------------|-----------|--------|
| **Add Column** | `INSERT VALUES` (no cols) | `SELECT *`, Views | Explicit `INSERT (cols)` |
| **Drop Column** | All explicit refs | `SELECT *` | Comments only |
| **Rename Column** | All old name refs | `SELECT *` | Aliases, comments |
| **Modify Column** | Type mismatches | Size-sensitive ops | Same-type widens |

---

## Output Format (Canonical)

### Markdown Summary Template

```markdown
## Impact Analysis: {OBJECT_NAME}

### Summary
| Metric | Value |
|--------|-------|
| **Object** | {table.column or object name} |
| **Change Type** | {add/modify/drop/rename} |
| **Module** | {owning module} |
| **Severity** | {🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low} |
| **Total Matches** | {count} |
| **🔴 Risks** | {count - will break} |
| **🟡 Review** | {count - needs review} |
| **🟢 Safe** | {count - informational} |
| **Search Scope** | {module / module+shared / cross-module} |
| **Analysis Date** | {YYYY-MM-DD} |

### 🔴 Risks ({count}) - Must Address Before Change

| File | Line | Type | Why Risk | Snippet |
|------|------|------|----------|---------|
| {path} | {line} | {type} | {reason} | {excerpt} |

### 🟡 Review ({count}) - Needs Human Assessment

| File | Line | Type | Pattern | Snippet |
|------|------|------|---------|---------|
| {path} | {line} | {type} | {pattern} | {excerpt} |

### Risk Factors
- {factor 1}
- {factor 2}

### Severity Score
- Base ({change type}): +{n}
- 🔴 Risks ({count} × 3): +{n}
- 🟡 Reviews ({count} × 1): +{n}
- Critical table modifier: +{n}
- **Total: {score} → {Severity Level}**

### Recommendations
- {action items based on risks found}
```

### CSV Format

```csv
file_path,line_number,match_type,risk_level,pattern_matched,code_snippet
{path},{line},{proc|trigger|view|direct},{Risk|Review|Safe},{pattern},{snippet (60 char max)}
```

### Metadata JSON Format

```json
{
  "change_id": "{object}-{operation}-{YYYY-MM-DD}",
  "object_name": "{name}",
  "change_type": "{add|modify|drop|rename}",
  "owning_module": "{module}",
  "severity": "{Critical|High|Medium|Low}",
  "severity_score": {number},
  "total_matches": {count},
  "risk_count": {count},
  "review_count": {count},
  "safe_count": {count},
  "search_scope": ["{module1}", "{module2}"],
  "search_type": "{grep_search|comprehensive}",
  "analysis_date": "{YYYY-MM-DD}"
}
```

---

## Decision Tree

```
What are you changing?
│
├─► TABLE structure
│   ├─► Adding column      → load tables/add-column.md
│   ├─► Modifying column   → load tables/modify-column.md
│   ├─► Dropping column    → load tables/drop-column.md
│   ├─► Renaming column    → load tables/rename-column.md
│   ├─► Adding table       → load tables/add-table.md
│   └─► Dropping table     → load tables/drop-table.md
│
├─► PROCEDURE
│   └─► Any change         → load procedures/patterns.md
│
├─► FUNCTION
│   └─► Any change         → load functions/patterns.md
│
├─► TRIGGER
│   └─► Any change         → load triggers/patterns.md
│
├─► VIEW
│   └─► Any change         → load views/patterns.md
│
├─► INDEX
│   └─► Any change         → load indexes/patterns.md
│
└─► PATCH deployment
    └─► Ordering/deps      → load patches/ordering.md
```
