```prompt
---
name: Add Column Analysis
description: 'Quick impact analysis for adding a new column to a table'
agent: sql-impact
---

# Add Column Impact Analysis

Analyze the impact of adding a new column to a table.

## Input

Describe the column you want to add in natural language, for example:
- "add email_verified boolean column to customers table"
- "add policy_status varchar(20) to policies, not null, default 'active'"
- "customers table needs a new created_at timestamp column"

## Verification Step

**BEFORE running analysis**, parse the user's input and confirm:

```
📋 I understood:
- **Table**: {extracted_table_name}
- **New Column**: {extracted_column_name}
- **Data Type**: {extracted_type or "not specified - please clarify"}
- **Nullable**: {yes/no/not specified}
- **Default**: {value or "none"}

Is this correct? (yes / no, let me clarify)
```

Wait for user confirmation before proceeding.

## Analysis Focus

After confirmation, analyze:

1. **INSERT statements without column lists**
   - Pattern: `INSERT INTO {table} VALUES`
   - Risk: These will break if column count changes
   
2. **SELECT * queries**
   - Pattern: `SELECT \* FROM {table}`
   - Risk: May return unexpected data

3. **Views on this table**
   - Check for views that SELECT * or need updating

4. **Table size consideration**
   - Large tables may lock during ALTER
   - NOT NULL without DEFAULT requires table rewrite

## Risk Modifiers

Apply these severity adjustments:
- NOT NULL without DEFAULT: **+4** (requires data backfill)
- Large table (known high-volume): **+2** (lock time)
- Has dependent views with SELECT *: **+1** per view
- Critical table: **+2**

## Pre-loaded Context

Reference: `#skill:sql-impact-analysis/references/tables/add-column.md`

## Output

After analysis, provide:
1. Standard impact summary
2. Specific callouts for INSERT/SELECT * issues
3. Recommendation on deployment approach (online vs maintenance window)
```
