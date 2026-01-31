# Procedure Dependency Patterns

## Finding Procedure Calls

### By Database Type

| Pattern | Description | Database |
|---------|-------------|----------|
| `EXEC(UTE)?\s+(\w+\.)?{PROC}` | Execute statement | SQL Server |
| `CALL\s+(\w+\.)?{PROC}` | Call statement | Oracle, MySQL, PostgreSQL |
| `PERFORM\s+(\w+\.)?{PROC}` | Perform statement | PostgreSQL |
| `{PROC}\s*\(` | Direct call in PL/SQL | Oracle |
| `BEGIN\s+(\w+\.)?{PROC}` | Block call | Oracle |
| `{PACKAGE}\.{PROC}` | Package procedure | Oracle |
| `SELECT\s+(\w+\.)?{PROC}\s*\(` | Function-style call | PostgreSQL |

### Combined Pattern (All Databases)

```regex
(EXEC(UTE)?|CALL|PERFORM)\s+(\w+\.)?{PROC}|{PROC}\s*\(
```

## Finding Procedure Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+(OR\s+REPLACE\s+)?PROC(EDURE)?\s+(\w+\.)?{PROC}` | Create/replace |
| `ALTER\s+PROC(EDURE)?\s+(\w+\.)?{PROC}` | Alter |
| `DROP\s+PROC(EDURE)?\s+(\w+\.)?{PROC}` | Drop |
| `GRANT\s+EXECUTE\s+ON\s+(\w+\.)?{PROC}` | Permissions |

## Finding What a Procedure Depends On

Search WITHIN the procedure body for these patterns:

### Table Dependencies

| Pattern | What It Means |
|---------|---------------|
| `FROM\s+(\w+\.)?(\w+)` | Tables being read |
| `INTO\s+(\w+\.)?(\w+)` | Tables being inserted into |
| `UPDATE\s+(\w+\.)?(\w+)` | Tables being updated |
| `DELETE\s+(FROM\s+)?(\w+\.)?(\w+)` | Tables being deleted from |

### Other Procedure Calls

| Pattern | What It Means |
|---------|---------------|
| `EXEC(UTE)?\s+(\w+\.)?(\w+)` | Procedures called |
| `CALL\s+(\w+\.)?(\w+)` | Procedures called |

### Function Calls

| Pattern | What It Means |
|---------|---------------|
| `(\w+)\s*\(` | Potential function calls |
| `SELECT\s+(\w+)\s*\(` | Functions in SELECT |

## Search Strategy

### To Find What Calls This Procedure

```
# Step 1: Direct EXEC/CALL references
grep_search: "(EXEC|EXECUTE|CALL|PERFORM)\s+(\w+\.)?{PROC}"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Direct invocation (Oracle PL/SQL style)
grep_search: "{PROC}\s*\("
isRegexp: true

# Step 3: Package-qualified calls (Oracle)
grep_search: "\w+\.{PROC}\s*\("
isRegexp: true

# Step 4: In dynamic SQL
grep_search: "'{PROC}'"
isRegexp: true

# Step 5: Semantic search
semantic_search: "code that calls {PROC} procedure"
```

### To Find What This Procedure Depends On

```
# First, read the procedure definition
# Then search within it for:

# Tables used
grep_search: "(FROM|INTO|UPDATE|DELETE)\s+\w+"
includePattern: "{PROC_FILE}"

# Other procedures called
grep_search: "(EXEC|CALL)\s+\w+"
includePattern: "{PROC_FILE}"
```

## Severity Factors

| Factor | Score |
|--------|-------|
| Called by 10+ other objects | +5 (Critical) |
| Called by 5-10 objects | +3 |
| Called by 1-5 objects | +1 |
| Called by scheduled jobs | +3 |
| Called by external systems/APIs | +5 |
| Has output parameters | +2 (signature change risk) |
| Returns result set | +2 (structure change risk) |
| Modifies data (INSERT/UPDATE/DELETE) | +2 |
| Part of transaction flow | +3 |

## Change Types and Risks

### Signature Changes (Parameters)

| Change | Risk |
|--------|------|
| Add optional parameter (with default) | Low |
| Add required parameter | High - all callers must update |
| Remove parameter | High - callers may pass it |
| Change parameter type | High - type mismatch |
| Change parameter order | High - positional callers break |
| Rename parameter | Medium - named callers break |

### Body Changes

| Change | Risk |
|--------|------|
| Logic fix (same inputs/outputs) | Low |
| Performance optimization | Low |
| Additional table access | Medium - new dependencies |
| Changed return values | High - callers may expect old values |
| Changed error handling | Medium - callers may catch specific errors |

### Output Changes

| Change | Risk |
|--------|------|
| Add column to result set | Low - callers ignore extra |
| Remove column from result set | High - callers may use it |
| Change column type in result | High - type issues |
| Change column order | Medium - positional access breaks |

## Pre-Change Checklist

- [ ] All callers identified?
- [ ] Signature change? All callers can be updated?
- [ ] Output change? All consumers can handle it?
- [ ] New dependencies introduced?
- [ ] Error handling changes? Callers handle errors correctly?
- [ ] Part of scheduled jobs? Job timing OK?
- [ ] Called by external systems? API contract OK?

## Deployment Considerations

### For Signature Changes

```sql
-- Option 1: Add new procedure, deprecate old
CREATE PROCEDURE {PROC}_v2 (new_params) ...
-- Update callers to use _v2
-- Later drop old procedure

-- Option 2: Overload (if supported)
CREATE PROCEDURE {PROC} (new_params) ...  -- new signature
-- Keep old signature with wrapper

-- Option 3: Default parameters
ALTER PROCEDURE {PROC} 
ADD @new_param INT = NULL;  -- existing callers still work
```
