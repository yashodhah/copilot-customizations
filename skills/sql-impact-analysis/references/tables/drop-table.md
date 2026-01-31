# Drop Table Impact Analysis

## Risk Level
🔴 **Critical risk** - All data and dependent objects will be lost

## Key Concerns

| Concern | Impact |
|---------|--------|
| Data loss | All rows permanently deleted |
| FK constraints | Other tables referencing this will fail/block |
| Views | Views using this table become invalid |
| Procedures | Procedures querying this table will error |
| Triggers | Triggers on this table will be dropped |
| Indexes | All indexes on this table will be dropped |
| Sequences | Associated sequences may become orphaned |

## Patterns to Search

### Direct Table References

| Pattern | Description |
|---------|-------------|
| `FROM\s+(\w+\.)?{TABLE}(\s\|$\|,\|;)` | SELECT from table |
| `JOIN\s+(\w+\.)?{TABLE}(\s\|ON)` | JOIN with table |
| `INTO\s+(\w+\.)?{TABLE}` | INSERT into table |
| `UPDATE\s+(\w+\.)?{TABLE}` | UPDATE table |
| `DELETE\s+(FROM\s+)?(\w+\.)?{TABLE}` | DELETE from table |
| `TRUNCATE\s+.*{TABLE}` | TRUNCATE table |
| `MERGE\s+INTO\s+(\w+\.)?{TABLE}` | MERGE into table |

### Foreign Key References (CRITICAL)

| Pattern | Description |
|---------|-------------|
| `REFERENCES\s+(\w+\.)?{TABLE}` | Other tables with FK to this table |
| `FOREIGN\s+KEY.*REFERENCES\s+(\w+\.)?{TABLE}` | Explicit FK syntax |

### View Dependencies

| Pattern | Description |
|---------|-------------|
| `CREATE.*VIEW[\s\S]*?FROM\s+(\w+\.)?{TABLE}` | Views querying this table |
| `CREATE.*VIEW[\s\S]*?JOIN\s+(\w+\.)?{TABLE}` | Views joining this table |

### Procedure/Function Dependencies

| Pattern | Description |
|---------|-------------|
| `(PROCEDURE\|FUNCTION)[\s\S]*?FROM\s+(\w+\.)?{TABLE}` | Procs selecting from table |
| `(PROCEDURE\|FUNCTION)[\s\S]*?(INTO\|UPDATE\|DELETE).*{TABLE}` | Procs modifying table |

### Trigger Dependencies

| Pattern | Description |
|---------|-------------|
| `TRIGGER.*ON\s+(\w+\.)?{TABLE}` | Triggers on this table |

### Synonym/Alias References

| Pattern | Description |
|---------|-------------|
| `SYNONYM.*FOR\s+(\w+\.)?{TABLE}` | Synonyms pointing to this table |

### Search Strategy

```
# Step 1: Find all DML references
grep_search: "(FROM|JOIN|INTO|UPDATE|DELETE)\s+(\w+\.)?{TABLE}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find FK references (CRITICAL - blocks drop!)
grep_search: "REFERENCES\s+(\w+\.)?{TABLE}"
isRegexp: true

# Step 3: Find views using this table
grep_search: "CREATE.*VIEW[\s\S]*?{TABLE}"
isRegexp: true

# Step 4: Find triggers on this table
grep_search: "TRIGGER.*ON\s+(\w+\.)?{TABLE}"
isRegexp: true

# Step 5: Find procedures referencing this table
grep_search: "(PROCEDURE|FUNCTION)[\s\S]*?{TABLE}"
isRegexp: true

# Step 6: Semantic search
semantic_search: "SQL that uses {TABLE} table"
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Other tables have FK to this table | +10 (Critical - blocks drop) |
| Table has data | +3 |
| Views depend on this table | +3 per view |
| Procedures depend on this table | +2 per procedure |
| Triggers on this table | +1 per trigger |
| 20+ references found | +5 (Critical) |
| 10-20 references found | +3 |
| Table is in production | +5 |

## Pre-Drop Checklist

- [ ] Data backed up?
- [ ] Data migrated to replacement table (if applicable)?
- [ ] All FK references from other tables removed?
- [ ] All views depending on this table dropped/updated?
- [ ] All procedures depending on this table updated?
- [ ] All synonyms pointing to this table dropped?
- [ ] Triggers on this table will be auto-dropped?
- [ ] Indexes on this table will be auto-dropped?
- [ ] Associated sequences can be dropped?

## Drop Sequence

### Safe Drop Order

1. **Remove FK constraints** from other tables that reference this table
2. **Drop or update views** that depend on this table
3. **Update procedures** that reference this table
4. **Drop synonyms** pointing to this table
5. **Drop the table** (triggers and indexes drop automatically)
6. **Drop orphaned sequences** if applicable

### SQL Commands

```sql
-- Step 1: Find and drop FKs from other tables
-- (Must identify these first via search)
ALTER TABLE other_table DROP CONSTRAINT fk_to_this_table;

-- Step 2: Drop dependent views
DROP VIEW view_using_this_table;

-- Step 3: Drop the table
DROP TABLE {TABLE};
-- Or with cascade (dangerous - auto-drops dependents)
DROP TABLE {TABLE} CASCADE CONSTRAINTS;  -- Oracle
DROP TABLE {TABLE} CASCADE;              -- PostgreSQL
```

## CASCADE Warning

⚠️ **Using CASCADE is dangerous!**

```sql
-- This will automatically drop:
-- - All FK constraints referencing this table
-- - All views (in some databases)
-- - All triggers
-- Only use if you've identified all dependencies!
DROP TABLE {TABLE} CASCADE;
```

## Alternative: Soft Delete

Instead of dropping, consider:

```sql
-- Rename to mark as deprecated
ALTER TABLE {TABLE} RENAME TO {TABLE}_deprecated;

-- Or move to archive schema
ALTER TABLE {TABLE} SET SCHEMA archive;
```

This preserves data and allows rollback.
