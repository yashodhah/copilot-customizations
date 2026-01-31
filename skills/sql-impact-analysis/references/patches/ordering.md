# Patch Ordering and Dependencies

## Finding Explicit Dependencies

### Dependency Comments

Many teams use comments to mark dependencies:

| Pattern | Description |
|---------|-------------|
| `--\s*DEPENDS\s*ON\s*:\s*(.*)` | Explicit dependency |
| `--\s*REQUIRES\s*:\s*(.*)` | Required patch |
| `--\s*AFTER\s*:\s*(.*)` | Must run after |
| `--\s*BEFORE\s*:\s*(.*)` | Must run before |
| `--\s*PREREQUISITE\s*:\s*(.*)` | Prerequisite patch |
| `/\*\s*DEPENDS\s*ON\s*:[\s\S]*?\*/` | Block comment deps |

### Script Includes

| Pattern | Description | Database/Tool |
|---------|-------------|---------------|
| `@@\s*{FILENAME}` | Include script | SQL Server (SQLCMD) |
| `@\s*{FILENAME}` | Include script | Oracle (SQL*Plus) |
| `\i\s+{FILENAME}` | Include script | PostgreSQL (psql) |
| `SOURCE\s+{FILENAME}` | Include script | MySQL |
| `:r\s+{FILENAME}` | Include script | SQL Server (SQLCMD) |

## Finding Implicit Dependencies

### Object Creation Order

| If Patch Creates... | It Depends On... |
|--------------------|------------------|
| Table with FK | Referenced table |
| View | Base tables |
| Procedure using table | That table |
| Trigger on table | That table |
| Index on table | That table |
| Grant on object | That object |

### Search for Create Statements

```
# Find what objects a patch creates
grep_search: "CREATE\s+(OR\s+REPLACE\s+)?(TABLE|VIEW|PROCEDURE|FUNCTION|TRIGGER|INDEX|SEQUENCE)"
isRegexp: true
includePattern: "{PATCH_FILE}"
```

### Search for Dependencies in Creates

```
# Tables referenced by FKs
grep_search: "REFERENCES\s+(\w+\.)?(\w+)"
isRegexp: true
includePattern: "{PATCH_FILE}"

# Tables used in views
grep_search: "CREATE.*VIEW[\s\S]*?FROM\s+(\w+\.)?(\w+)"
isRegexp: true

# Tables used in procedures
grep_search: "CREATE.*PROCEDURE[\s\S]*?(FROM|INTO|UPDATE|DELETE)\s+(\w+\.)?(\w+)"
isRegexp: true
```

## Search Strategy

### Step 1: Find Explicit Dependencies

```
# Look for dependency comments
grep_search: "(DEPENDS|REQUIRES|AFTER|BEFORE|PREREQUISITE)"
isRegexp: true
includePattern: "**/*.sql"
```

### Step 2: Build Object Inventory

For each patch, identify:
- What objects it CREATES
- What objects it ALTERS
- What objects it DROPS
- What objects it REFERENCES

```
# Creates
grep_search: "CREATE\s+(OR\s+REPLACE\s+)?(\w+)\s+(\w+\.)?(\w+)"
isRegexp: true
includePattern: "{PATCH_FILE}"

# Alters
grep_search: "ALTER\s+(\w+)\s+(\w+\.)?(\w+)"
isRegexp: true

# Drops
grep_search: "DROP\s+(\w+)\s+(\w+\.)?(\w+)"
isRegexp: true
```

### Step 3: Cross-Reference

For each object CREATED in patch A:
- Find patches that REFERENCE that object
- Those patches must run AFTER patch A

## Dependency Matrix

Build a matrix:

| Patch | Creates | Depends On Objects | Must Run After |
|-------|---------|-------------------|----------------|
| 001_tables.sql | customers, orders | - | - |
| 002_fk.sql | FK constraints | customers, orders | 001 |
| 003_views.sql | order_summary view | orders | 001 |
| 004_procs.sql | get_customer proc | customers | 001 |

## Circular Dependency Detection

Watch for:
- A depends on B, B depends on A
- A → B → C → A

If found:
1. Combine into single patch, or
2. Create stub objects, then alter

## Patch Naming Conventions

Common patterns (extract from filename):

| Pattern | Meaning |
|---------|---------|
| `\d{3}_.*\.sql` | Numbered sequence (001_, 002_) |
| `\d{8}_.*\.sql` | Date-based (20260131_) |
| `v\d+\.\d+.*\.sql` | Version-based (v1.2_) |
| `.*_ddl\.sql` | DDL changes |
| `.*_dml\.sql` | Data changes |
| `.*_rollback\.sql` | Rollback script |

## Severity Factors

| Factor | Score |
|--------|-------|
| Patch creates core table | +4 |
| Patch is dependency for 5+ others | +3 |
| Patch has no explicit dependency markers | +2 (risk of missed deps) |
| Patch drops objects | +3 |
| Patch modifies procedures | +2 |
| Circular dependency detected | +5 (Critical) |

## Pre-Deployment Checklist

- [ ] All patches have explicit dependency comments?
- [ ] Deployment order documented?
- [ ] Rollback scripts exist?
- [ ] No circular dependencies?
- [ ] All referenced objects exist or created earlier?
- [ ] DDL runs before DML that needs the objects?

## Deployment Order Algorithm

1. **Parse all patches** - extract creates/alters/drops/references
2. **Build dependency graph** - edges from referenced to referencing
3. **Topological sort** - order patches so dependencies come first
4. **Detect cycles** - fail if circular dependency found

## Example Analysis

```
# Patch: add_order_status.sql

-- Content analysis:
-- CREATES: order_status table
-- ALTERS: orders table (add FK to order_status)
-- REFERENCES: orders table

-- Dependencies:
-- - orders table must exist
-- - This patch must run before any patch that queries order_status

-- Explicit dependency header (recommended):
-- DEPENDS ON: 001_create_orders_table.sql
```

## Common Issues

### Issue: Missing Intermediate Object
```sql
-- Patch 003 creates view using table from patch 001
-- But runs before patch 001 in alphabetical order!
CREATE VIEW v AS SELECT * FROM new_table;  -- FAILS!
```

### Issue: FK Before Referenced Table
```sql
-- Patch 002 adds FK to table created in patch 003
ALTER TABLE orders ADD CONSTRAINT fk 
  REFERENCES new_table(id);  -- FAILS!
```

### Issue: Procedure Before Table
```sql
-- Procedure references table that doesn't exist yet
CREATE PROCEDURE get_data AS
  SELECT * FROM future_table;  -- May fail depending on DB
```

## Rollback Order

Rollback is **reverse** of deployment:

| Deploy Order | Rollback Order |
|--------------|----------------|
| 1. Create table | 3. Drop table |
| 2. Add FK | 2. Drop FK |
| 3. Create view | 1. Drop view |

Ensure rollback scripts exist and are tested!
