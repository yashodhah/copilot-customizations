---
name: sql-impact-analysis
description: 'Analyze database schema changes for impact and risk. Use for: SQL dependency mapping, finding affected queries/procedures/views, assessing change severity, identifying breaking changes before deployment, database migration risk assessment.'
---

# SQL Impact Analysis

## When to Use
- Before modifying table schemas (add/drop/rename columns)
- Before changing stored procedures or views
- Evaluating migration risk
- Identifying downstream dependencies
- Assessing breaking changes in database refactoring

## Procedure

### 1. Gather Change Details
Ask the user for:
- Table/column/object being changed
- Type of change (add, modify, drop, rename)
- Target environment (prod, staging, dev)

### 2. Search for Dependencies
Use the patterns in [regex-patterns.md](./references/regex-patterns.md) to search the codebase:

**Step 2a: Direct SQL Pattern Search**
Run `grep_search` with relevant patterns for the object type:
- For tables: `FROM\s+{TABLE}|JOIN\s+{TABLE}|INTO\s+{TABLE}|UPDATE\s+{TABLE}`
- For columns: `{TABLE}\.{COLUMN}|SELECT.*{COLUMN}|WHERE.*{COLUMN}`
- Include file patterns: `*.sql`, `*.py`, `*.java`, `*.ts`, `*.js`, `*.cs`

**Step 2b: Semantic Search**
Run `semantic_search` for conceptual matches:
- Query: "code that uses {TABLE} table" or "queries {COLUMN} column"
- This catches ORM usage, dynamic queries, and indirect references

**Step 2c: Combine Results**
- Deduplicate findings by file + line number
- Categorize as "direct" (regex) or "semantic" (conceptual)

### 3. Classify Impact Severity
Apply criteria from [severity-criteria.md](./references/severity-criteria.md):
- Count affected files and categorize by type
- Check for critical table markers
- Assess rollback complexity
- Calculate severity score

### 4. Generate Report
Output structured findings in BOTH markdown and CSV formats:

---

## Output Templates

### Markdown Report

```markdown
## Impact Analysis: [Object Name]

### Summary
- **Change Type**: [add/modify/drop/rename]
- **Severity**: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low
- **Files Affected**: [count]
- **Analysis Date**: [YYYY-MM-DD]

### Dependencies Found

| File | Line | Type | Pattern | Snippet |
|------|------|------|---------|---------|
| path/to/file.sql | 42 | direct | FROM table | SELECT * FROM... |

### Risk Factors
- [List factors that contributed to severity rating]

### Recommendations
- [Actionable next steps based on severity]
```

### CSV Report (for Excel/spreadsheet import)

```csv
file_path,line_number,match_type,pattern_matched,code_snippet,severity_contribution
```

### Summary CSV

```csv
metric,value
object_name,[name]
change_type,[type]
severity,[level]
total_files_affected,[count]
direct_matches,[count]
semantic_matches,[count]
critical_factors,[list]
analysis_date,[date]
```
