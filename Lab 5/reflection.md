# Lab 5 – Static Code Analysis Reflection

## 1. What is static code analysis, and why is it useful?

Static code analysis examines source code without running the program. It can identify potential bugs, security weaknesses, and style violations early, making code easier to maintain and helping developers fix problems before deployment.

## 2. What did Pylint, Bandit, and Flake8 identify?

Pylint highlighted code-quality and maintainability issues, including the mutable default argument, naming and documentation problems, and unnecessary use of a global statement. Bandit identified security-sensitive patterns in the original code, including FTP, marshal deserialization, hardcoded credentials, and subprocess usage. Flake8 reported unused imports and formatting problems such as long lines and incorrect blank-line spacing.

## 3. What changes were made to address the issues?

I corrected the annual interest-rate conversion used for EMI, improved loan eligibility and maximum-loan calculations, replaced the mutable default argument, validated loaded JSON records, and used context managers for file handling. I also replaced FTP with SFTP, removed hardcoded credentials, replaced predictable IDs with UUIDs, replaced the subprocess notification call with SMTP support, and corrected naming and formatting issues.

## 4. What did I learn, and what are the limitations of static analysis?

I learned that the three tools complement one another: Pylint focuses on code quality, Flake8 on style, and Bandit on common security risks. After fixing issues, I reran the tools and tested the program. The final Pylint score was 9.79/10, Flake8 reported no violations, and Bandit reported no findings. However, clean reports do not prove that software is completely correct or secure; runtime tests, input testing, and code review are still important.
