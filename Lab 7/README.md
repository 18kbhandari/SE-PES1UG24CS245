# L6_L7_57 — Income Tax Calculator

**Lab 7: Fuzzing for Input Validation Bugs**  
**Student:** Kushagra Bhandari  
**SRN:** PES1UG24CS245  
**Course:** Software Engineering Lab (UE22CS341AA2 / UE22CS342AA2)  
**Section / Roll:** Section D, Roll 57  
**Python Version:** Python 3.8+ (Verified on Python 3.10.11)  

---

## 1. Project Objective

The objective of Lab 7 is to explore **property-based fuzz testing** as a software quality assurance and defensive programming technique using **Hypothesis** and **Pytest**. 

Unlike standard unit testing, which typically tests predictable inputs along the "happy path", fuzz testing automatically feeds unexpected, malformed, randomized, boundary, and null data into functions to detect unhandled exceptions, type errors, and parsing crashes. The uncovered bugs are then systematically resolved through **defensive programming**, guaranteeing robustness against arbitrary user input.

---

## 2. Tools and Libraries Used

- **Python 3.8+**: Language runtime.
- **Pytest**: Test execution framework.
- **Hypothesis**: Property-based fuzz testing library for Python. Generates randomized test inputs and automatically minimizes failing cases (shrinking).

---

## 3. Description of the Application Functions

The module `income_tax_parser.py` parses user-provided income tax details:

1. **`clean_pan(pan)`**:
   - Takes a PAN string (e.g. `"abcde 1234f"`).
   - Removes all internal and surrounding whitespace.
   - Converts all characters to uppercase (`"ABCDE1234F"`).
   - Safely handles `None`, non-string types, and blank inputs, returning an empty string `""` where appropriate.

2. **`parse_amount(text)`**:
   - Parses a currency amount string into an integer.
   - Robustly handles Indian rupee formatting variations including `"Rs 12,50,000"`, `"Rs. 12,50,000"`, `"₹12,50,000"`, and `"INR 12,50,000"`.
   - Removes currency symbols, commas, and whitespace.
   - Safely converts valid strings and direct numeric types into integers.
   - Encloses conversion in exception envelopes and returns `0` as fallback on malformed or empty inputs without crashing.

3. **`parse_tax_slab(line)`**:
   - Parses tax bracket expressions formatted as `LOW-HIGH:RATE` (e.g. `"250000-500000:5"`, `"500000-1000000:20%"`).
   - Validates delimiters (`:` and `-`) before unpacking.
   - Supports positive and negative boundary limits.
   - Safely returns a 3-tuple of integers `(low, high, rate)`.
   - Returns safe default `(0, 0, 0)` for `None`, non-string, or malformed inputs without crashing.

---

## 4. Bugs Discovered via Hypothesis Fuzzing

Running `pytest test_income_tax_parser.py` against the initial starter code immediately uncovered multiple critical failures:

| Function | Vulnerability | Shrunk Failing Input | Exception Raised | Root Cause |
|---|---|---|---|---|
| `clean_pan()` | Unhandled `None` / invalid types | `s = None` | `AttributeError: 'NoneType' object has no attribute 'strip'` | Assumed input is always a string and called `.strip()` directly. |
| `parse_amount()` | Unhandled `None` & empty string | `s = None`<br>`s = ''` | `AttributeError: 'NoneType' object has no attribute 'replace'`<br>`ValueError: invalid literal for int() with base 10: ''` | Called `.replace()` on null input; passed empty string or non-numeric text directly to `int()`. |
| `parse_tax_slab()` | Unsafe tuple unpacking on `.split()` | `s = None`<br>`s = ''`<br>`s = ':'` | `AttributeError: 'NoneType' object has no attribute 'split'`<br>`ValueError: not enough values to unpack (expected 2, got 1)` | Called `.split()` on `None`; blindly unpacked lists into variables without validating length. |

---

## 5. Defensive Fixes Implemented

1. **`clean_pan(pan)`**:
   - Check `if pan is None: return ""`.
   - If `pan` is not a string, coerce via `str(pan)`.
   - Remove all whitespace characters safely using `''.join(pan.split()).upper()`.

2. **`parse_amount(text)`**:
   - Returns `0` if `text is None` or invalid type. Directly returns `int(text)` if numeric integer/float.
   - Systematically cleans currency indicators (`"Rs."`, `"Rs"`, `"rs"`, `"RS"`, `"₹"`, `"INR"`, `"inr"`), commas, and spaces.
   - Wraps conversion in `try...except (ValueError, TypeError, OverflowError)` returning default `0`.

3. **`parse_tax_slab(line)`**:
   - Returns `(0, 0, 0)` if `line is None` or not a string.
   - Splits on `:` and verifies `len(parts) == 2`.
   - Strips optional `%` from rate.
   - Splits limits on `-` supporting standard bounds and negative numbers.
   - Wraps conversions in `try...except (ValueError, TypeError, OverflowError)` returning default `(0, 0, 0)`.

---

## 6. How to Install Dependencies

From inside the `LAB7` folder:
```bash
pip install -r requirements.txt
```
Or directly:
```bash
pip install hypothesis pytest
```

---

## 7. How to Run the Application

```bash
python income_tax_parser.py
```
**Sample Inputs:**
- Enter a PAN: `abcde 1234f`
- Enter an amount: `Rs 12,50,000`
- Enter a tax slab: `250000-500000:5`

**Output:**
```
==== Running clean_pan ====
Enter a PAN (e.g. abcde 1234f): Cleaned PAN: ABCDE1234F

==== Running parse_amount ====
Enter an amount (e.g. Rs 12,50,000): Amount in rupees: 1250000

==== Running parse_tax_slab ====
Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): Tax slab (low, high, rate): (250000, 500000, 5)
```

---

## 8. How to Execute the Tests

Run the test suite with Pytest:
```bash
python -m pytest test_income_tax_parser.py -v
```

---

## 9. Final Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\bhand\Desktop\L6_L7_57_income_tax\LAB7
plugins: anyio-4.16.0, hypothesis-6.168.5, platformdirs-4.12.4
collected 6 items

test_income_tax_parser.py::test_clean_pan_no_crash PASSED                [ 16%]
test_income_tax_parser.py::test_parse_amount_no_crash PASSED             [ 33%]
test_income_tax_parser.py::test_parse_tax_slab_no_crash PASSED           [ 50%]
test_income_tax_parser.py::test_clean_pan_expected_behavior PASSED       [ 66%]
test_income_tax_parser.py::test_parse_amount_expected_behavior PASSED    [ 83%]
test_income_tax_parser.py::test_parse_tax_slab_expected_behavior PASSED  [100%]

============================== 6 passed in 0.42s ==============================
```
- **Fuzzing Coverage**: Over 100 random, boundary, null, and malformed inputs tested per function with **zero crashes**.
- **Behavioral Verification**: Formatted rupee strings, uppercase conversion, whitespace removal, and fallback returns verified.

---

## 10. Deliverables and File Organization

```text
LAB7/
│
├── README.md                                 # Comprehensive lab documentation
├── income_tax_parser.py                      # Hardened application file
├── test_income_tax_parser.py                 # Completed Hypothesis test suite
├── requirements.txt                          # Dependencies (hypothesis, pytest)
├── reflection.md                             # Answers to the 3 reflection questions
├── PES1UG24CS245_Kushagra_Bhandari_LAB7.pdf  # Final submission PDF with screenshots & reflection
│
└── screenshots/
    ├── SS1_original_application_output.png   # Output of original application
    ├── SS2_failing_hypothesis_tests.png      # Failing Hypothesis tests on buggy code
    ├── SS3_fixed_application_output.png      # Output of fixed application
    └── SS4_passing_hypothesis_tests.png      # Passing Hypothesis tests on fixed code
```
