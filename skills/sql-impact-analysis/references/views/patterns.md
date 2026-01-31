# View Dependency Patterns

## Finding View Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+(OR\s+REPLACE\s+)?VIEW\s+(\w+\.)?{VIEW}` | Create/replace view |
| `CREATE\s+(OR\s+REPLACE\s+)?MATERIALIZED\s+VIEW\s+(\w+\.)?{VIEW}` | Materialized view |
| `ALTER\s+VIEW\s+(\w+\.)?{VIEW}` | Alter view |
| `DROP\s+VIEW\s+(\w+\.)?{VIEW}` | Drop view |
| `REFRESH\s+MATERIALIZED\s+VIEW\s+(\w+\.)?{VIEW}` | Refresh mat view |

## Finding View Usage

Views are used like tables:

| Pattern | Description |
|---------|-------------|
| `FROM\s+(\w+\.)?{VIEW}` | Select from view |
| `JOIN\s+(\w+\.)?{VIEW}` | Join with view |
| `INTO\s+(\w+\.)?{VIEW}` | Insert through view |
| `UPDATE\s+(\w+\.)?{VIEW}` | Update through view |
| `DELETE\s+(FROM\s+)?(\w+\.)?{VIEW}` | Delete through view |

## Finding What a View Depends On

Look inside the view definition:

| Pattern | What It Finds |
|---------|---------------|
| `FROM\s+(\w+\.)?(\w+)` | Base tables |
| `JOIN\s+(\w+\.)?(\w+)` | Joined tables |
| `(\w+)\.(\w+)` | Table.column references |
| `{FUNC}\s*\(` | Functions used |
| `{VIEW2}` | Other views (nested) |

## Search Strategy

### Find Views That Use a Table

```
# Step 1: Find views selecting from the table
grep_search: "CREATE.*VIEW[\s\S]*?FROM\s+(\w+\.)?{TABLE}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find views joining the table
grep_search: "CREATE.*VIEW[\s\S]*?JOIN\s+(\w+\.)?{TABLE}"
isRegexp: true

# Step 3: Semantic search
semantic_search: "view definition that uses {TABLE}"
```

### Find Views That Use a Column

```
# Find views referencing a specific column
grep_search: "CREATE.*VIEW[\s\S]*?\b{COLUMN}\b"
isRegexp: true

# Find views with qualified column reference
grep_search: "CREATE.*VIEW[\s\S]*?{TABLE}\.{COLUMN}"
isRegexp: true
```

### Find What Depends on a View

```
# Other views using this view (nested views)
grep_search: "CREATE.*VIEW[\s\S]*?FROM\s+(\w+\.)?{VIEW}"
isRegexp: true

# Procedures using the view
grep_search: "(PROCEDURE|FUNCTION)[\s\S]*?FROM\s+(\w+\.)?{VIEW}"
isRegexp: true

# Any SELECT from view
grep_search: "(FROM|JOIN)\s+(\w+\.)?{VIEW}"
isRegexp: true
```

## View Types

| Type | Characteristics |
|------|-----------------|
| Simple view | Single table, no functions |
| Complex view | Joins, functions, grouping |
| Materialized view | Stored results, needs refresh |
| Updatable view | Can INSERT/UPDATE/DELETE through it |
| WITH CHECK OPTION | Validates modifications |

## Severity Factors

| Factor | Score |
|--------|-------|
| Materialized view | +3 (requires refresh strategy) |
| View used by other views | +2 per dependent view |
| View used by procedures | +2 per procedure |
| View used by external systems/reports | +4 |
| Updatable view | +2 (INSERT/UPDATE behavior affected) |
| WITH CHECK OPTION | +2 (validation may fail) |
| 10+ references to view | +3 |

## Impact of Table Changes on Views

### Column Added to Table
- Views using `SELECT *` will include new column
- Explicit column lists unaffected

### Column Modified in Table
- Views referencing column may break if type incompatible
- Computed expressions may fail

### Column Dropped from Table
- **Breaking** - views referencing column become invalid
- Must update or drop views first

### Column Renamed in Table
- **Breaking** - views using old name become invalid
- Must update views first

### Table Dropped
- **Breaking** - all views on table become invalid
- Must drop views first

## Pre-Change Checklist

### When Changing a View
- [ ] What tables does it depend on?
- [ ] What other views depend on it?
- [ ] What procedures use it?
- [ ] Is it updatable? Will it stay updatable?
- [ ] Is it materialized? Refresh strategy?

### When Changing a Base Table
- [ ] What views use this table?
- [ ] Do views use `SELECT *`?
- [ ] Do views reference the column being changed?
- [ ] Will views still compile after change?

## View Validation

After changing base tables, views may become invalid:

```sql
-- Oracle: Check for invalid views
SELECT object_name, status 
FROM user_objects 
WHERE object_type = 'VIEW' AND status = 'INVALID';

-- SQL Server: Try to recompile
EXEC sp_refreshview '{VIEW}';

-- PostgreSQL: Views auto-validate, but check
SELECT * FROM {VIEW} LIMIT 1;
```

## Migration Strategy

### Changing a Column Used by Views

1. **Find all views** using the column
2. **Script the views** (save current definitions)
3. **Drop dependent views** (or let them go invalid)
4. **Make table change**
5. **Recreate views** with updated definitions

```sql
-- Step 1: Find views
grep_search: "CREATE.*VIEW.*{COLUMN}"

-- Step 2: Save definitions (from search results)

-- Step 3: Drop views (reverse dependency order)
DROP VIEW child_view;
DROP VIEW parent_view;

-- Step 4: Change table
ALTER TABLE {TABLE} ...;

-- Step 5: Recreate views
CREATE VIEW parent_view AS ...;
CREATE VIEW child_view AS ...;
```

### Materialized View Considerations

```sql
-- Materialized views need refresh after base table changes
REFRESH MATERIALIZED VIEW {MV};

-- May need to drop and recreate if structure changes
DROP MATERIALIZED VIEW {MV};
-- Change base table
CREATE MATERIALIZED VIEW {MV} AS ...;
```

## Common Issues

### Issue: SELECT * in View
```sql
-- View uses SELECT *
CREATE VIEW v AS SELECT * FROM t;

-- Adding column to t changes view's output!
-- This may break consumers expecting fixed columns
```

### Issue: Nested View Cascade
```sql
-- V1 depends on T1
-- V2 depends on V1
-- V3 depends on V2
-- Changing T1 affects all three!
```

### Issue: Computed Expression Type Change
```sql
-- View computes a value
CREATE VIEW v AS SELECT price * quantity AS total FROM orders;

-- If price changes from INT to DECIMAL, total type changes too!
```
