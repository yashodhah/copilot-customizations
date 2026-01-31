# Module-Specific .copilotignore Templates

Use these templates in each module directory to fine-tune what Copilot sees.

---

## Claims Module

**File**: `patches/claims/.copilotignore`

```gitignore
# Claims Module Ignore

# Test fixtures (large)
/test-data/**
/fixtures/**

# Historical claim scripts (pre-2024)
/archive/**
/*_pre2024.sql

# Generated audit procedures (auto-created)
/generated/**
sp_audit_*.sql

# Temporary migration scripts
*_migration_temp.sql
```

---

## Policies Module

**File**: `patches/policies/.copilotignore`

```gitignore
# Policies Module Ignore

# Old policy versions
/archive/**
/v1/**
/legacy/**

# Large data load scripts
*_bulk_load.sql
*_data_fix.sql

# Test policies
/test/**
```

---

## Payments Module

**File**: `patches/payments/.copilotignore`

```gitignore
# Payments Module Ignore

# Sensitive reconciliation scripts
/reconciliation/internal/**

# Bank-specific integrations (third-party)
/vendor/**
/bank-integrations/**

# Historical batches
/archive/**
```

---

## Usage

1. Copy the appropriate template to your module directory
2. Name it `.copilotignore` (no extension)
3. Customize patterns for your specific needs
4. Commit to SVN

Copilot will respect these ignore files when searching.
