"""Statement-coverage tests for the Income Tax Calculator (Lab 6)."""

import pytest

from income_tax import refund_status, tax_due, taxable_income


@pytest.mark.parametrize(
    ("gross", "regime", "investments", "expected"),
    [
        (1_000_000, "new", 0, 925_000),
        (100_000, "new", 0, 25_000),
        (200_000, "old", 100_000, 50_000),
        (500_000, "old", 200_000, 300_000),
        (40_000, "old", 0, 0),
    ],
)
def test_taxable_income_for_each_regime_and_deduction_case(
    gross, regime, investments, expected
):
    """Calculate taxable income for new/old regimes and deduction boundaries."""
    assert taxable_income(gross, regime, investments) == expected


@pytest.mark.parametrize(
    ("gross", "regime", "expected_message"),
    [(-1, "new", "invalid income"), (100_000, "invalid", "unknown regime")],
)
def test_taxable_income_rejects_invalid_values(gross, regime, expected_message):
    """Reject negative gross income and an unsupported regime."""
    with pytest.raises(ValueError, match=expected_message):
        taxable_income(gross, regime, 0)


@pytest.mark.parametrize(
    ("taxable", "age", "expected"),
    [
        (200_000, 30, 0),
        (300_000, 30, 2_500),
        (800_000, 60, 62_500),
        (600_000, 80, 5_000),
    ],
)
def test_tax_due_for_exemption_and_tax_slabs(taxable, age, expected):
    """Calculate zero, first-slab, and higher-slab tax for all age groups."""
    assert tax_due(taxable, age) == expected


def test_tax_due_rejects_negative_taxable_amount():
    """A negative taxable amount is invalid."""
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-1, 30)


@pytest.mark.parametrize(
    ("tax_paid", "tax_due_amount", "filed_on_time", "expected"),
    [
        (10_000, 5_000, True, "refund"),
        (10_000, 5_000, False, "refund delayed"),
        (5_000, 10_000, True, "pay balance"),
        (5_000, 10_000, False, "pay balance with penalty"),
        (10_000, 10_000, True, "settled"),
    ],
)
def test_refund_status_for_every_outcome(
    tax_paid, tax_due_amount, filed_on_time, expected
):
    """Report each refund, payment, and settled outcome."""
    assert refund_status(tax_paid, tax_due_amount, filed_on_time) == expected
