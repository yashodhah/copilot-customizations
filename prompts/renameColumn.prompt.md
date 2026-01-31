```prompt
---
name: Rename Column Analysis
description: 'Quick impact analysis for renaming a column (high-risk operation)'
agent: sql-impact
---

# Rename Column Impact Analysis

⚠️ **High-Risk Operation**: Column renames are breaking changes. All references must be updated simultaneously.

## Input

Describe the rename in natural language, for example:
- "rename email to email_address in customers table"
- "change customers.phone_number to mobile_phone"
- "policies table: rename policy_id to policy_number"

## Verification Step

**BEFORE running analysis**, parse the user's input and confirm:

```
⚠️ RENAME COLUMN - Breaking Change

📋 I understood:
- **Table**: {extracted_table_name}
- **Current Column**: {old_column_name}
- **New Column**: {new_column_name}

This will BREAK all existing references to {table}.{old_column}.

Is this correct? (yes / no, let me clarify)
```

Wait for user confirmation before proceeding.

## Analysis Focus

After confirmation, perform EXHAUSTIVE search:

### 1. Qualified References (HIGH PRIORITY)
- Pattern: `{TABLE}\.{OLD_COLUMN}`
- Pattern: `{TABLE}\s+\w+\.\s*{OLD_COLUMN}` (aliased)
- These WILL break

### 2. Unqualified References
- Pattern: `{OLD_COLUMN}` in procedures that touch this table
- Context-dependent, need manual review

### 3. Indexes and Constraints
- Check index definitions
- Check foreign key references
- Check check constraints

### 4. Views
- Views selecting this column
- Views may need ALTER

### 5. Procedures/Functions/Triggers
- Any code using this column
- May have embedded column names

### 6. External Systems
- Search for string references in config files
- ORM mappings, API contracts

## Severity Baseline

**Rename operations start at 🟠 High (score: 6)** due to breaking nature.

Additional modifiers:
- Critical table: **+3**
- Foreign key references: **+2** per FK
- Used in indexes: **+1** per index
- External system references found: **+3**
- More than 50 file references: **+2**

## Pre-loaded Context

Reference: `#skill:sql-impact-analysis/references/tables/rename-column.md`

## Output

After analysis, provide:
1. **Comprehensive dependency list** - Miss nothing
2. **Deployment coordination requirements**
3. **Suggested deployment order**:
   - Option A: Big-bang (all changes at once, downtime)
   - Option B: Dual-write migration (add new, migrate, drop old)
4. **Risk assessment for each approach**

## Important Notes

- This analysis must be THOROUGH - missing a reference causes production errors
- Consider recommending the safer "add new column, migrate, drop old" approach
- External systems may need coordinated release
```
