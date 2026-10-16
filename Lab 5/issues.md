# Lab 5 – Static Code Analysis Issues

## Overview

The original `loan_calculator.py` was analysed with Pylint, Bandit, and Flake8 before changes were made. The initial Pylint score was **5.17/10**. The line numbers below refer to the original version of the script.

## Issues Identified and Fixes Applied

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Insecure FTP transfer | Security – High (Bandit B402, B321) | 3, 68–71 | The original code used FTP, which does not encrypt credentials or transferred data. | Replaced FTP with Paramiko SFTP and system host-key checking. Credentials and host are read from environment variables. |
| Unsafe `marshal` deserialization | Security – Medium (Bandit B302) | 4, 63–65 | Loading serialized data with `marshal` can be unsafe for untrusted data. | Replaced the binary marshal format with JSON and validated the loaded record structure. |
| Hardcoded credentials | Security (Bandit B107) | 67–69 | The original upload function contained a default username and password in source code. | Removed credential defaults and read the username and password from environment variables. |
| Subprocess mail command | Security / reliability (Bandit B404, B607, B603; Pylint W1510) | 6, 73–74 | The original notification function invoked the system `mail` command without checking its result. | Replaced the subprocess call with Python's SMTP email support and added input validation and a timeout. |
| Predictable application IDs | Security / reliability (Bandit B311) | 5, 50–51 | The original IDs were generated using the non-cryptographic `random` module. | Used UUID-based identifiers instead. |
| Mutable default argument | Code quality (Pylint W0102) | 20 | The default list was shared across calls, so one call could affect later calls. | Changed the default to `None` and created a fresh list inside the function. |
| Incorrect annual-rate conversion in EMI | Logic error | 14–16 | The original calculation treated the annual percentage rate as if it were already a monthly rate, producing incorrect EMI values. | Converted the annual percentage rate to a monthly decimal rate before calculating EMI. |
| Eligibility logic and loan-type validation | Logic error | 20–31 | An early condition could approve an applicant without validating the loan type or all eligibility rules. | Validated the loan type and applied age, income, credit-score, and FOIR checks before approving. |
| Incorrect maximum-loan calculation and built-in shadowing | Logic / code quality (Pylint W0622, W0612, W0613) | 33–37 | The original function shadowed Python's built-in `sum`, used an unused loop variable, and added the same payment repeatedly instead of calculating an affordable principal. | Renamed the function to snake_case and calculated the principal supported by the available payment, term, and interest rate. |
| Files not closed reliably | Reliability (Pylint R1732; Flake8 style context) | 55–65, 70 | Files were opened manually and closed later, so an exception could leave a file open. | Used `with open(...)` context managers for JSON file operations. |
| Missing validation for invalid credit scores | Logic error | 81–90 | Scores above the supported range could be assigned a low-risk band. | Added explicit credit-score range validation and return `INVALID` for out-of-range values. |
| Style, naming, and formatting issues | Code quality / style (Pylint, Flake8) | Throughout; see `pylint_before.txt` and `flake8_before.txt` | The original file contained unused imports, non-snake-case function names, missing docstrings, long lines, and blank-line/formatting violations. | Removed unused imports, added docstrings, used snake_case names, and formatted the file with autopep8. |

## Verification

- Initial Pylint score: **5.17/10**
- Final Pylint score: **9.79/10**
- Final Flake8 report: no violations reported
- Final Bandit report: no findings reported

The saved before-and-after reports provide the tool output used to verify these changes. Static analysis results do not guarantee that every possible bug or security risk has been eliminated.
