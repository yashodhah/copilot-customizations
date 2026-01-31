# Function Dependency Patterns

## Finding Function Calls

Functions are called inline in SQL statements, unlike procedures.

### Common Call Patterns

| Pattern | Description |
|---------|-------------|
| `{FUNC}\s*\(` | Direct function call |
| `SELECT\s+.*{FUNC}\s*\(` | Function in SELECT |
| `WHERE\s+.*{FUNC}\s*\(` | Function in WHERE |
| `SET\s+.*=\s*.*{FUNC}\s*\(` | Function in SET |
| `ORDER\s+BY\s+.*{FUNC}\s*\(` | Function in ORDER BY |
| `GROUP\s+BY\s+.*{FUNC}\s*\(` | Function in GROUP BY |
| `HAVING\s+.*{FUNC}\s*\(` | Function in HAVING |
| `:=\s*{FUNC}\s*\(` | PL/SQL assignment |
| `=\s*{FUNC}\s*\(` | T-SQL assignment |

### Schema-Qualified Calls

| Pattern | Description |
|---------|-------------|
| `{SCHEMA}\.{FUNC}\s*\(` | Schema-qualified call |
| `{PACKAGE}\.{FUNC}\s*\(` | Package function (Oracle) |
| `dbo\.{FUNC}\s*\(` | dbo schema (SQL Server) |

### In Computed Columns/Defaults

| Pattern | Description |
|---------|-------------|
| `DEFAULT\s+.*{FUNC}\s*\(` | Function in default value |
| `GENERATED.*AS\s*\(.*{FUNC}` | Computed column |
| `AS\s+{FUNC}\s*\(` | Computed column |

### In Constraints

| Pattern | Description |
|---------|-------------|
| `CHECK\s*\(.*{FUNC}\s*\(` | Function in check constraint |

## Finding Function Definitions

| Pattern | Description |
|---------|-------------|
| `CREATE\s+(OR\s+REPLACE\s+)?FUNCTION\s+(\w+\.)?{FUNC}` | Create/replace |
| `ALTER\s+FUNCTION\s+(\w+\.)?{FUNC}` | Alter |
| `DROP\s+FUNCTION\s+(\w+\.)?{FUNC}` | Drop |
| `GRANT\s+EXECUTE\s+ON\s+(FUNCTION\s+)?(\w+\.)?{FUNC}` | Permissions |

## Search Strategy

### To Find What Calls This Function

```
# Step 1: Direct function calls
grep_search: "{FUNC}\s*\("
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Schema-qualified calls
grep_search: "\w+\.{FUNC}\s*\("
isRegexp: true

# Step 3: In DEFAULT/COMPUTED columns (function embedded in DDL)
grep_search: "(DEFAULT|GENERATED|AS)\s+.*{FUNC}"
isRegexp: true

# Step 4: In CHECK constraints
grep_search: "CHECK\s*\(.*{FUNC}"
isRegexp: true

# Step 5: Semantic search
semantic_search: "SQL using {FUNC} function"
```

### To Find What This Function Depends On

Read the function definition and search for:
- Table references
- Other function calls
- Procedure calls (if allowed in your DB)

## Function vs Procedure

| Aspect | Function | Procedure |
|--------|----------|-----------|
| Returns value | Yes (required) | Optional (OUT params) |
| Called in SQL | Yes | No (usually) |
| Side effects | Should not have | Can have |
| Transaction control | Cannot (usually) | Can |
| Used in WHERE/SELECT | Yes | No |

## Severity Factors

| Factor | Score |
|--------|-------|
| Used in computed columns | +5 (DDL change needed to modify) |
| Used in check constraints | +5 (constraint must be dropped first) |
| Used in default values | +4 |
| Called in 10+ places | +3 |
| Called in views | +2 per view |
| Called in procedures | +2 per procedure |
| Return type change | +4 (all callers affected) |
| Parameter change | +3 (all callers affected) |
| Deterministic → Non-deterministic | +3 (index/cache implications) |

## Change Types and Risks

### Return Type Changes

| Change | Risk |
|--------|------|
| Widen type (INT → BIGINT) | Medium - implicit conversion |
| Narrow type | High - overflow/truncation |
| Change type family | Critical - all callers break |

### Parameter Changes

| Change | Risk |
|--------|------|
| Add optional parameter | Low (with default) |
| Add required parameter | High - all callers break |
| Remove parameter | High - callers pass extra args |
| Change parameter type | High - type mismatch |

### Determinism Changes

| Change | Risk |
|--------|------|
| Deterministic → Non-deterministic | High - can't use in indexes/computed |
| Non-deterministic → Deterministic | Low |

## Special Considerations

### Functions in Indexes

```sql
-- Function-based index (Oracle)
CREATE INDEX idx ON table (UPPER(column));

-- If you change UPPER() behavior, index becomes inconsistent!
```

### Functions in Computed Columns

```sql
-- Computed column using function
ALTER TABLE t ADD full_name AS (dbo.get_full_name(first, last));

-- To change the function, must:
-- 1. Drop the computed column
-- 2. Change the function
-- 3. Re-add the computed column
```

### Functions in Check Constraints

```sql
-- Check constraint using function
ALTER TABLE t ADD CONSTRAINT chk CHECK (dbo.is_valid(column) = 1);

-- To change the function, may need to:
-- 1. Drop the constraint
-- 2. Change the function
-- 3. Re-add the constraint
```

## Pre-Change Checklist

- [ ] All call sites identified?
- [ ] Used in computed columns? (Must alter DDL)
- [ ] Used in check constraints? (Must drop/recreate)
- [ ] Used in indexes? (Must rebuild)
- [ ] Return type changing? All callers handle it?
- [ ] Parameters changing? All callers updated?
- [ ] Determinism changing? No index/computed usage?
