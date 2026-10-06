from decimal import Decimal

from app import SECTIONS, _overview_rows


def test_dashboard_sections_match_established_navigation():
    assert SECTIONS == (
        "Overview",
        "Transactions & Spending",
        "Accounts",
        "Retirement Plan",
        "Social Security",
        "Taxes & Roth Conversions",
    )


def test_dashboard_overview_uses_real_retirement_projection():
    rows = _overview_rows()

    assert len(rows) == 14
    assert rows[0]["Year"] == 2027
    assert rows[-1]["Year"] == 2040
    assert "Withdrawal sources" in rows[0]
    assert "Ending portfolio" in rows[-1]
    assert "Roth IRA" in rows[-1]["Ending account balances"]


def test_dashboard_overview_uses_applied_plan_assumptions():
    rows = _overview_rows(
        {
            "monthly_spending_target": Decimal("12500"),
            "annual_return_assumption": Decimal("0.04"),
            "annual_roth_conversion_target": Decimal("50000"),
        }
    )

    assert rows[0]["Spending"] > Decimal("101621.92")
    assert rows[0]["Roth conversion"] == Decimal("50000")
