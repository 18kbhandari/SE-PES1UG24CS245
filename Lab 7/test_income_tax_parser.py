"""
Hypothesis property-based fuzz tests for Lab 7 - Income Tax Parser.
Tests input validation, invariants, and fallback behavior across
arbitrary strings, None, numeric types, malformed formats, and boundary values.
"""
from hypothesis import given, strategies as st
from income_tax_parser import clean_pan, parse_amount, parse_tax_slab

# Comprehensive fuzzing strategy generating arbitrary text, nulls, numbers, and types
fuzz_input = st.one_of(
    st.text(),
    st.none(),
    st.integers(min_value=-10**12, max_value=10**12),
    st.floats(allow_nan=True, allow_infinity=True),
    st.booleans(),
)


@given(fuzz_input)
def test_clean_pan_no_crash(s):
    """
    clean_pan must never crash on any input.
    Asserts:
    - Return value is always a string.
    - No whitespace characters remain.
    - Result is always uppercase.
    - None or blank inputs return empty string.
    """
    res = clean_pan(s)
    assert isinstance(res, str)
    assert not any(c.isspace() for c in res)
    assert res == res.upper()
    if s is None or (isinstance(s, str) and not s.strip()):
        assert res == ""


@given(fuzz_input)
def test_parse_amount_no_crash(s):
    """
    parse_amount must never crash on any input.
    Asserts:
    - Return value is always an integer.
    - None or empty string input returns fallback 0.
    - Direct integer inputs are preserved.
    """
    res = parse_amount(s)
    assert isinstance(res, int)
    if s is None or (isinstance(s, str) and not s.strip()):
        assert res == 0
    if isinstance(s, int) and not isinstance(s, bool):
        assert res == s


@given(fuzz_input)
def test_parse_tax_slab_no_crash(s):
    """
    parse_tax_slab must never crash on any input.
    Asserts:
    - Return value is always a 3-tuple of integers (low, high, rate).
    - None or non-string inputs return fallback (0, 0, 0).
    - Malformed lines lacking colon or hyphen return (0, 0, 0).
    """
    res = parse_tax_slab(s)
    assert isinstance(res, tuple)
    assert len(res) == 3
    assert all(isinstance(x, int) for x in res)
    if s is None or not isinstance(s, str) or ":" not in s:
        assert res == (0, 0, 0)


# Concrete validation and edge-case tests
def test_clean_pan_expected_behavior():
    """Verify expected happy path and edge-case behavior for clean_pan."""
    assert clean_pan("abcde 1234f") == "ABCDE1234F"
    assert clean_pan("  ab cd  12 34 z  ") == "ABCD1234Z"
    assert clean_pan(None) == ""
    assert clean_pan("") == ""
    assert clean_pan("   ") == ""
    assert clean_pan(12345) == "12345"


def test_parse_amount_expected_behavior():
    """Verify rupee prefixes, commas, and fallback behavior for parse_amount."""
    assert parse_amount("Rs 12,50,000") == 1250000
    assert parse_amount("Rs. 12,50,000") == 1250000
    assert parse_amount("₹12,50,000") == 1250000
    assert parse_amount("  50,000  ") == 50000
    assert parse_amount("Rs -50,000") == -50000
    assert parse_amount(None) == 0
    assert parse_amount("") == 0
    assert parse_amount("Rs") == 0
    assert parse_amount("invalid_amount") == 0
    assert parse_amount(50000) == 50000


def test_parse_tax_slab_expected_behavior():
    """Verify standard slabs, percent signs, and fallback behavior for parse_tax_slab."""
    assert parse_tax_slab("250000-500000:5") == (250000, 500000, 5)
    assert parse_tax_slab("0-250000:0") == (0, 250000, 0)
    assert parse_tax_slab("500000-1000000:20%") == (500000, 1000000, 20)
    assert parse_tax_slab(None) == (0, 0, 0)
    assert parse_tax_slab("") == (0, 0, 0)
    assert parse_tax_slab(":") == (0, 0, 0)
    assert parse_tax_slab("250000-500000") == (0, 0, 0)
    assert parse_tax_slab("invalid:slab") == (0, 0, 0)
