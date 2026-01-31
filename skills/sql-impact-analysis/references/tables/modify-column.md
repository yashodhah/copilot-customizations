# Modify Column Impact Analysis

## Risk Level
🟠 **Medium to High risk** - Data type changes can cause data loss or errors

## Types of Modifications

| Modification | Risk Level | Concern |
|--------------|------------|---------|
| Widen data type (VARCHAR(50) → VARCHAR(100)) | Low | Generally safe |
| Narrow data type (VARCHAR(100) → VARCHAR(50)) | High | Data truncation |
| Change type (VARCHAR → INT) | Critical | Data conversion errors |
| Add NOT NULL | High | Existing NULLs will fail |
| Remove NOT NULL | Low | Safe |
| Add DEFAULT | Low | Safe |
| Change DEFAULT | Low | Only affects new rows |
| Add CHECK constraint | Medium | Existing data may violate |

## Patterns to Search

### Find All Column References

| Pattern | Description |
|---------|-------------|
| `{TABLE}\.{COLUMN}` | Qualified column reference |
| `SELECT\s+.*\b{COLUMN}\b.*FROM\s+.*{TABLE}` | Column in SELECT |
| `WHERE\s+.*\b{COLUMN}\b` | Column in WHERE (type matters) |
| `SET\s+{COLUMN}\s*=` | Column in UPDATE |
| `INSERT.*{TABLE}.*\b{COLUMN}\b` | Column in INSERT |
| `ORDER\s+BY\s+.*\b{COLUMN}\b` | Column in ORDER BY |
| `GROUP\s+BY\s+.*\b{COLUMN}\b` | Column in GROUP BY |
| `CAST\s*\(.*{COLUMN}` | Explicit casts (type sensitive) |
| `CONVERT\s*\(.*{COLUMN}` | Type conversions |

### Find Comparisons (Type Sensitive)

| Pattern | Description |
|---------|-------------|
| `{COLUMN}\s*=\s*'` | String comparison |
| `{COLUMN}\s*=\s*\d` | Numeric comparison |
| `{COLUMN}\s*(>\|<\|>=\|<=)` | Range comparison |
| `{COLUMN}\s+IN\s*\(` | IN clause |
| `{COLUMN}\s+LIKE` | Pattern matching (string only) |
| `{COLUMN}\s+BETWEEN` | Range check |

### Find Index Usage

| Pattern | Description |
|---------|-------------|
| `INDEX.*\b{COLUMN}\b` | Column in index |
| `CREATE.*INDEX.*\({COLUMN}` | Index on column |

### Search Strategy

```
# Step 1: Find all direct column references
grep_search: "{TABLE}\.{COLUMN}"
isRegexp: false
includePattern: "**/*.sql"

# Step 2: Find WHERE clause usage (type sensitive)
grep_search: "WHERE.*\b{COLUMN}\b\s*(=|>|<|IN|LIKE|BETWEEN)"
isRegexp: true

# Step 3: Find type casts involving column
grep_search: "(CAST|CONVERT).*{COLUMN}"
isRegexp: true

# Step 4: Find indexes on column
grep_search: "INDEX.*{COLUMN}"
isRegexp: true

# Step 5: Semantic search
semantic_search: "SQL comparing or filtering on {COLUMN}"
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Narrowing data type | +4 |
| Changing data type family | +5 (Critical) |
| Adding NOT NULL (existing NULLs) | +4 |
| Column in WHERE clauses | +2 |
| Column in indexes | +3 |
| Column used in joins | +3 |
| Column has explicit CASTs | +2 |
| Used in procedures/functions | +2 per object |

## Data Validation Queries

Before modifying, run these checks:

```sql
-- Check for NULLs (before adding NOT NULL)
SELECT COUNT(*) FROM {TABLE} WHERE {COLUMN} IS NULL;

-- Check max length (before narrowing VARCHAR)
SELECT MAX(LEN({COLUMN})) FROM {TABLE};

-- Check for conversion errors (before type change)
SELECT {COLUMN} FROM {TABLE}
WHERE TRY_CAST({COLUMN} AS {NEW_TYPE}) IS NULL
  AND {COLUMN} IS NOT NULL;
```

## Pre-Modify Checklist

- [ ] What is the current data type?
- [ ] What data currently exists? (min/max/nulls)
- [ ] Will any existing data be truncated or fail conversion?
- [ ] Are there indexes that need rebuilding?
- [ ] Are there procedures doing type-specific operations?
- [ ] Will comparison operations still work?

## Recommendations

### Widening Type
- Usually safe, test and deploy

### Narrowing Type
- Validate no data exceeds new limit
- Consider adding CHECK constraint first
- Deploy during maintenance window

### Changing Type Family
- Create new column with new type
- Migrate data with explicit conversion
- Update dependent code
- Drop old column
