# Index Dependency Patterns

## Finding Index Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+(UNIQUE\s+)?INDEX\s+(\w+\.)?{INDEX}` | Create index |
| `CREATE\s+.*INDEX\s+(\w+\.)?{INDEX}\s+ON\s+(\w+\.)?{TABLE}` | Index on table |
| `DROP\s+INDEX\s+(\w+\.)?{INDEX}` | Drop index |
| `ALTER\s+INDEX\s+(\w+\.)?{INDEX}` | Alter index |
| `REINDEX\s+.*{INDEX}` | Rebuild index |

## Finding Indexes on a Table

| Pattern | Description |
|---------|-------------|
| `INDEX.*ON\s+(\w+\.)?{TABLE}` | Any index on table |
| `INDEX.*ON\s+(\w+\.)?{TABLE}\s*\(` | Index with columns |
| `CREATE.*INDEX.*ON\s+(\w+\.)?{TABLE}\s*\(.*{COLUMN}` | Index on specific column |

## Index Types

| Pattern | Type |
|---------|------|
| `CREATE\s+INDEX` | Basic index |
| `CREATE\s+UNIQUE\s+INDEX` | Unique index |
| `CREATE\s+CLUSTERED\s+INDEX` | Clustered (SQL Server) |
| `CREATE\s+NONCLUSTERED\s+INDEX` | Non-clustered (SQL Server) |
| `CREATE\s+BITMAP\s+INDEX` | Bitmap index (Oracle) |
| `CREATE\s+.*INDEX.*USING\s+BTREE` | B-tree index |
| `CREATE\s+.*INDEX.*USING\s+HASH` | Hash index |
| `CREATE\s+.*INDEX.*USING\s+GIN` | GIN index (PostgreSQL) |
| `CREATE\s+.*INDEX.*USING\s+GIST` | GiST index (PostgreSQL) |

## Function-Based Indexes

| Pattern | Description |
|---------|-------------|
| `INDEX.*ON.*\(\s*{FUNC}\s*\(` | Function in index |
| `INDEX.*ON.*\(\s*UPPER\s*\(` | Upper-case index |
| `INDEX.*ON.*\(\s*LOWER\s*\(` | Lower-case index |
| `INDEX.*ON.*\(\s*COALESCE\s*\(` | Coalesce index |

## Search Strategy

### Find All Indexes on a Table

```
# Step 1: Find index definitions
grep_search: "CREATE.*INDEX.*ON\s+(\w+\.)?{TABLE}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find indexes on specific column
grep_search: "INDEX.*ON\s+(\w+\.)?{TABLE}\s*\(.*\b{COLUMN}\b"
isRegexp: true
```

### Find Indexes Using a Column

```
# Column in any index
grep_search: "CREATE.*INDEX.*\(.*\b{COLUMN}\b"
isRegexp: true

# Column as first/leading column (most important)
grep_search: "INDEX.*\(\s*{COLUMN}\s*(,|\))"
isRegexp: true
```

### Find Function-Based Indexes

```
# Indexes using functions
grep_search: "INDEX.*\(\s*\w+\s*\("
isRegexp: true

# Specific function
grep_search: "INDEX.*\(\s*{FUNC}\s*\("
isRegexp: true
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Primary key index | +5 (critical) |
| Unique index | +4 (constraint) |
| Clustered index | +4 (physical order) |
| Foreign key index | +3 |
| Composite index (multiple columns) | +2 |
| Function-based index | +3 (function change affects) |
| Covering index | +2 (query performance) |
| Index on large table | +2 (rebuild time) |

## Impact of Column Changes on Indexes

### Column Dropped
- Indexes containing column are **dropped automatically** (usually)
- Performance impact on queries that used the index

### Column Type Changed
- Index may become invalid
- May need to drop and recreate index
- Function-based indexes especially sensitive

### Column Renamed
- Index definitions reference old name
- May need to recreate index

## Impact of Index Changes on Queries

Queries don't directly reference indexes, but:

### Index Dropped
- Queries using the index will slow down
- Full table scans may occur

### Index Modified
- Query plans may change
- Performance may improve or degrade

### New Index Added
- Generally safe
- May improve query performance
- Takes time to build on large tables

## Pre-Change Checklist

### When Changing an Index
- [ ] What queries use this index?
- [ ] Is it a unique constraint?
- [ ] Is it a primary key?
- [ ] Is it supporting a foreign key?
- [ ] How large is the table?
- [ ] Online rebuild possible?

### When Changing a Column with Indexes
- [ ] What indexes contain this column?
- [ ] Is the column the leading column in any index?
- [ ] Are there function-based indexes on this column?
- [ ] Will indexes auto-update or need recreation?

## Index Rebuild Strategies

```sql
-- SQL Server: Online rebuild
ALTER INDEX {INDEX} ON {TABLE} REBUILD WITH (ONLINE = ON);

-- Oracle: Online rebuild
ALTER INDEX {INDEX} REBUILD ONLINE;

-- PostgreSQL: Concurrent rebuild
REINDEX INDEX CONCURRENTLY {INDEX};

-- Drop and recreate (offline)
DROP INDEX {INDEX};
CREATE INDEX {INDEX} ON {TABLE} (...);
```

## Common Issues

### Issue: Implicit Index Removal
```sql
-- Dropping a column removes indexes that include it
ALTER TABLE t DROP COLUMN c;
-- Any index containing 'c' is now gone!
-- Queries that depended on that index will slow down
```

### Issue: Type Change Invalidates Index
```sql
-- Index on varchar column
CREATE INDEX idx ON t (varchar_col);

-- Changing to text may invalidate
ALTER TABLE t ALTER COLUMN varchar_col TYPE text;
-- Index may need recreation
```

### Issue: Function Index and Function Change
```sql
-- Function-based index
CREATE INDEX idx ON t (my_func(col));

-- If you change my_func, index may:
-- - Give wrong results
-- - Need to be rebuilt
-- - Become invalid
```

## Query Impact Analysis

To understand which queries are affected by index changes:

```
# Find queries that might use the index
# (Queries filtering on indexed columns)

# For index on (col1, col2):
grep_search: "WHERE.*\bcol1\b"
grep_search: "ORDER\s+BY.*\bcol1\b"
grep_search: "JOIN.*ON.*\bcol1\b"
```

Note: Actual index usage depends on query optimizer, not just query text.
