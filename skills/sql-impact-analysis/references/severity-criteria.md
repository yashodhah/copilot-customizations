# Impact Severity Classification

## Severity Levels

### 🔴 Critical (Score: 10+)

**Any ONE of these conditions triggers Critical:**

| Condition | Why Critical |
|-----------|--------------|
| Core business table | Direct revenue/compliance impact |
| PRIMARY KEY or FOREIGN KEY affected | Referential integrity at risk |
| 10+ files reference the object | Wide blast radius |
| External system integration | API contracts, ETL feeds, regulatory reports |
| No rollback path | DROP with data loss, irreversible rename |
| Cascade triggers exist | Change propagates unpredictably |
| Table has audit requirements | Compliance/legal implications |

**Required Actions:**
- [ ] Full architecture review
- [ ] Staging environment validation
- [ ] Documented rollback plan
- [ ] Stakeholder sign-off
- [ ] Off-hours deployment window
- [ ] Monitoring plan post-deployment

---

### 🟠 High (Score: 6-9)

**TWO or more of these conditions:**

| Condition | Score |
|-----------|-------|
| 5-10 files affected | +3 |
| Shared across 2+ services | +2 |
| Used in scheduled jobs/batch processing | +2 |
| Has dependent views or materialized views | +2 |
| Column in WHERE/JOIN clauses | +2 (query performance impact) |
| Part of reporting queries | +2 |

**Required Actions:**
- [ ] Team review required
- [ ] Test in staging environment
- [ ] Notify dependent team owners
- [ ] Plan for rollback
- [ ] Monitor query performance after change

---

### 🟡 Medium (Score: 3-5)

**Characteristics:**

| Condition | Score |
|-----------|-------|
| 2-4 files affected | +2 |
| Single service/module scope | +1 |
| Internal tooling or admin functionality | +1 |
| Additive change (new nullable column) | +1 |
| Change is backward compatible | +1 |

**Required Actions:**
- [ ] Standard code review
- [ ] Basic integration testing
- [ ] Update documentation

---

### 🟢 Low (Score: 0-2)

**Characteristics:**

| Condition | Score |
|-----------|-------|
| 0-1 files affected | +1 |
| Test/development database only | 0 |
| Isolated feature, no dependencies | 0 |
| Fully reversible change | 0 |
| New optional column with default | 0 |

**Required Actions:**
- [ ] Self-review sufficient
- [ ] Local testing

---

## Scoring Calculator

### Base Score by Change Type

| Change Type | Base Score |
|-------------|------------|
| DROP column/table | +5 |
| RENAME column/table | +4 |
| MODIFY column type | +3 |
| ADD NOT NULL column | +3 |
| ADD column with default | +1 |
| ADD nullable column | +0 |
| ADD index | +0 |

### Modifiers

| Factor | Modifier |
|--------|----------|
| Per file affected | +0.5 |
| Core business table | +5 |
| Has foreign keys | +2 |
| Used in WHERE clauses | +1 |
| External API exposure | +3 |
| Audit/compliance table | +3 |
| Test environment only | -3 |
| Has comprehensive tests | -1 |

### Quick Formula

```
Severity Score = Base Score + (Files × 0.5) + Sum(Modifiers)

Critical: Score >= 10
High:     Score 6-9
Medium:   Score 3-5
Low:      Score 0-2
```

---

## Quick Assessment Checklist

Use this checklist during analysis:

```markdown
### Severity Checklist for: [OBJECT_NAME]

**Critical Triggers (any = Critical)**
- [ ] Core business table (policies, claims, customers, payments)
- [ ] Change affects PRIMARY KEY or FOREIGN KEY
- [ ] External system dependency (API, ETL, regulatory)
- [ ] 10+ files reference this object
- [ ] No clear rollback path

**Score Factors**
- [ ] Files affected: ___ (×0.5 = ___)
- [ ] Change type base score: ___
- [ ] Foreign key constraints: +2 if yes
- [ ] Used in WHERE/JOIN: +1 if yes
- [ ] Audit requirements: +3 if yes
- [ ] Test env only: -3 if yes

**Total Score: ___**
**Severity: ___**
```

---

## Domain-Specific Critical Tables

### Insurance Domain

Flag as **Critical** if change affects:

| Table Pattern | Domain |
|---------------|--------|
| `polic*` | Policy master data |
| `claim*` | Claims processing |
| `premium*` | Premium calculations |
| `customer*`, `insured*`, `member*` | Customer/insured party |
| `coverage*` | Coverage details |
| `payment*`, `billing*` | Financial transactions |
| `agent*`, `broker*`, `commission*` | Distribution channel |
| `underwriting*` | Risk assessment |
| `reserve*` | Loss reserves |
| `regulatory*`, `compliance*`, `audit*` | Compliance data |

### General Business

| Table Pattern | Domain |
|---------------|--------|
| `user*`, `account*` | Identity/auth |
| `order*`, `transaction*` | Core business |
| `product*`, `inventory*` | Catalog |
| `payment*`, `invoice*` | Financial |
| `audit*`, `log*` | Compliance |

---

## Output Template

After assessment, output:

```markdown
### Severity Assessment

**Score Breakdown:**
- Base (DROP column): +5
- Files affected (7 × 0.5): +3.5
- Core business table: +5
- Foreign key exists: +2
- **Total: 15.5**

**Classification: 🔴 Critical**

**Critical Factors:**
1. Core business table (policies)
2. Score exceeds threshold (15.5 > 10)

**Required Actions:**
- Full architecture review
- Staging validation required
- Rollback plan mandatory
```
