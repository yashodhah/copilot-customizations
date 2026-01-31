# Add Table Impact Analysis

## Risk Level
🟢 **Low risk** - Additive change with no existing dependencies

## Key Considerations

| Factor | Consideration |
|--------|---------------|
| Foreign keys | If FK references existing tables, those tables are dependencies |
| Sequences | If using sequences, they must exist first |
| Types | If using custom types, they must exist first |
| Schema | Schema must exist |
| Tablespace | Tablespace must exist (if specified) |

## Patterns to Search

### Check for Prerequisites

| Pattern | Description |
|---------|-------------|
| `REFERENCES\s+(\w+\.)?(\w+)` | FK to other tables (dependencies) |
| `(\w+)\.NEXTVAL` | Sequence usage (Oracle) |
| `NEXTVAL\s*\(\s*'(\w+)'` | Sequence usage (PostgreSQL) |
| `TYPE\s+(\w+)` | Custom type usage |

### Check for Naming Conflicts

| Pattern | Description |
|---------|-------------|
| `CREATE\s+TABLE\s+(\w+\.)?{TABLE}` | Table already exists? |
| `CREATE\s+VIEW\s+(\w+\.)?{TABLE}` | View with same name? |
| `CREATE\s+SYNONYM\s+.*{TABLE}` | Synonym with same name? |

### Search Strategy

```
# Step 1: Check if table name already exists
grep_search: "CREATE\s+(TABLE|VIEW)\s+(\w+\.)?{TABLE}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: If table has FKs, find referenced tables
# (Parse the CREATE TABLE statement to find REFERENCES clauses)

# Step 3: Check sequence dependencies
grep_search: "NEXTVAL.*{SEQUENCE}"
isRegexp: true
```

## Deployment Order

When adding a table with dependencies:

1. **Sequences** - Create any sequences used for auto-increment
2. **Types** - Create any custom types used
3. **Referenced tables** - Ensure FK target tables exist
4. **New table** - Create the table
5. **Indexes** - Create indexes on the table
6. **Grants** - Apply permissions

## Severity Factors

| Factor | Score |
|--------|-------|
| Table has no FKs | +0 (standalone) |
| Table has FKs to existing tables | +1 per FK |
| Table uses sequences | +1 |
| Table uses custom types | +1 |
| Part of larger migration | +1 |

## Pre-Add Checklist

- [ ] Table name doesn't conflict with existing objects?
- [ ] All referenced tables (FK targets) exist?
- [ ] All sequences exist?
- [ ] All custom types exist?
- [ ] Schema exists?
- [ ] Tablespace exists (if specified)?
- [ ] Permissions planned?

## Common Issues

### Issue: FK Target Doesn't Exist
```sql
-- This will fail if customers doesn't exist
CREATE TABLE orders (
  customer_id INT REFERENCES customers(id)  -- dependency!
);
```

### Issue: Sequence Not Created
```sql
-- This will fail if order_seq doesn't exist
CREATE TABLE orders (
  id INT DEFAULT order_seq.NEXTVAL  -- dependency!
);
```

## Rollback

```sql
-- Simple rollback - just drop the table
DROP TABLE {TABLE};

-- If you created supporting objects:
DROP TABLE {TABLE};
DROP SEQUENCE {TABLE}_seq;
```
