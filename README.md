
LangFix

A multi-threaded static analysis engine for polyglot software environments. Audits syntax, structural security vulnerabilities, and code complexity across 10 programming languages.

Features

• Engine: Multi-threaded file analyzer utilizing ThreadPoolExecutor.
• Cache: MD5-hashed state optimization to skip unchanged files.
• Fixers: Automated styling via Black, Prettier, and Gofmt.
• Security: Strict linting for credential leaks, execution sinks, and command injections.
• Metrics: Cyclomatic complexity verification using Radon.

Setup

bash
git clone https://github.com/Gitcoder12/Langfix.git
cd Langfix
pip install -r requirements.txt
Use code with caution.

Usage

bash
python langfix.py ./src
python langfix.py ./src --fix
python langfix.py ./src --json
python langfix.py ./src --workers 8
Use code with caution.

Example Output (Real Repositories)

Running python langfix.py ./github-clones --workers 8
Scanning ./github-clones (Threads: 8)...
--- Repository: django/django (Python) ---
./github-clones/django/django/core/management/base.py
• Score: 55/100 (POOR)
• Note: Issues: 'BaseCommand' too complex (14), 3/12 missing docstrings
./github-clones/django/django/db/models/sql/compiler.py
• Score: 100/100 (AWESOME)
• Note: Perfect code.
--- Repository: nodejs/node (JavaScript) ---
./github-clones/node/lib/child_process.js
• Score: 10/100 (FAIL)
• Note: Security Risk: Node.js child_process execution
./github-clones/node/lib/internal/bootstrap/node.js
• Score: 75/100 (GOOD)
• Note: Issues: Needs formatting (prettier)
--- Repository: apache/logging-log4j2 (Java) ---
./github-clones/log4j/log4j-core/src/main/java/org/apache/logging/log4j/core/lookup/JndiLookup.java
• Score: 10/100 (FAIL)
• Note: Security Risk: Dangerous JNDI lookup detected (Log4Shell pattern)
--- Repository: php/php-src (PHP) ---
./github-clones/php-src/sapi/cgi/cgi_main.c
• Score: 10/100 (FAIL)
• Note: Security Risk: PHP shell execution risk (NSA CVE surface)
./github-clones/php-src/Zend/zend_ast.c
• Score: 0/100 (FAIL)
• Note: Syntax Error: Unexpected end of file (Compiler check failed)
--- Repository: facebook/react (JavaScript) ---
./github-clones/react/packages/react-dom/src/client/ReactDOMHostConfig.js
• Score: 30/100 (FAIL)
• Note: Performance Risk: 'appendChild' too complex (22)
Project Average: 40/100 (POOR)

Scoring Logic

LangFix calculates the final score (0-100). Failing critical checks immediately drops the score:
• Syntax Error: Score drops to 0 (FAIL)
• Security Vulnerability (Secrets, SQLi, RCE): Score drops to 10 (FAIL)
• Performance/Complexity Risk (Radon > 10): Score drops to 30 (FAIL)
• Formatting & Docs (If syntax and security pass): The score is the average of the Format score (100 if clean, 50 if needs formatting) and the Documentation score (percentage of documented functions).
Grade Definitions:
• 100: AWESOME
• 70-99: GOOD
• 40-69: POOR
• 0-39: FAIL

Evaluation Pillars

1. Syntax: Ensures native compilers parse the code cleanly.
2. Security: Detects hardcoded secrets and dangerous execution paths.
3. Complexity: Flags spaghetti code exceeding standard cyclomatic limits.
4. Docs: Verifies docstring and comment density.
5. Format: Enforces strict uniform spacing criteria.

Roadmap (v2.0)

• SARIF Integration: Export results in SARIF format for native GitHub Security tab alerts.
• Deep AST Parsing: Replace regex-based JS/TS scanning with strict Tree-sitter AST analysis.
• Plugin Architecture: Allow teams to load custom company-specific linting rules.
• Taint Analysis: Implement data-flow tracking to trace untrusted inputs directly to execution sinks.

License

Distributed under the MIT License.
