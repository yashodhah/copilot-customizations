---
name: sql-impact-analysis
description: 'Analyze database schema changes for impact and risk. Use for: SQL dependency mapping, finding affected queries/procedures/views/triggers, assessing change severity, identifying breaking changes before deployment, database migration and patch risk assessment.'
---

# SQL Impact Analysis

## When to Use
- Before modifying tables, columns, procedures, functions, views, triggers
- Evaluating migration/patch deployment risk
- Finding dependencies between database objects in SQL files

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

**Step 3a: Direct Pattern Search**
```
grep_search with isRegexp: true
includePattern: "**/*.sql"
```

**Step 3b: Semantic Search**
```
semantic_search: "SQL that uses {OBJECT}"
```

### 4. Assess Severity

Load and apply [severity-criteria.md](./references/severity-criteria.md):
- Calculate base score from change type
- Add modifiers based on findings
- Determine severity level

### 5. Generate Report

Output in BOTH formats:

#### Markdown Summary
```markdown
## Impact Analysis: {OBJECT_NAME}

### Summary
| Metric | Value |
|--------|-------|
| **Object** | {name} |
| **Change Type** | {type} |
| **Severity** | {🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low} |
| **Files Affected** | {count} |

### Dependencies Found
| File | Line | Type | Pattern | Snippet |
|------|------|------|---------|---------|

### Risk Factors
- {factors}

### Recommendations
- {actions}
```

#### CSV Data
```csv
file_path,line_number,match_type,pattern_matched,code_snippet,severity_contribution
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
