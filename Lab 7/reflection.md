# Lab 7: Fuzzing for Input Validation Bugs — Reflection

**Student Name:** Kushagra Bhandari  
**SRN:** PES1UG24CS245  
**Course:** Software Engineering Lab (UE22CS341AA2 / UE22CS342AA2)  
**Section / Roll:** Section D, Roll 57  
**Module:** `income_tax_parser.py` / `processor.py`  
**Test Suite:** `test_income_tax_parser.py` / `test_processor.py`  

---

## 1. What is fuzz testing and how does Hypothesis differ from traditional unit testing?

**Fuzz testing (fuzzing)** is a dynamic software testing technique where a system or function is executed with randomized, unexpected, malformed, or boundary-breaking inputs to detect crashes, unhandled exceptions, memory leaks, and security vulnerabilities.

**Hypothesis vs. Traditional Unit Testing:**
- **Traditional Unit Testing (Example-Based):** The developer writes specific test cases with manually chosen inputs (e.g., asserting that `sanitize_string("!hello!") == "hello"`). This approach is heavily biased toward the developer's assumptions and typically validates only the "happy path" or obvious corner cases.
- **Hypothesis (Property-Based Fuzz Testing):** Instead of individual input examples, the tester defines general *properties* or *invariants* that must always hold true (e.g., "for any text or None input, this function must execute without crashing or raising an unhandled exception"). Hypothesis automatically generates hundreds of pseudo-random, diverse inputs across character sets, extreme lengths, and boundary values.
- **Shrinking:** When a failure occurs, Hypothesis automatically performs input minimization ("shrinking"). It systematically reduces a complex failing input to the simplest possible counterexample (e.g., reducing a long Unicode string causing a crash down to `s = ''` or `s = None`), making debugging fast and straightforward.

---

## 2. What categories of bugs did fuzzing uncover in the application that manual testing missed?

When the original application was run manually using sample inputs (`"abcde 1234f"`, `"Rs 12,50,000"`, `"250000-500000:5"`), it appeared to work correctly. However, Hypothesis fuzzing uncovered critical unhandled input validation bugs across all three functions:

### A. Null Pointer / Type Dereference (`AttributeError`)
- **Functions:** `clean_pan()`, `parse_amount()`, `parse_tax_slab()`
- **Failing Input:** `s = None`
- **Issue:** The original functions assumed inputs would always be strings and invoked methods like `.strip()`, `.replace()`, and `.split()` directly. When `None` was provided, Python immediately threw `AttributeError: 'NoneType' object has no attribute 'strip'`.

### B. Unchecked String Conversions (`ValueError`)
- **Function:** `parse_amount()`
- **Failing Inputs:** `s = ''`, `s = 'Rs'`, `s = 'abc'`, `s = '   '`
- **Issue:** After stripping `"Rs"` and commas, empty or alphabetic strings were passed directly to `int(text)`. This resulted in `ValueError: invalid literal for int() with base 10: ''`.

### C. Unsafe Structural Unpacking (`ValueError`)
- **Function:** `parse_tax_slab()`
- **Failing Inputs:** `s = ''`, `s = ':'`, `s = '250000'`, `s = '1:2:3'`
- **Issue:** The code executed `limits, rate = line.split(':')` and `low, high = limits.split('-')` without first checking the length of the split arrays. Any input lacking a colon or hyphen, or containing extra delimiters, caused `ValueError: not enough values to unpack` or `ValueError: too many values to unpack`.

### D. Type Fragility with Non-String Inputs
- **All Functions:**
- When integers, floats, or booleans were supplied instead of strings, string methods raised immediate `AttributeError`.

---

## 3. How does defensive programming protect applications against malformed inputs discovered during fuzzing?

Defensive programming is the practice of designing code under the assumption that unexpected, invalid, or adversarial inputs will occur. The following defensive strategies were implemented:

1. **Explicit Null and Type Checking:**
   - Functions immediately verify if the input is `None` and return safe defaults (e.g., `""` for strings, `0` for numbers, `(0, 0, 0)` for slabs).
   - If a non-string type is passed, functions either convert it safely (`str(pan)`) or return a fallback.

2. **Deliberate Structural Validation (Look Before You Leap - LBYL):**
   - For `parse_tax_slab`, rather than blindly unpacking `line.split(':')`, the code validates `if len(parts) != 2: return (0, 0, 0)`.
   - Limits are split and verified before unpacking.

3. **Exception Envelopes with Safe Fallbacks (Easier to Ask Forgiveness - EAFP):**
   - Integer conversion calls (`int()`) are wrapped in `try...except (ValueError, TypeError, OverflowError)` blocks.
   - If conversion fails (due to invalid text, corrupted inputs, or integer overflow), the function gracefully returns a neutral default (`0` or `(0, 0, 0)`) without crashing the application.

4. **Input Normalization:**
   - Currency prefixes (`"Rs."`, `"Rs"`, `"rs"`, `"₹"`), commas, and extraneous spaces are stripped systematically.
   - All whitespace characters (including tabs and newlines) are collapsed using `''.join(pan.split())`.

---

## 4. Verification and Results Summary

| Metric | Before Fix (Buggy) | After Fix (Defensive) |
|---|---|---|
| `python income_tax_parser.py` (Valid Inputs) | Works (Cleaned: `ABCDE1234F`) | Works (Cleaned: `ABCDE1234F`) |
| `python income_tax_parser.py` (Empty/Malformed) | Crashes (`ValueError` / `AttributeError`) | Handled safely (`""`, `0`, `(0, 0, 0)`) |
| `pytest test_income_tax_parser.py` | **3 FAILED** on buggy code | **6 PASSED** in 0.42s (100+ fuzzed cases/test) |
