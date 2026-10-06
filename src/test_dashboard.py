from decimal import Decimal

from app import SECTIONS, _account_view_data, _overview_rows
from real_retirement_scenario import run_real_retirement_scenario


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


def test_dashboard_accounts_match_real_retirement_projection():
    summary, balances, withdrawals = _account_view_data()
    results = run_real_retirement_scenario()

    assert len(summary) == 6
    assert summary[0]["Account"] == "Chris 401(k)"
    assert summary[0]["Starting balance"] == results[0].beginning_balances[
        "Chris 401(k)"
    ]
    assert summary[0]["Ending balance"] == results[-1].ending_balances[
        "Chris 401(k)"
    ]
    assert len(balances) == 14 * 6
    assert {row["Year"] for row in balances} == set(range(2027, 2041))
    assert sum(
        (row["Withdrawal"] for row in withdrawals), Decimal("0")
    ) == sum((result.gross_withdrawal for result in results), Decimal("0"))


def test_dashboard_accounts_use_applied_plan_assumptions():
    assumptions = {
        "monthly_spending_target": Decimal("12500"),
        "annual_return_assumption": Decimal("0.04"),
        "annual_roth_conversion_target": Decimal("50000"),
    }
    _, balances, _ = _account_view_data(assumptions)
    _, default_balances, _ = _account_view_data()

    assert balances[0]["Balance"] != default_balances[0]["Balance"]
