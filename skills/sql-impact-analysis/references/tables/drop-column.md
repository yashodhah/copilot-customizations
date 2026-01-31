# Drop Column Impact Analysis

## Risk Level
🔴 **High risk** - Data loss is irreversible

## Key Concerns

| Concern | Impact |
|---------|--------|
| Data loss | Permanent - cannot recover without backup |
| Breaking queries | SELECT, INSERT, UPDATE referencing column will fail |
| Breaking procedures | Stored procedures using column will error |
| Breaking views | Views selecting column will become invalid |
| Index removal | Indexes containing column will be dropped |
| Constraint removal | Constraints on column will be dropped |

## Patterns to Search

### Direct Column References

| Pattern | Description |
|---------|-------------|
| `{TABLE}\.{COLUMN}` | Qualified column reference |
| `SELECT\s+.*\b{COLUMN}\b` | Column in SELECT (use word boundaries) |
| `WHERE\s+.*\b{COLUMN}\b` | Column in WHERE clause |
| `ORDER\s+BY\s+.*\b{COLUMN}\b` | Column in ORDER BY |
| `GROUP\s+BY\s+.*\b{COLUMN}\b` | Column in GROUP BY |
| `HAVING\s+.*\b{COLUMN}\b` | Column in HAVING |
| `SET\s+{COLUMN}\s*=` | Column in UPDATE SET |
| `INSERT\s+INTO\s+{TABLE}\s*\([^)]*\b{COLUMN}\b` | Column in INSERT column list |

### Index References

| Pattern | Description |
|---------|-------------|
| `CREATE\s+.*INDEX.*\(.*\b{COLUMN}\b` | Index includes column |
| `INDEX.*ON\s+.*{TABLE}.*\b{COLUMN}\b` | Index on table with column |

### Constraint References

| Pattern | Description |
|---------|-------------|
| `CONSTRAINT.*\b{COLUMN}\b` | Named constraints |
| `CHECK\s*\(.*\b{COLUMN}\b` | Check constraints |
| `DEFAULT\s+.*FOR\s+.*\b{COLUMN}\b` | Default constraints |
| `FOREIGN\s+KEY\s*\(.*\b{COLUMN}\b` | FK constraint (this table) |
| `REFERENCES\s+{TABLE}\s*\(.*\b{COLUMN}\b` | FK reference (other tables!) |

### View References

| Pattern | Description |
|---------|-------------|
| `CREATE.*VIEW[\s\S]*?SELECT.*\b{COLUMN}\b[\s\S]*?FROM.*{TABLE}` | Column in view definition |

### Procedure/Function References

| Pattern | Description |
|---------|-------------|
| `(PROCEDURE\|FUNCTION)[\s\S]*?\b{COLUMN}\b` | Column used in proc/func |

### Search Strategy

```
# Step 1: Find qualified references (most reliable)
grep_search: "{TABLE}\.{COLUMN}"
isRegexp: false
includePattern: "**/*.sql"

# Step 2: Find in SELECT statements
grep_search: "SELECT\s+.*\b{COLUMN}\b.*FROM.*{TABLE}"
isRegexp: true

# Step 3: Find in WHERE clauses
grep_search: "WHERE.*\b{COLUMN}\b"
isRegexp: true

# Step 4: Find in UPDATE statements
grep_search: "SET\s+{COLUMN}\s*="
isRegexp: true

# Step 5: Find in constraints (including FK references from other tables!)
grep_search: "REFERENCES\s+{TABLE}\s*\(.*{COLUMN}"
isRegexp: true

# Step 6: Find in indexes
grep_search: "INDEX.*{COLUMN}"
isRegexp: true

# Step 7: Semantic search for broader context
semantic_search: "SQL using {COLUMN} column from {TABLE} table"
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Column is PRIMARY KEY | +10 (Critical - cannot drop) |
| Column is FOREIGN KEY | +5 |
| Column is FK target (other tables reference it) | +10 (Critical) |
| Column in indexes | +2 |
| Column in views | +3 per view |
| Column in procedures | +2 per procedure |
| Column in WHERE clauses | +2 |
| Column has data | +2 |
| 10+ references found | +5 (Critical) |
| 5-10 references found | +3 |

## Pre-Drop Checklist

- [ ] Is this column part of PRIMARY KEY? (Cannot drop if yes)
- [ ] Is this column a FOREIGN KEY? (Must drop FK first)
- [ ] Do other tables have FK references to this column? (Critical!)
- [ ] Data backed up or no longer needed?
- [ ] All referencing views identified and updated?
- [ ] All referencing procedures identified and updated?
- [ ] All referencing application code updated?
- [ ] Indexes on this column will be automatically dropped?
- [ ] Constraints on this column will be automatically dropped?

## Migration Strategy

### Safe Drop Sequence

1. **Identify all dependencies** (run this analysis)
2. **Backup the column data** if needed
3. **Drop foreign keys** referencing this column (other tables)
4. **Update/drop views** that use the column
5. **Update procedures** that reference the column
6. **Drop indexes** that include the column (or let them auto-drop)
7. **Drop constraints** on the column
8. **Drop the column**

### Rollback Considerations

- Once dropped, column and data are gone
- Must restore from backup to recover
- Consider renaming instead of dropping (safer)

## Alternative: Soft Delete

Instead of dropping, consider:

```sql
-- Rename to mark as deprecated
ALTER TABLE {TABLE} RENAME COLUMN {COLUMN} TO {COLUMN}_deprecated;

-- Or add comment
COMMENT ON COLUMN {TABLE}.{COLUMN} IS 'DEPRECATED - Do not use. To be removed in v2.0';
```
