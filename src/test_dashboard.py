from contextlib import closing
from decimal import Decimal
from pathlib import Path
import sqlite3
import tempfile

from app import (
    SECTIONS,
    _account_view_data,
    _available_transaction_years,
    _overview_rows,
    _transaction_view_data,
)
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


def test_dashboard_transactions_apply_category_overrides_and_summarize():
    database_directory = Path(__file__).resolve().parent.parent / "data" / "db"
    with tempfile.NamedTemporaryFile(
        prefix="dashboard-transactions-",
        suffix=".sqlite",
        dir=database_directory,
        delete=False,
    ) as temporary_database:
        database_path = Path(temporary_database.name)

    try:
        with closing(sqlite3.connect(database_path)) as connection:
            connection.executescript(
                """
                CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT);
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY,
                    account_id INTEGER,
                    transaction_date TEXT,
                    description TEXT,
                    amount NUMERIC,
                    category TEXT,
                    category_override TEXT,
                    merchant TEXT,
                    merchant_override TEXT
                );
                INSERT INTO accounts (id, name) VALUES (1, 'Checking');
                INSERT INTO transactions VALUES
                    (1, 1, '2027-01-04', 'Grocery market', -100, 'Food', 'Groceries', 'Market', NULL),
                    (2, 1, '2027-01-05', 'Power bill', -50, 'Utilities', NULL, NULL, NULL),
                    (3, 1, '2027-02-01', 'Pay deposit', 200, 'Income', NULL, NULL, NULL);
                """
            )

        assert _available_transaction_years(database_path) == [2027]
        data = _transaction_view_data(2027, 1, database_path)

        assert data["monthly_spending"] == Decimal("150")
        assert data["monthly_income"] == Decimal("0")
        assert data["annual_spending"] == Decimal("150")
        assert data["annual_income"] == Decimal("200")
        assert data["categories"] == [
            {"Category": "Groceries", "Spending": Decimal("100")},
            {"Category": "Utilities", "Spending": Decimal("50")},
        ]
        assert data["transactions"][1]["Category"] == "Groceries"
    finally:
        database_path.unlink(missing_ok=True)
