# Sequence Dependency Patterns

## Finding Sequence Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+SEQUENCE\s+(\w+\.)?{SEQ}` | Create sequence |
| `ALTER\s+SEQUENCE\s+(\w+\.)?{SEQ}` | Alter sequence |
| `DROP\s+SEQUENCE\s+(\w+\.)?{SEQ}` | Drop sequence |

## Finding Sequence Usage

### Oracle Syntax

| Pattern | Description |
|---------|-------------|
| `{SEQ}\.NEXTVAL` | Get next value |
| `{SEQ}\.CURRVAL` | Get current value |
| `(\w+\.)?{SEQ}\.NEXTVAL` | Schema-qualified |

### PostgreSQL Syntax

| Pattern | Description |
|---------|-------------|
| `NEXTVAL\s*\(\s*'{SEQ}'` | Get next value |
| `CURRVAL\s*\(\s*'{SEQ}'` | Get current value |
| `SETVAL\s*\(\s*'{SEQ}'` | Set value |
| `LASTVAL\s*\(\s*\)` | Get last value (any sequence) |

### SQL Server (IDENTITY alternative)

| Pattern | Description |
|---------|-------------|
| `NEXT\s+VALUE\s+FOR\s+(\w+\.)?{SEQ}` | Get next value |

### In Default Values

| Pattern | Description |
|---------|-------------|
| `DEFAULT\s+.*{SEQ}\.NEXTVAL` | Oracle default |
| `DEFAULT\s+NEXTVAL\s*\(\s*'{SEQ}'` | PostgreSQL default |
| `DEFAULT\s+NEXT\s+VALUE\s+FOR\s+{SEQ}` | SQL Server default |

## Search Strategy

### Find All Sequence Usage

```
# Step 1: Oracle NEXTVAL/CURRVAL
grep_search: "{SEQ}\.(NEXTVAL|CURRVAL)"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: PostgreSQL functions
grep_search: "(NEXTVAL|CURRVAL|SETVAL)\s*\(\s*'{SEQ}'"
isRegexp: true

# Step 3: SQL Server
grep_search: "NEXT\s+VALUE\s+FOR\s+(\w+\.)?{SEQ}"
isRegexp: true

# Step 4: In default constraints
grep_search: "DEFAULT.*{SEQ}"
isRegexp: true
```

### Find Tables Using a Sequence

```
# Find tables with sequence in default
grep_search: "CREATE\s+TABLE[\s\S]*?{SEQ}"
isRegexp: true

# Find INSERT statements using sequence
grep_search: "INSERT[\s\S]*?{SEQ}\.(NEXTVAL|CURRVAL)"
isRegexp: true
```

## Sequence Usage Contexts

| Context | Example |
|---------|---------|
| Column default | `id INT DEFAULT seq.NEXTVAL` |
| INSERT statement | `INSERT INTO t (id) VALUES (seq.NEXTVAL)` |
| Procedure | `v_id := seq.NEXTVAL;` |
| Trigger | `NEW.id := seq.NEXTVAL;` |

## Severity Factors

| Factor | Score |
|--------|-------|
| Used for PRIMARY KEY | +4 (identity mechanism) |
| Used in multiple tables | +2 per table |
| Used in procedures | +2 per procedure |
| Has specific increment/start values | +1 |
| Cycling sequence | +1 (wrap-around logic) |
| Referenced in default constraints | +3 |

## Impact of Sequence Changes

### Changing INCREMENT
- Future values spaced differently
- May affect batch processing assumptions

### Changing MAXVALUE
- Sequence may stop working when reached
- Or cycle if CYCLE enabled

### Changing START/RESTART
- Doesn't affect existing data
- Only affects new values

### Dropping Sequence
- **Breaking** - all references fail
- Must update/remove references first

## Pre-Change Checklist

- [ ] Which tables use this sequence?
- [ ] Which procedures use this sequence?
- [ ] Is it embedded in column defaults?
- [ ] What is the current value?
- [ ] Will the change cause conflicts (duplicate IDs)?
- [ ] Any code depends on specific increment?

## Common Issues

### Issue: Sequence in Column Default
```sql
-- Column default uses sequence
CREATE TABLE orders (
  id INT DEFAULT order_seq.NEXTVAL PRIMARY KEY
);

-- Dropping sequence breaks table!
DROP SEQUENCE order_seq;  -- INSERT will fail!
```

### Issue: Gap Assumptions
```sql
-- Code assumes no gaps in sequence
SELECT * FROM t WHERE id BETWEEN seq.CURRVAL - 100 AND seq.CURRVAL;

-- But sequences can have gaps from rollbacks!
```

### Issue: Sequence Not Owned by Table
```sql
-- PostgreSQL: Sequence not tied to table
CREATE SEQUENCE my_seq;
CREATE TABLE t (id INT DEFAULT NEXTVAL('my_seq'));

-- Dropping table doesn't drop sequence
DROP TABLE t;
-- my_seq still exists, orphaned
```

## Migration Strategies

### Changing Sequence Properties
```sql
-- Usually safe, affects future values only
ALTER SEQUENCE {SEQ} INCREMENT BY 10;
ALTER SEQUENCE {SEQ} MAXVALUE 1000000;
```

### Dropping a Sequence
```sql
-- Step 1: Find all usages
grep_search: "{SEQ}"

-- Step 2: Remove from column defaults
ALTER TABLE t ALTER COLUMN id DROP DEFAULT;

-- Step 3: Update procedures to use different approach

-- Step 4: Drop sequence
DROP SEQUENCE {SEQ};
```

### Renaming a Sequence
```sql
-- Step 1: Find all usages (must update all!)
grep_search: "{OLD_SEQ}"

-- Step 2: Rename (or create new + migrate)
ALTER SEQUENCE {OLD_SEQ} RENAME TO {NEW_SEQ};
-- OR
CREATE SEQUENCE {NEW_SEQ} START WITH <current_value>;

-- Step 3: Update all references
-- Step 4: Drop old sequence (if created new)
```

## Auto-Generated Sequences

Some databases auto-create sequences:

```sql
-- PostgreSQL SERIAL creates a sequence
CREATE TABLE t (id SERIAL PRIMARY KEY);
-- Creates: t_id_seq

-- These are "owned" by the column
-- Dropping the table drops the sequence
```

Find auto-generated sequences:
```
grep_search: "_seq\b"
isRegexp: true
```
