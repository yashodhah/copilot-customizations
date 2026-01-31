```prompt
---
name: generateImpactExcel
description: 'Generate a business-friendly Excel report from SQL impact analysis CSV'
tools: ["read", "edit"]
agent: "agent"
argument-hint: "Optional: path to CSV file (default: uses most recent in copilot_impact_analysis/)"
---

Generate an Excel report from SQL impact analysis results for business stakeholders.

## When to Use

Run this after `/saveImpactReport` or when `@sql-impact` auto-saves CSV for 100+ matches.
Creates a formatted Excel file suitable for:
- Business stakeholder review
- Change approval meetings
- Audit documentation
- Team coordination

## Instructions

### 1. Find the Source CSV

If no path provided, look for the most recent CSV in `copilot_impact_analysis/`:
```
ls -t copilot_impact_analysis/*.csv | head -1
```

Expected CSV format:
```csv
file_path,line_number,match_type,risk_level,pattern_matched,code_snippet
```

### 2. Read and Parse CSV

Use `read` tool to get the CSV content.

### 3. Generate Excel Structure

Create an Excel file with these sheets:

#### Sheet 1: Executive Summary

| Metric | Value |
|--------|-------|
| Report Title | SQL Impact Analysis: {object_name} |
| Generated | {date} |
| Change Type | {type} |
| Overall Severity | {🔴/🟠/🟡/🟢} {level} |
| Total Files Affected | {count} |
| 🔴 Risks (Must Fix) | {count} |
| 🟡 Review Needed | {count} |
| 🟢 Safe (Info Only) | {count} |
| Recommendation | {based on severity} |

#### Sheet 2: Risk Summary (🔴 Must Address)

| # | File Path | Line | Type | Risk Reason | Code Snippet |
|---|-----------|------|------|-------------|--------------|
| 1 | {path} | {line} | {type} | {why it's a risk} | {snippet} |

- Sort by: Type (proc, trigger, view first), then alphabetically
- Include ALL 🔴 Risk items
- Add conditional formatting: red background

#### Sheet 3: Review Items (🟡 Check These)

| # | File Path | Line | Type | Pattern | Code Snippet | Decision |
|---|-----------|------|------|---------|--------------|----------|
| 1 | {path} | {line} | {type} | {pattern} | {snippet} | {blank for user to fill} |

- Include ALL 🟡 Review items
- Add "Decision" column for stakeholder sign-off
- Yellow background

#### Sheet 4: Safe References (🟢 Info Only)

| # | File Path | Line | Type | Pattern | Code Snippet |
|---|-----------|------|------|---------|--------------|
| 1 | {path} | {line} | {type} | {pattern} | {snippet} |

- Include ALL 🟢 Safe items
- Green background
- Collapsed by default (if Excel supports)

#### Sheet 5: Raw Data

Full CSV data for filtering/pivoting:
- All columns from source CSV
- Enable auto-filter
- Freeze header row

### 4. Save Excel File

Save to: `copilot_impact_analysis/{object_name}-{date}-report.xlsx`

### 5. Confirm with User

```markdown
## Excel Report Generated ✅

📊 **File**: `copilot_impact_analysis/{object}-{date}-report.xlsx`

### Contents:
| Sheet | Purpose | Rows |
|-------|---------|------|
| Executive Summary | One-page overview | 1 |
| 🔴 Risks | Must address before change | {n} |
| 🟡 Review | Needs team decision | {n} |
| 🟢 Safe | Informational only | {n} |
| Raw Data | Full data for analysis | {total} |

### Next Steps:
1. Open Excel and review 🔴 Risks sheet
2. Discuss 🟡 Review items with team
3. Get sign-off in Decision column
4. Attach to change request ticket
```

## Excel Formatting Guidelines

### Colors
- 🔴 Risk rows: Light red background (#FFCCCC)
- 🟡 Review rows: Light yellow background (#FFFFCC)
- 🟢 Safe rows: Light green background (#CCFFCC)
- Headers: Bold, dark background (#4472C4), white text

### Column Widths
- File Path: 50 characters
- Line: 8 characters
- Type: 12 characters
- Pattern/Reason: 30 characters
- Code Snippet: 60 characters
- Decision: 20 characters

### Data Validation
- Decision column: Dropdown with options: "Approved", "Needs Update", "Defer", "N/A"

## Notes

- If CSV has more than 10,000 rows, warn user about Excel performance
- If no CSV found, prompt user to run `@sql-impact` first
- This prompt uses existing Excel generation skills in the codebase
```
