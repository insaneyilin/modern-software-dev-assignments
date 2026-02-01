Fix following issues, and write a report in docs/fix_vulnerabilities.md, the document should contain:

- Show precise edits and explain the mitigation
- For each fixed issue, provide:
  - File and line(s)
  - Rule/category Semgrep flagged
  - Brief risk description
  - Your change (short code diff or explanation, AI coding tool usage)
  - Why this mitigates the issue

Important: Ensure the app still runs and tests still pass after your fixes.

## 1 SQL Injection

SQL Injection with FastAPI:
Untrusted input might be used to build a database query, which can lead to a SQL injection vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to sensitive data, modify, delete data, or execute arbitrary system commands. The driver API has the ability to bind parameters to the query in a safe way. Make sure not to dynamically create SQL queries from user-influenced inputs. If you cannot avoid this, either escape the data properly or create an allowlist to check the value.

SQL Injection with aiosqlite via fastapi/fastapi-without-url-path:
- Untrusted input might be used to build a database query, which can lead to a SQL injection vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to sensitive data, modify, delete data, or execute arbitrary system commands. To prevent this vulnerability, use prepared statements that do not concatenate user-controllable strings and use parameterized queries where SQL commands and user data are strictly separated. Also, consider using an object-relational (ORM) framework to operate with safer abstractions.

Related files:
- week6/backend/app/routers/action_items.py:33
- week6/backend/app/routers/notes.py:33
- week6/backend/app/routers/notes.py:80

## 2 Code Injection with FastAPI

The application might dynamically evaluate untrusted input, which can lead to a code injection vulnerability. An attacker can execute arbitrary code, potentially gaining complete control of the system. To prevent this vulnerability, avoid executing code containing user input. If this is unavoidable, validate and sanitize the input, and use safe alternatives for evaluating user input.

Related files:
- week6/backend/app/routers/notes.py:104

## 3 SQL Injection with SQLAlchemy

Untrusted input might be used to build a database query, which can lead to a SQL injection vulnerability. An attacker can execute malicious SQL statements and gain unauthorized access to sensitive data, modify, delete data, or execute arbitrary system commands. Use the SQLAlchemy ORM provided functions to build SQL queries instead to avoid SQL injection.

Related files:
- week6/backend/app/routers/notes.py:72
