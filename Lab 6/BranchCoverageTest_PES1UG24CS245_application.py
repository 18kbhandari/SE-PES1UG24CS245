"""Branch-coverage tests for the Income Tax Calculator (Lab 6)."""

import pytest

from income_tax import refund_status, tax_due, taxable_income


@pytest.mark.parametrize(
    ("gross", "regime", "investments", "expected"),
    [
        (0, "new", 0, 0),                 # taxable < 0 after new-regime deduction
        (75_000, "new", 10_000, 0),        # exact new-regime deduction boundary
        (75_001, "new", 0, 1),
        (50_000, "old", 0, 0),             # taxable < 0 after old-regime deduction
        (200_000, "old", 150_000, 0),      # exact investment-limit boundary
        (200_001, "old", 150_000, 1),
        (500_000, "old", 150_001, 300_000),  # capped investment deduction
    ],
)
def test_taxable_income_branches_and_boundaries(gross, regime, investments, expected):
    """Exercise both regimes, investment cap outcomes, and taxable boundaries."""
    assert taxable_income(gross, regime, investments) == expected


@pytest.mark.parametrize(
    ("gross", "regime", "investments", "message"),
    [(-1, "new", 0, "invalid income"), (100_000, "other", 0, "unknown regime")],
)
def test_taxable_income_exception_branches(gross, regime, investments, message):
    """Exercise both exceptions raised by taxable_income."""
    with pytest.raises(ValueError, match=message):
        taxable_income(gross, regime, investments)


@pytest.mark.parametrize(
    ("taxable", "age", "expected"),
    [
        (250_000, 59, 0),       # non-senior exemption boundary
        (250_001, 59, 0),       # non-senior first slab, integer truncation
        (500_000, 59, 12_500),  # first-slab upper boundary
        (500_001, 59, 12_500),  # higher slab branch
        (300_000, 60, 0),       # senior exemption boundary
        (300_001, 79, 0),       # senior first slab
        (500_000, 80, 0),       # super-senior exemption boundary
        (500_001, 80, 0),       # super-senior first slab
    ],
)
def test_tax_due_all_age_and_slab_branches(taxable, age, expected):
    """Exercise age selection plus exempt, first-slab, and higher-slab paths."""
    assert tax_due(taxable, age) == expected


def test_tax_due_negative_amount_exception_branch():
    """Exercise the invalid taxable-amount exception."""
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-1, 30)


@pytest.mark.parametrize(
    ("tax_paid", "tax_due_amount", "filed_on_time", "expected"),
    [
        (1, 0, True, "refund"),
        (1, 0, False, "refund delayed"),
        (0, 1, True, "pay balance"),
        (0, 1, False, "pay balance with penalty"),
        (0, 0, True, "settled"),
    ],
)
def test_refund_status_true_and_false_branches(
    tax_paid, tax_due_amount, filed_on_time, expected
):
    """Exercise refund, payment, filing-time, and settled branches."""
    assert refund_status(tax_paid, tax_due_amount, filed_on_time) == expected
