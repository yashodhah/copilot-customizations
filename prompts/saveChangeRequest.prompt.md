---
name: Save Change Request
description: 'Save a change request context document that guides analysis and review.'
agent: agent
tools: ["edit"]
---

# Save Change Request Context

Save the change request document to the `change-requests` folder. This is a **context template** that captures details for future reference and guides impact analysis.

## Instructions

1. Generate a filename using: `CR-{YYYYMMDD}-{OBJECT_NAME}.md`
2. Save to: `copilot_client/change-requests/`
3. Use the simplified template below

## Template

```markdown
# Change Request: {OBJECT_NAME}

**ID**: CR-{YYYYMMDD}-{OBJECT_NAME}  
**Created**: {DATE}  
**Ticket**: {JIRA/ServiceNow ID or N/A}

---

## What's Changing?

| Field | Value |
|-------|-------|
| **Object Type** | {TABLE/COLUMN/PROCEDURE/FUNCTION/VIEW/TRIGGER} |
| **Object Name** | {schema.object_name} |
| **Operation** | {ADD/MODIFY/DROP/RENAME} |
| **Module** | {claims/policies/payments/billing/shared/core} |

---

## Technical Details

### Current State
{Describe current object definition or "N/A - new object"}

### Proposed Change
```sql
{DDL statement or description of change}
```

### Column Details (if applicable)
| Column | Current | Proposed | Notes |
|--------|---------|----------|-------|
| {name} | {type/constraint} | {new type/constraint} | {reason} |

---

## Context

### Why?
{Brief business reason - 1-2 sentences}

### Who Requested?
{Team/person and ticket reference}

### Known Dependencies
- {System or module that uses this object}
- {Another known consumer}

---

## Risk Flags

Check all that apply:
- [ ] Critical table (policy, claim, payment, customer, billing)
- [ ] Table has production data
- [ ] Breaking change (removes or renames something)
- [ ] External systems affected
- [ ] Large table (may lock during ALTER)

---

## Impact Analysis

> **Run**: `@sql-impact analyze {OBJECT_NAME}`

| Metric | Value |
|--------|-------|
| Severity | _{pending analysis}_ |
| Files Affected | _{pending analysis}_ |

### Findings Summary
{Paste key findings from @sql-impact or note "pending"}

### Full Report
{Link to `copilot_impact_analysis/` CSV if generated}

---

## Rollback

```sql
-- Rollback DDL (if applicable)
{rollback statement or "N/A - additive change"}
```

---

## Notes

{Any edge cases, concerns, or coordination needed}
```

## After Saving

Tell the user:
1. Document saved to `copilot_client/change-requests/CR-{ID}.md`
2. Run `@sql-impact analyze {OBJECT}` to populate impact section  
3. Share with team for review before deployment
