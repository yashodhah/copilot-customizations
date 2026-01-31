```prompt
---
name: Drop Column Analysis
description: 'Quick impact analysis for dropping a column (destructive operation)'
agent: sql-impact
---

# Drop Column Impact Analysis

🔴 **Destructive Operation**: Dropping a column permanently deletes all data in that column. This cannot be undone.

## Input

Describe the drop in natural language, for example:
- "drop the legacy_id column from customers table"
- "remove fax_number from contacts"
- "policies table: drop the deprecated_flag column"

## Verification Step

**BEFORE running analysis**, parse the user's input and confirm:

```
🔴 DROP COLUMN - Destructive & Irreversible

📋 I understood:
- **Table**: {extracted_table_name}
- **Column to Drop**: {column_name}

⚠️ WARNING: All data in this column will be PERMANENTLY DELETED.
⚠️ WARNING: All code referencing this column will BREAK.

Is this correct? (yes / no, let me clarify)
```

Wait for user confirmation before proceeding.

## Analysis Focus

After confirmation, perform EXHAUSTIVE search:

### 1. ALL Code References (CRITICAL)
- Pattern: `{TABLE}\.{COLUMN}`
- Pattern: `{COLUMN}` in context of {TABLE}
- Pattern: String literals `'{COLUMN}'`
- Every reference found = code that will break

### 2. Data Assessment
- Is there data in this column?
- Is the data used anywhere?
- Has it been migrated elsewhere?

### 3. Foreign Key Check
- Is this column a FK target?
- Are other tables referencing it?
- FK constraints must be dropped first

### 4. Index Check
- Is column part of any index?
- Indexes must be modified/dropped first

### 5. Views and Procedures
- Views selecting this column
- Procedures using this column
- Triggers referencing this column

### 6. Application Layer
- ORM mappings
- API responses including this field
- Reports/exports using this column

## Severity Baseline

**Drop operations start at 🟠 High (score: 7)** due to data loss.

Escalation to 🔴 Critical if:
- Column has data: **+3**
- Critical table: **+3**
- Foreign key references exist: **+4**
- More than 10 code references: **+2**
- External system references: **+3**

## Pre-loaded Context

Reference: `#skill:sql-impact-analysis/references/tables/drop-column.md`

## Output

Use the **consistent output format** from sql-impact agent:
1. Markdown summary with all standard fields (severity, total matches, search scope)
2. Dependencies table (all matches, or top 25 if >25)
3. CSV data in chat (always)
4. Risk factors and recommendations
5. Offer `/saveImpactReport` to export

After analysis, also include:
1. **Data status**: Empty or has data?
2. **Complete dependency list** - Miss nothing
3. **Prerequisites**:
   - FKs to drop first
   - Indexes to modify
   - Views to update
4. **Code changes required** before drop
5. **Deployment sequence**:
   1. Deploy code changes (stop writing to column)
   2. Verify no reads
   3. Drop FK constraints
   4. Drop column
   5. Clean up indexes
6. **Rollback assessment**: Can we recover? (Usually: NO)

## Important Notes

- This analysis must be EXHAUSTIVE
- Recommend deprecation period if column has data
- Consider soft-delete approach (rename to `_deprecated_{column}`) as safer alternative
- If column has data, strongly recommend data export before drop
```
