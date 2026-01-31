# grep_search Tool Limitations

> **Source:** VS Code Copilot Chat Extension
> **Repository:** [microsoft/vscode-copilot-chat](https://github.com/microsoft/vscode-copilot-chat)
> **File:** [`src/extension/tools/node/findTextInFilesTool.tsx`](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx)

## Summary

The `grep_search` tool (internally `FindTextInFiles`) has hard-coded limits that cannot be overridden by the user or agent.

| Limit | Value | Impact |
|-------|-------|--------|
| **Max Results** | 200 matches | Large codebases may have incomplete results |
| **Timeout** | 20 seconds | Complex regex or broad patterns may timeout |
| **Default Results** | 20 matches | Unless FullContext mode, only 20 returned |

---

## Hard Limits with Code References

### 1. 200 Result Cap

**Location:** [Line 40](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L40)

```typescript
const MaxResultsCap = 200;
```

**Enforcement:** [Line 73](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L73)

```typescript
const maxResults = Math.min(options.input.maxResults ?? 20, MaxResultsCap);
```

**Key Facts:**
- This is **200 text matches**, not 200 files
- A single file with 10 occurrences consumes 10 result slots
- User requesting >200 gets a warning, not more results

---

### 2. 20-Second Timeout

**Location:** [Line 78](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L78)

```typescript
const timeoutInMs = 20_000;
```

**Implementation:** [Lines 80-84](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L80-L84)

```typescript
let results = await raceTimeoutAndCancellationError(
    (searchToken) => this.searchAndCollectResults(options.input.query, isRegExp, patterns, maxResults, includeIgnoredFiles, searchToken),
    token,
    timeoutInMs,
    `Timeout in searching text in files with ${isRegExp ? 'regex' : 'literal'} search, try a more specific search pattern or change regex/literal mode`
);
```

**Key Facts:**
- Hard 20-second timeout per search attempt
- If timeout occurs, LLM receives hint to narrow search
- Automatic retry with opposite regex mode adds another 20s (40s max total)

---

### 3. Default vs FullContext Mode

**Location:** [Lines 218-223](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L218-L223)

```typescript
async resolveInput(input: IFindTextInFilesToolParams, _promptContext: IBuildPromptContext, mode: CopilotToolMode): Promise<IFindTextInFilesToolParams> {
    // ...
    return {
        maxResults: mode === CopilotToolMode.FullContext ? 200 : 20,
        ...input,
        includePattern,
    };
}
```

**Key Facts:**
- **Default mode:** 20 results max
- **FullContext mode:** 200 results max
- Agent cannot override this programmatically

---

### 4. Automatic Fallback Retry

**Location:** [Lines 87-100](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L87-L100)

```typescript
// If we still have no results, we need to try the opposite regex mode
if (!results.length && queryIsValidRegex) {
    results = await raceTimeoutAndCancellationError(
        (searchToken) => this.searchAndCollectResults(options.input.query, !isRegExp, patterns, maxResults, includeIgnoredFiles, searchToken),
        token,
        timeoutInMs,
        `Find ${results.length} results in searching text in files with ${isRegExp ? 'regex' : 'literal'} search...`
    );
}
```

**Key Facts:**
- Zero results triggers automatic retry with opposite mode
- Regex → Literal fallback, or Literal → Regex
- Adds another 20-second potential timeout

---

### 5. Ignore File Escape Hatch

**Location:** [Lines 103-114](https://github.com/microsoft/vscode-copilot-chat/blob/main/src/extension/tools/node/findTextInFilesTool.tsx#L103-L114)

```typescript
let noMatchInstructions: string | undefined = undefined;
if (!results.length && !includeIgnoredFiles) {
    const excludeSettings = this.configurationService.getNonExtensionConfig<Record<string, boolean>>('search.exclude');
    // ...
    noMatchInstructions = `Your search pattern might be excluded completely by either the search.exclude settings or .*ignore files...`;
}
```

**Key Facts:**
- Default behavior respects `.gitignore` and `search.exclude`
- Zero results may be due to filtering, not absence
- `includeIgnoredFiles: true` parameter bypasses this

---

## Implications for SQL Impact Analysis

| Scenario | Problem | Workaround |
|----------|---------|------------|
| Large codebase with 500+ matches | Only first 200 returned | Use module-scoped `includePattern` |
| Complex regex pattern | 20s timeout | Simplify pattern, search multiple times |
| Need comprehensive results | Cap prevents full view | Use Python skill for unbounded search |
| Files in .gitignore | Zero results | Pass `includeIgnoredFiles: true` |

---

## Workaround: Python grep Skill

For scenarios requiring unbounded search:

1. Use `#skill:python-grep-search` when grep_search returns exactly 200 results (limit hit)
2. Python skill has no timeout, no result cap
3. Reads search scope from `.copilot-context.md`
4. Writes results to `copilot_impact_analysis/search_cache/`

See: [Python grep Search Skill](../skills/python-grep-search/SKILL.md)
