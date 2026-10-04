from decimal import Decimal

from withdrawal_engine import (
    calculate_portfolio_withdrawal,
)


def test_portfolio_withdrawal_2027_january():
    result = calculate_portfolio_withdrawal(
        2027,
        1,
    )

    expected_withdrawal = Decimal("3863.66")

    assert (
        result["portfolio_withdrawal"].quantize(
            Decimal("0.01")
        )
        == expected_withdrawal
    )


def test_portfolio_withdrawal_has_no_excess_cash():
    result = calculate_portfolio_withdrawal(
        2027,
        1,
    )

    assert (
        result["excess_cash"].quantize(
            Decimal("0.01")
        )
        == Decimal("0.00")
    )


def test_portfolio_withdrawal_uses_retirement_target():
    result = calculate_portfolio_withdrawal(
        2027,
        1,
    )

    # The retirement plan target is $11,000/month.
    # Actual transaction spending is intentionally
    # not used as the retirement spending requirement.

    assert (
        result["portfolio_withdrawal"]
        > result["actual_spending"]
    )