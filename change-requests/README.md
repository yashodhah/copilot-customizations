# Change Requests

This folder contains database change request documents created by the `@db-change-intake` agent.

## Workflow

1. **Create**: Run `@db-change-intake` to start a guided intake process
2. **Analyze**: Run `@sql-impact` to perform impact analysis
3. **Review**: Circulate the document for DBA and team lead approval
4. **Deploy**: Once approved, proceed with deployment

## File Naming Convention

```
CR-{YYYYMMDD}-{OBJECT_NAME}.md
```

Examples:
- `CR-20260131-customers_add_email.md`
- `CR-20260131-sp_get_policy_details.md`

## Status Indicators

| Status | Meaning |
|--------|---------|
| 🟡 Pending Review | Awaiting initial review |
| 🟠 Impact Analysis | Impact analysis in progress |
| 🔵 Under Review | Being reviewed by DBA/team |
| 🟢 Approved | Ready for deployment |
| 🔴 Rejected | Change request denied |
| ✅ Deployed | Successfully deployed |

## Quick Commands

```
@db-change-intake   → Start a new change request
@sql-impact         → Run impact analysis on an object
/saveChangeRequest  → Save a change request document
/saveImpactReport   → Save impact analysis results
```
