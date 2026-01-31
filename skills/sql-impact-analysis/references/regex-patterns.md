# SQL Dependency Search Patterns

Use these regex patterns with `grep_search` (set `isRegexp: true`).

## Table References

Search for these patterns, replacing `{TABLE}` with the actual table name.

| Pattern | Finds | Priority |
|---------|-------|----------|
| `FROM\s+{TABLE}(\s\|$\|,)` | SELECT queries | High |
| `JOIN\s+{TABLE}(\s\|$)` | All JOIN types (INNER, LEFT, RIGHT, OUTER) | High |
| `INTO\s+{TABLE}(\s\|$\|\()` | INSERT statements | High |
| `UPDATE\s+{TABLE}(\s\|$)` | UPDATE statements | High |
| `DELETE\s+FROM\s+{TABLE}` | DELETE statements | High |
| `TRUNCATE\s+(TABLE\s+)?{TABLE}` | TRUNCATE statements | Critical |
| `DROP\s+TABLE.*{TABLE}` | DROP statements | Critical |
| `ALTER\s+TABLE\s+{TABLE}` | Schema modifications | Critical |
| `CREATE.*INDEX.*ON\s+{TABLE}` | Index definitions | Medium |

### Combined Table Pattern
For efficient single-search:
```
FROM\s+{TABLE}|JOIN\s+{TABLE}|INTO\s+{TABLE}|UPDATE\s+{TABLE}|DELETE\s+FROM\s+{TABLE}
```

## Column References

Replace `{TABLE}` and `{COLUMN}` with actual names.

| Pattern | Finds | Priority |
|---------|-------|----------|
| `{TABLE}\.{COLUMN}` | Qualified column access | High |
| `SELECT\s+.*{COLUMN}` | Column in SELECT list | Medium |
| `WHERE\s+.*{COLUMN}\s*(=\|<\|>\|IS\|IN\|LIKE)` | Column in WHERE clause | High |
| `ORDER\s+BY\s+.*{COLUMN}` | Column in ORDER BY | Low |
| `GROUP\s+BY\s+.*{COLUMN}` | Column in GROUP BY | Medium |
| `SET\s+{COLUMN}\s*=` | Column in UPDATE SET | High |
| `ON\s+.*{COLUMN}\s*=` | Column in JOIN condition | High |

### Combined Column Pattern
```
{TABLE}\.{COLUMN}|WHERE.*{COLUMN}|SET\s+{COLUMN}|ON.*{COLUMN}\s*=
```

## Stored Procedures & Functions

| Pattern | Finds | Database |
|---------|-------|----------|
| `EXEC\s+{PROC_NAME}` | Procedure execution | SQL Server |
| `EXECUTE\s+{PROC_NAME}` | Procedure execution | SQL Server |
| `CALL\s+{PROC_NAME}` | Procedure call | MySQL, PostgreSQL |
| `SELECT\s+{FUNC_NAME}\(` | Function call in SELECT | All |
| `{FUNC_NAME}\(` | Function invocation | All |

## Views & Triggers

| Pattern | Finds |
|---------|-------|
| `CREATE\s+(OR\s+REPLACE\s+)?VIEW.*{VIEW_NAME}` | View definitions |
| `FROM\s+{VIEW_NAME}` | View usage |
| `CREATE\s+TRIGGER.*ON\s+{TABLE}` | Triggers on table |
| `REFERENCES\s+{TABLE}` | Foreign key constraints |

## Application Code Patterns

These patterns find database references in application code (Python, Java, TypeScript, etc.)

| Pattern | Finds | Context |
|---------|-------|---------|
| `['"\`]{TABLE}['"\`]` | Table name in strings | ORM, raw queries |
| `['"\`]{COLUMN}['"\`]` | Column name in strings | ORM, raw queries |
| `\.query\(.*{TABLE}` | Query method calls | Database drivers |
| `\.execute\(.*{TABLE}` | Execute method calls | Database drivers |
| `@Table.*{TABLE}` | JPA/Hibernate annotations | Java |
| `@Column.*{COLUMN}` | JPA/Hibernate annotations | Java |
| `model:\s*['"]?{TABLE}` | Model definitions | ORMs |
| `tableName:\s*['"]?{TABLE}` | Table name config | ORMs |
| `class\s+{TABLE}` | Model class (if named after table) | ORMs |

## File Type Patterns for `includePattern`

Use these to scope your search:

| Pattern | Targets |
|---------|---------|
| `**/*.sql` | SQL scripts |
| `**/*.py` | Python (SQLAlchemy, Django) |
| `**/*.java` | Java (Hibernate, JDBC) |
| `**/*.ts` | TypeScript (TypeORM, Prisma) |
| `**/*.js` | JavaScript (Sequelize, Knex) |
| `**/*.cs` | C# (Entity Framework) |
| `**/*.xml` | MyBatis mappers, Hibernate config |
| `**/*.yaml,**/*.yml` | ORM configurations |

## Search Strategy

1. **Start broad**: Use combined patterns to get overview
2. **Narrow by file type**: Add `includePattern` for specific languages
3. **Handle case sensitivity**: SQL keywords can be upper/lower case
4. **Watch for aliases**: Tables often have aliases (`FROM customers c`)
5. **Check string literals**: Application code often has table names in strings

## Example Search Sequence

For analyzing impact of changing `customers` table:

```
# Step 1: Find all SQL references
grep_search: "FROM\s+customers|JOIN\s+customers|INTO\s+customers|UPDATE\s+customers"
isRegexp: true
includePattern: "**/*.sql"

# Step 2: Find application code references  
grep_search: "customers"
isRegexp: false
includePattern: "**/*.py,**/*.java,**/*.ts"

# Step 3: Find ORM/model definitions
grep_search: "class\s+Customer|tableName.*customers|@Table.*customers"
isRegexp: true
```
