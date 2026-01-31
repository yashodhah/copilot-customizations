```prompt
---
name: Edit Column Analysis
description: 'Quick impact analysis for modifying a column type, size, or constraints'
agent: sql-impact
---

# Edit/Modify Column Impact Analysis

Analyze the impact of modifying an existing column's type, size, or constraints.

## Input

Describe the column modification in natural language, for example:
- "change customers.email from varchar(100) to varchar(255)"
- "make policy_number not null in policies table"
- "change amount column in payments from int to decimal(10,2)"
- "remove default value from status column in claims"

## Verification Step

**BEFORE running analysis**, parse the user's input and confirm:

```
📋 I understood:
- **Table**: {extracted_table_name}
- **Column**: {extracted_column_name}
- **Current**: {current_type_or_constraint or "will look up"}
- **Proposed**: {new_type_or_constraint}
- **Change Type**: {widen/narrow/type-change/constraint-change}

Is this correct? (yes / no, let me clarify)
```

Wait for user confirmation before proceeding.

## Analysis Focus

After confirmation, analyze based on change type:

### For Type/Size Changes:

1. **Data truncation risk** (if narrowing)
   - Pattern: Check if existing data exceeds new size
   - Risk: Data loss or ALTER failure

2. **Implicit conversion issues**
   - Pattern: Code expecting old type behavior
   - Risk: Runtime errors or wrong results

3. **Index rebuild requirements**
   - Indexes on modified columns may need rebuild
   - Risk: Extended lock time

### For Constraint Changes:

1. **Existing data violations**
   - Adding NOT NULL: Check for NULL values
   - Adding CHECK: Verify data satisfies constraint

2. **Application code assumptions**
   - Code may rely on NULLability
   - Default values may be expected

## Risk Modifiers

Apply these severity adjustments:
- Narrowing type (varchar(255)→varchar(100)): **+3**
- Type change (int→varchar): **+4**
- Adding NOT NULL to populated column: **+3**
- Removing NOT NULL: **+1**
- Critical table: **+2**
- Column in WHERE clauses: **+1** per occurrence (query plan changes)

## Pre-loaded Context

Reference: `#skill:sql-impact-analysis/references/tables/modify-column.md`

## Output

After analysis, provide:
1. Standard impact summary
2. Data compatibility assessment
3. Index impact if applicable
4. Recommendation: safe to ALTER online vs needs maintenance window
```
