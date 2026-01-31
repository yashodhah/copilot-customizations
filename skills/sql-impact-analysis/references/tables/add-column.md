# Add Column Impact Analysis

## Risk Level
🟢 **Generally low risk** - Additive change, but watch for NOT NULL without defaults

## Risk Classification

> **Not all matches are risks for ADD COLUMN.** Most explicit column references are safe.

### 🔴 Risk (Will Break)

| Pattern | Why Risk | Regex |
|---------|----------|-------|
| `INSERT INTO table VALUES (...)` | Column count mismatch if NOT NULL | `INSERT\s+INTO\s+(\w+\.)?{TABLE}\s+VALUES` |
| `INSERT...SELECT *` | Inserts all cols including new one | `INSERT.*SELECT\s+\*.*FROM` |

### 🟡 Review (May Be Affected)

| Pattern | Why Review | Regex |
|---------|------------|-------|
| `SELECT * FROM table` | Returns new column - check consumers | `SELECT\s+\*\s+FROM\s+(\w+\.)?{TABLE}` |
| Views with `SELECT *` | View will include new column | `CREATE.*VIEW.*SELECT\s+\*.*{TABLE}` |
| `SELECT * INTO #temp` | Temp table schema changes | `SELECT\s+\*\s+INTO\s+#` |

### 🟢 Safe (Informational Only)

| Pattern | Why Safe | Regex |
|---------|----------|-------|
| `INSERT INTO table (col1, col2)` | Explicit columns - new col ignored | `INSERT\s+INTO\s+(\w+\.)?{TABLE}\s*\(` |
| `SELECT col1, col2 FROM table` | Explicit columns - unaffected | `SELECT\s+\w+.*FROM.*{TABLE}` |
| `UPDATE table SET col = x` | Doesn't affect new column | `UPDATE.*{TABLE}.*SET` |
| Views with explicit columns | View definition unchanged | - |

## Key Considerations

| Factor | Risk Impact |
|--------|-------------|
| Nullable column | Low - safe addition |
| NOT NULL with DEFAULT | Medium - default applied to existing rows |
| NOT NULL without DEFAULT | High - may fail on existing data |
| Large table | Medium - may lock table during ALTER |

## Patterns to Search

### Find Existing Table References

Before adding, understand how the table is used:

| Pattern | Description |
|---------|-------------|
| `INSERT\s+INTO\s+(\w+\.)?{TABLE}\s*\(` | INSERT with column list - may need update |
| `INSERT\s+INTO\s+(\w+\.)?{TABLE}\s+VALUES` | INSERT without columns - will break if NOT NULL |
| `SELECT\s+\*\s+FROM\s+(\w+\.)?{TABLE}` | SELECT * - will include new column |
| `CREATE.*VIEW.*FROM\s+(\w+\.)?{TABLE}` | Views on table |

### Search Strategy

```
# Step 1: Find INSERTs that list columns explicitly
grep_search: "INSERT\s+INTO\s+(\w+\.)?{TABLE}\s*\("
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find INSERTs without column list (risky if NOT NULL)
grep_search: "INSERT\s+INTO\s+(\w+\.)?{TABLE}\s+VALUES"
isRegexp: true

# Step 3: Find SELECT * queries
grep_search: "SELECT\s+\*\s+FROM\s+(\w+\.)?{TABLE}"
isRegexp: true

# Step 4: Find views that may need updating
grep_search: "CREATE.*VIEW.*{TABLE}"
isRegexp: true
```

## Severity Factors

| Factor | Score |
|--------|-------|
| NOT NULL without DEFAULT | +4 |
| NOT NULL with DEFAULT | +1 |
| Nullable column | +0 |
| Table has INSERT without column list | +2 per occurrence |
| Table has SELECT * in views | +1 per view |
| Large table (performance concern) | +1 |

## Pre-Add Checklist

- [ ] Is the column nullable or does it have a DEFAULT?
- [ ] Will existing INSERT statements work?
- [ ] Do any views need to be updated?
- [ ] Is the table large enough to cause lock concerns?
- [ ] Are there triggers on INSERT that may be affected?

## Recommendations by Severity

### Low Severity (nullable column)
- Standard deployment, no special handling

### Medium Severity (NOT NULL with DEFAULT)
- Test on staging with production-like data volume
- Consider off-hours deployment for large tables

### High Severity (NOT NULL without DEFAULT)
- Must update existing rows first OR
- Add as nullable, populate, then alter to NOT NULL
