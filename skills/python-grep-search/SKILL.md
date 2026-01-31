---
name: python-grep-search
description: 'Unbounded regex search for large codebases. Use when grep_search hits 200-result limit or 20-second timeout. No limits, writes CSV results to cache.'
---

# Python grep Search Skill

## Purpose

Overcome VS Code `grep_search` tool limitations:
- **No 200-result cap** - returns all matches
- **No 20-second timeout** - runs to completion
- **CSV output** - lightweight, easy to parse
- **JSON metadata** - structured summary for agent

> **When to Use:** Agent detects `grep_search` returned exactly 200 results (limit hit) or timed out.

## Limitations Reference

See [grep-search-limitations.md](../../research/grep-search-limitations.md) for detailed analysis of VS Code grep_search limits.

---

## Search Scope

**Always read `.copilot-context.md` first** to determine module paths:

```markdown
# From .copilot-context.md
modules:
  - patches/claims/
  - patches/policies/
  - patches/payments/
  - patches/shared/
```

Default scope: All modules listed in `.copilot-context.md`
Override: Pass explicit `search_paths` parameter

---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | Yes | Regex pattern to search |
| `file_glob` | string | No | File pattern (default: `*.sql`) |
| `search_paths` | list | No | Override paths (default: from `.copilot-context.md`) |
| `change_id` | string | Yes | Identifier for this analysis (used in output filename) |
| `case_sensitive` | bool | No | Case sensitivity (default: false) |

---

## Output Format

### 1. JSON Metadata (returned to agent)

```json
{
  "search_phase": "comprehensive",
  "pattern": "customer_email",
  "result_count": 847,
  "files_matched": 156,
  "limit_reached": false,
  "timeout": false,
  "results_file": "copilot_impact_analysis/search_cache/{change_id}_results.csv",
  "metadata_file": "copilot_impact_analysis/search_cache/{change_id}_metadata.json",
  "search_scope": ["patches/claims/", "patches/policies/", "patches/shared/"],
  "duration_seconds": 12.4
}
```

### 2. CSV Results (written to file)

**File:** `copilot_impact_analysis/search_cache/{change_id}_results.csv`

```csv
file_path,line_number,match_content
patches/claims/handlers.sql,42,"SELECT customer_email FROM claims WHERE..."
patches/policies/views.sql,156,"CREATE VIEW v_policy AS SELECT customer_email..."
patches/shared/utils.sql,89,"UPDATE customers SET customer_email = :new_email"
```

**Columns:**
- `file_path` - Relative path from workspace root
- `line_number` - 1-indexed line number
- `match_content` - Matched line content (trimmed, max 200 chars)

### 3. Metadata File (written to file)

**File:** `copilot_impact_analysis/search_cache/{change_id}_metadata.json`

Same as JSON returned to agent, persisted for reference.

---

## Procedure

### Step 1: Read Context

```python
# Load .copilot-context.md to get module paths
context_file = workspace_root / ".copilot-context.md"
modules = parse_modules(context_file)
```

### Step 2: Execute Search

```python
import re
from pathlib import Path

def search_files(pattern, paths, file_glob="*.sql", case_sensitive=False):
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)
    results = []

    for base_path in paths:
        for file in Path(base_path).rglob(file_glob):
            with open(file, 'r', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        results.append({
                            'file_path': str(file.relative_to(workspace_root)),
                            'line_number': line_num,
                            'match_content': line.strip()[:200]
                        })

    return results
```

### Step 3: Write Results

```python
import csv
import json

def write_results(results, change_id, metadata):
    cache_dir = workspace_root / "copilot_impact_analysis" / "search_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Write CSV
    csv_path = cache_dir / f"{change_id}_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file_path', 'line_number', 'match_content'])
        writer.writeheader()
        writer.writerows(results)

    # Write metadata JSON
    json_path = cache_dir / f"{change_id}_metadata.json"
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return csv_path, json_path
```

### Step 4: Return Metadata

Return JSON metadata to agent for parsing. Agent can then:
- Report result count to user
- Read CSV file if detailed analysis needed
- Reference results in subsequent tools

---

## Integration with sql-impact-analysis

### Trigger Condition

Agent detects grep_search limit hit:

```
IF grep_search returns exactly 200 results:
    → "Found 200 results (limit reached). Run comprehensive search?"
    → User confirms
    → Invoke python-grep-search skill
```

### Workflow

```
1. Initial grep_search (fast, 20s timeout, 200 cap)
   ↓
2. Agent checks: result_count == 200?
   ↓ YES
3. Ask user: "Run comprehensive search?"
   ↓ User confirms
4. Invoke python-grep-search (no limits)
   ↓
5. Read CSV results for analysis
   ↓
6. Generate impact report
```

---

## Example Invocation

**Agent prompt:**
```
Run comprehensive search for pattern `customer_email` across all modules.
Change ID: rename-customer-email-2024-01-15
```

**Skill execution:**
```python
# Read context
modules = ["patches/claims/", "patches/policies/", "patches/payments/", "patches/shared/"]

# Search
results = search_files(
    pattern=r"customer_email",
    paths=modules,
    file_glob="*.sql",
    case_sensitive=False
)

# Write
csv_path, json_path = write_results(
    results=results,
    change_id="rename-customer-email-2024-01-15",
    metadata={
        "search_phase": "comprehensive",
        "pattern": "customer_email",
        "result_count": len(results),
        "files_matched": len(set(r['file_path'] for r in results)),
        # ...
    }
)
```

**Returns to agent:**
```json
{
  "result_count": 847,
  "results_file": "copilot_impact_analysis/search_cache/rename-customer-email-2024-01-15_results.csv"
}
```

---

## Cache Management

Results are stored in `copilot_impact_analysis/search_cache/`:

```
copilot_impact_analysis/
  search_cache/
    {change_id}_results.csv      # Full search results
    {change_id}_metadata.json    # Search metadata
```

**Cleanup:** User manually deletes cache when analysis complete, or agent can suggest cleanup after save.
