# Modify Column Impact Analysis

## Risk Level
🟠 **Medium to High risk** - Data type changes can cause data loss or errors

## Risk Classification

> **Risk depends on WHAT is being modified.** Widening is safer than narrowing or type changes.

### Risk Matrix by Modification Type

| Pattern | Widen | Narrow | Type Change | Add NOT NULL |
|---------|-------|--------|-------------|--------------|
| `SELECT column` | 🟢 Safe | 🟢 Safe | 🟢 Safe | 🟢 Safe |
| `WHERE column = 'str'` | 🟢 Safe | 🟢 Safe | 🔴 Risk | 🟢 Safe |
| `WHERE column > 100` | 🟢 Safe | 🟢 Safe | 🔴 Risk | 🟢 Safe |
| `WHERE column LIKE '%x%'` | 🟢 Safe | 🟢 Safe | 🔴 Risk | 🟢 Safe |
| `INSERT (column)` | 🟢 Safe | 🟡 Review | 🔴 Risk | 🟡 Review |
| `SET column = value` | 🟢 Safe | 🟡 Review | 🔴 Risk | 🟡 Review |
| Index on column | 🟢 Safe | 🟡 Review | 🔴 Risk | 🟢 Safe |
| `CAST(column AS type)` | 🟢 Safe | 🟢 Safe | 🟡 Review | 🟢 Safe |

### 🔴 Risk (Will Break or Cause Data Issues)

**For Type Changes (e.g., VARCHAR → INT):**

| Pattern | Why Risk | Regex |
|---------|----------|-------|
| `WHERE column = 'string'` | Type mismatch | `WHERE.*{COLUMN}\s*=\s*'` |
| `WHERE column LIKE` | LIKE only works on strings | `WHERE.*{COLUMN}\s+LIKE` |
| `column + other_column` | Arithmetic/concat mismatch | `{COLUMN}\s*[\+\-\*\/]` |
| Procedure DECLARE | Variable type mismatch | `DECLARE.*{COLUMN}` |

**For Adding NOT NULL:**

| Pattern | Why Risk | Regex |
|---------|----------|-------|
| `INSERT without column` | NULL implicit - will fail | `INSERT.*{TABLE}.*VALUES` |
| `INSERT with NULL` | Explicit NULL - will fail | `INSERT.*{COLUMN}.*NULL` |

### 🟡 Review (May Be Affected)

**For Narrowing (e.g., VARCHAR(100) → VARCHAR(50)):**

| Pattern | Why Review | Regex |
|---------|------------|-------|
| `INSERT (column)` | Data may be too long | `INSERT.*\(.*{COLUMN}` |
| `SET column = value` | Update value may be too long | `SET\s+{COLUMN}\s*=` |
| Index on column | May need rebuild | `INDEX.*{COLUMN}` |
| `column \|\| other` | Concat result may exceed | `{COLUMN}\s*\|\|` |

### 🟢 Safe (Informational Only)

**For Widening (e.g., VARCHAR(50) → VARCHAR(100)):**

| Pattern | Why Safe | Regex |
|---------|----------|-------|
| All SELECT patterns | No change in behavior | - |
| All WHERE patterns | No change in comparison | - |
| All ORDER BY patterns | No change in sorting | - |

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
