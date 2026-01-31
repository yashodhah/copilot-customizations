# Rename Column Impact Analysis

## Risk Level
🟠 **High risk** - All references must be updated simultaneously

## Key Concerns

| Concern | Impact |
|---------|--------|
| Breaking queries | All references use old name |
| Deployment coordination | Code and DB must change together |
| No gradual migration | Unlike add/drop, rename is atomic |
| Case sensitivity | Some databases are case-sensitive |

## Patterns to Search

### All Column References

| Pattern | Description |
|---------|-------------|
| `{TABLE}\.{OLD_COLUMN}` | Qualified reference |
| `\b{OLD_COLUMN}\b` | Unqualified reference (more false positives) |
| `SELECT\s+.*\b{OLD_COLUMN}\b` | In SELECT list |
| `WHERE\s+.*\b{OLD_COLUMN}\b` | In WHERE clause |
| `SET\s+{OLD_COLUMN}\s*=` | In UPDATE SET |
| `ORDER\s+BY\s+.*\b{OLD_COLUMN}\b` | In ORDER BY |
| `GROUP\s+BY\s+.*\b{OLD_COLUMN}\b` | In GROUP BY |
| `INSERT.*\(\s*.*\b{OLD_COLUMN}\b` | In INSERT column list |
| `ON\s+.*\b{OLD_COLUMN}\b\s*=` | In JOIN condition |

### Aliases (May Hide References)

| Pattern | Description |
|---------|-------------|
| `AS\s+{OLD_COLUMN}` | Column alias (output name) |
| `{OLD_COLUMN}\s+AS\s+` | Column being aliased |

### Index and Constraint References

| Pattern | Description |
|---------|-------------|
| `INDEX.*\b{OLD_COLUMN}\b` | In index definition |
| `CONSTRAINT.*\b{OLD_COLUMN}\b` | In constraint |
| `REFERENCES.*\(.*{OLD_COLUMN}` | FK references |

### Comments and Documentation

| Pattern | Description |
|---------|-------------|
| `COMMENT\s+ON\s+COLUMN.*{OLD_COLUMN}` | Column comments |
| `--.*{OLD_COLUMN}` | SQL comments mentioning column |

### Search Strategy

```
# Step 1: Find qualified references (most reliable)
grep_search: "{TABLE}\.{OLD_COLUMN}"
isRegexp: false
includePattern: "**/*.sql"

# Step 2: Find all occurrences of column name
grep_search: "\b{OLD_COLUMN}\b"
isRegexp: true
includePattern: "**/*.sql"

# Step 3: Find in index definitions
grep_search: "INDEX.*{OLD_COLUMN}"
isRegexp: true

# Step 4: Find in constraints
grep_search: "(CONSTRAINT|REFERENCES|FOREIGN\s+KEY).*{OLD_COLUMN}"
isRegexp: true

# Step 5: Semantic search
semantic_search: "SQL referencing {OLD_COLUMN} in {TABLE}"
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Column is PRIMARY KEY | +5 (many references) |
| Column is FOREIGN KEY | +4 |
| FK references from other tables | +5 (must update those too!) |
| In indexes | +2 |
| 20+ references found | +5 (Critical) |
| 10-20 references found | +3 |
| 5-10 references found | +2 |
| Used in views | +2 per view |
| Used in procedures | +2 per procedure |

## Pre-Rename Checklist

- [ ] All SQL file references identified?
- [ ] All view definitions will be updated?
- [ ] All procedure/function references will be updated?
- [ ] All index definitions accounted for?
- [ ] Constraints will auto-update or need recreation?
- [ ] FK references from other tables identified?
- [ ] Deployment can update DB and code atomically?

## Migration Strategies

### Strategy 1: Atomic Rename (Simple but Risky)

```sql
-- Single statement, all-or-nothing
ALTER TABLE {TABLE} RENAME COLUMN {OLD_COLUMN} TO {NEW_COLUMN};
```

**Risk**: All code must be deployed simultaneously.

### Strategy 2: Add-Migrate-Drop (Safer)

```sql
-- Step 1: Add new column
ALTER TABLE {TABLE} ADD {NEW_COLUMN} <type>;

-- Step 2: Copy data
UPDATE {TABLE} SET {NEW_COLUMN} = {OLD_COLUMN};

-- Step 3: Update code to use new column (can be gradual)

-- Step 4: Add trigger to sync during migration
CREATE TRIGGER sync_{OLD_COLUMN}
AFTER INSERT OR UPDATE ON {TABLE}
FOR EACH ROW
BEGIN
  NEW.{NEW_COLUMN} = NEW.{OLD_COLUMN};
  NEW.{OLD_COLUMN} = NEW.{NEW_COLUMN};
END;

-- Step 5: Once all code updated, drop old column
ALTER TABLE {TABLE} DROP COLUMN {OLD_COLUMN};
```

**Benefit**: Allows gradual code migration.

### Strategy 3: View Abstraction

```sql
-- Create view with new column name
CREATE VIEW {TABLE}_v2 AS
SELECT *, {OLD_COLUMN} AS {NEW_COLUMN}
FROM {TABLE};

-- Migrate code to use view
-- Later rename actual column and update view
```

## Files to Update

After identifying all references, create a list:

| File | Line | Current Code | Updated Code |
|------|------|--------------|--------------|
| | | `{OLD_COLUMN}` | `{NEW_COLUMN}` |

This list becomes your deployment checklist.
