# Trigger Dependency Patterns

## Finding Trigger Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+(OR\s+REPLACE\s+)?TRIGGER\s+(\w+\.)?{TRIGGER}` | Create/replace |
| `ALTER\s+TRIGGER\s+(\w+\.)?{TRIGGER}` | Alter trigger |
| `DROP\s+TRIGGER\s+(\w+\.)?{TRIGGER}` | Drop trigger |
| `(ENABLE\|DISABLE)\s+(ALL\s+)?TRIGGER(S)?\s+.*{TRIGGER}` | Enable/disable |

## Finding Triggers ON a Table

| Pattern | Description |
|---------|-------------|
| `TRIGGER\s+\w+\s+ON\s+(\w+\.)?{TABLE}` | Trigger on table |
| `(BEFORE\|AFTER\|INSTEAD\s+OF)\s+.*ON\s+(\w+\.)?{TABLE}` | With timing |
| `CREATE.*TRIGGER.*ON\s+(\w+\.)?{TABLE}` | Any trigger on table |
| `FOR\s+(INSERT\|UPDATE\|DELETE).*ON\s+.*{TABLE}` | DML triggers |

## Trigger Timing Keywords

| Pattern | When It Fires |
|---------|---------------|
| `BEFORE\s+(INSERT\|UPDATE\|DELETE)` | Before the DML |
| `AFTER\s+(INSERT\|UPDATE\|DELETE)` | After the DML |
| `INSTEAD\s+OF\s+(INSERT\|UPDATE\|DELETE)` | Replaces the DML |
| `FOR\s+(INSERT\|UPDATE\|DELETE)` | SQL Server syntax |

## Trigger Events

| Pattern | Event |
|---------|-------|
| `INSERT` | Row inserted |
| `UPDATE` | Row updated |
| `UPDATE\s+OF\s+{COLUMN}` | Specific column updated |
| `DELETE` | Row deleted |
| `TRUNCATE` | Table truncated (PostgreSQL) |

## Search Strategy

### Find All Triggers on a Table

```
# Step 1: Find trigger definitions on the table
grep_search: "TRIGGER.*ON\s+(\w+\.)?{TABLE}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find triggers with specific timing
grep_search: "(BEFORE|AFTER|INSTEAD\s+OF|FOR)\s+.*ON\s+(\w+\.)?{TABLE}"
isRegexp: true

# Step 3: Find column-specific triggers
grep_search: "UPDATE\s+OF\s+.*ON\s+(\w+\.)?{TABLE}"
isRegexp: true
```

### Find What a Trigger Does

Read the trigger body and search for:

```
# Tables modified by trigger
grep_search: "(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+\w+"

# Procedures called
grep_search: "(EXEC|CALL)\s+\w+"

# Functions called
grep_search: "\w+\s*\("
```

### Find Triggers Referencing a Column

```
# If changing a column, find triggers that use it
grep_search: "TRIGGER[\s\S]*?{TABLE}[\s\S]*?\b{COLUMN}\b"
isRegexp: true
```

## Trigger Types and Purposes

| Type | Common Use |
|------|------------|
| Audit trigger | Log changes to audit table |
| Cascade trigger | Update/delete related records |
| Validation trigger | Enforce business rules |
| Computed trigger | Calculate derived values |
| Sync trigger | Keep related data in sync |
| History trigger | Maintain history/versioning |

## Severity Factors

| Factor | Score |
|--------|-------|
| Audit trigger (compliance) | +4 |
| Cascade trigger (modifies other tables) | +5 |
| Validation trigger (business rules) | +3 |
| Trigger calls procedures | +2 per procedure |
| Trigger modifies other tables | +3 per table |
| Multiple triggers on same event | +2 (ordering issues) |
| INSTEAD OF trigger | +4 (replaces DML entirely) |

## Impact of Table Changes on Triggers

### Column Added
- Trigger may not be affected
- Check if trigger uses `SELECT *` or `NEW.*`

### Column Modified
- Check if trigger references the column
- Type change may break trigger logic

### Column Dropped
- **Breaking** if trigger references the column
- Must update trigger before dropping

### Column Renamed
- **Breaking** if trigger references old name
- Must update trigger before renaming

## Search for Column Usage in Triggers

```
# Find triggers that might use a column
grep_search: "TRIGGER[\s\S]*?ON\s+(\w+\.)?{TABLE}[\s\S]*?\b{COLUMN}\b"
isRegexp: true

# Check for NEW/OLD references (row-level triggers)
grep_search: "(NEW|OLD)\.{COLUMN}"
isRegexp: true

# Check for :NEW/:OLD references (Oracle)
grep_search: ":(NEW|OLD)\.{COLUMN}"
isRegexp: true
```

## Pre-Change Checklist

### When Modifying a Trigger
- [ ] What table is it on?
- [ ] What event (INSERT/UPDATE/DELETE)?
- [ ] What does it do currently?
- [ ] Any other triggers on same table/event?
- [ ] Trigger firing order matter?

### When Modifying a Table with Triggers
- [ ] What triggers exist on this table?
- [ ] Do any triggers reference the column being changed?
- [ ] Will trigger still compile after change?
- [ ] Will trigger behavior be affected?

## Trigger Ordering Issues

Multiple triggers on same event can cause problems:

```sql
-- Oracle: Triggers fire in undefined order unless specified
-- SQL Server: sp_settriggerorder to control

-- Check for multiple triggers on same table/event
grep_search: "(BEFORE|AFTER|FOR)\s+INSERT\s+ON\s+{TABLE}"
```

## Common Issues

### Issue: Trigger Uses Dropped Column
```sql
-- Trigger references email column
CREATE TRIGGER audit_changes ON users
AFTER UPDATE AS
  INSERT INTO audit (old_email) VALUES (OLD.email);

-- If you drop email column, trigger fails!
```

### Issue: Trigger Type Mismatch
```sql
-- Trigger expects INT
CREATE TRIGGER calc ON orders
AFTER INSERT AS
  UPDATE orders SET total = NEW.quantity * NEW.price;

-- If you change quantity from INT to DECIMAL, may have issues
```

### Issue: Cascade Loop
```sql
-- Trigger A updates table B
-- Trigger B updates table A
-- Infinite loop!
```

## Migration Strategy

When changing a table with triggers:

1. **Document all triggers** on the table
2. **Disable triggers** temporarily (if needed)
3. **Make table changes**
4. **Update trigger code** if needed
5. **Re-enable triggers**
6. **Test trigger behavior**

```sql
-- Disable triggers during migration
DISABLE TRIGGER ALL ON {TABLE};

-- Make changes...

-- Re-enable
ENABLE TRIGGER ALL ON {TABLE};
```
