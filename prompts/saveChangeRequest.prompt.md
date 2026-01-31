---
name: Save Change Request
description: 'Save a completed database change request document for human review and approval tracking.'
agent: agent
tools: ["edit"]
---

# Save Database Change Request

Save the change request document to the `change-requests` folder.

## Instructions

1. Generate a filename using: `CR-{YYYYMMDD}-{OBJECT_NAME}.md`
2. Save to: `copilot_client/change-requests/`
3. Use the template below

## Template

```markdown
# Database Change Request: {OBJECT_NAME}

**Request ID**: CR-{YYYYMMDD}-{OBJECT_NAME}
**Created**: {DATE}
**Status**: 🟡 Pending Review

---

## Change Summary

| Field | Value |
|-------|-------|
| **Object Type** | {TABLE/PROCEDURE/FUNCTION/VIEW/TRIGGER} |
| **Object Name** | {schema.object_name} |
| **Operation** | {ADD/MODIFY/DROP/RENAME} |
| **Ticket** | {JIRA/ServiceNow ID} |
| **Requester** | {name} |
| **Target Date** | {deployment date} |

---

## Technical Details

### Current State
{Describe current object definition or N/A for new objects}

### Proposed Change
```sql
{DDL statement or description}
```

### Affected Columns/Parameters
| Name | Current | Proposed | Notes |
|------|---------|----------|-------|
| | | | |

---

## Business Context

### Justification
{Why is this change needed?}

### Impact if Not Done
{What happens if we don't make this change?}

### Downstream Consumers
- [ ] {System/team 1}
- [ ] {System/team 2}

---

## Risk Assessment

### Risk Factors
| Factor | Applicable | Notes |
|--------|------------|-------|
| Critical table | ☐ Yes / ☐ No | |
| Has production data | ☐ Yes / ☐ No | |
| Breaking change | ☐ Yes / ☐ No | |
| Complex rollback | ☐ Yes / ☐ No | |
| External dependencies | ☐ Yes / ☐ No | |

### Preliminary Risk Level
☐ 🟢 Low  ☐ 🟡 Medium  ☐ 🟠 High  ☐ 🔴 Critical

---

## Pre-Deployment Checklist

### Analysis
- [ ] Impact analysis completed (run `@sql-impact`)
- [ ] Dependencies documented
- [ ] Test cases identified

### Review
- [ ] DBA reviewed change
- [ ] Team lead approved
- [ ] Stakeholders notified

### Deployment Prep
- [ ] Rollback script prepared
- [ ] Deployment window scheduled
- [ ] Monitoring plan in place
- [ ] Communication sent

---

## Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Requester | | | ☐ |
| DBA | | | ☐ |
| Team Lead | | | ☐ |
| Release Manager | | | ☐ |

---

## Impact Analysis Results

> Run `@sql-impact analyze {OBJECT_NAME}` and paste results here

### Summary
| Metric | Value |
|--------|-------|
| Severity | |
| Files Affected | |
| Critical Dependencies | |

### Detailed Findings
{Paste impact analysis output}

---

## Rollback Plan

```sql
-- Rollback DDL
{rollback statement}
```

### Rollback Verification
{How to verify rollback was successful}

---

## Deployment Notes

### Deployment Order
1. {step 1}
2. {step 2}

### Post-Deployment Verification
- [ ] {verification step 1}
- [ ] {verification step 2}

---

## History

| Date | Action | By |
|------|--------|-----|
| {DATE} | Created | {name} |
```

## After Saving

Instruct the user:
1. **Review** the saved document at `copilot_client/change-requests/CR-{ID}.md`
2. **Run impact analysis**: `@sql-impact analyze {OBJECT_NAME}`
3. **Circulate for approval** to DBA and team lead
4. **Update status** in the document as approvals are obtained
