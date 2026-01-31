---
name: saveImpactReport
description: 'Save the impact analysis results from the current conversation as CSV and markdown files for team sharing'
tools: ["edit"]
agent: "agent"
argument-hint: "Optional: filename prefix (default: impact-report)"
---

Save the SQL impact analysis from this conversation to files.

## Instructions

1. **Extract data** from the previous impact analysis response:
   - Find the markdown summary section
   - Find the CSV code blocks (detailed findings and summary)

2. **Generate filenames** using the pattern:
   - `{prefix}-{object-name}-{date}.csv` for detailed findings
   - `{prefix}-{object-name}-{date}-summary.csv` for summary
   - `{prefix}-{object-name}-{date}.md` for full markdown report
   - Use today's date in `YYYY-MM-DD` format
   - Default prefix is `impact-report` if not specified
   - Sanitize object name (replace spaces/special chars with hyphens)

3. **Save files** to `.github/impact-reports/` directory:
   - Create the directory if it doesn't exist
   - Write the detailed CSV
   - Write the summary CSV
   - Write the markdown report

4. **Confirm** with the user:
   - List the files created
   - Provide the full paths

## Example Output

If the analysis was for "customers.email" column on 2026-01-31:

```
Created impact analysis reports:

- .github/impact-reports/impact-report-customers-email-2026-01-31.csv (detailed findings)
- .github/impact-reports/impact-report-customers-email-2026-01-31-summary.csv (summary metrics)
- .github/impact-reports/impact-report-customers-email-2026-01-31.md (full report)

You can import the CSV files into Excel or share the markdown with your team.
```

## Excel Formatting (Optional)

If the user wants styled Excel output, suggest:

> "The CSV files are ready. To create a formatted Excel report with styling,
> you can use an Excel skill: `@excel-skill format impact-report`"

Or if Excel formatting is explicitly requested, hand off to the Excel skill after saving CSV.
