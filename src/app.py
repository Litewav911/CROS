from contextlib import closing
from decimal import Decimal
import sqlite3

import pandas as pd
import streamlit as st

from database import DATABASE_PATH
from real_retirement_scenario import run_real_retirement_scenario
from retirement_accounts import RETIREMENT_ACCOUNTS
from retirement_report import build_retirement_report
from retirement_plan import PLAN


SECTIONS = (
    "Overview",
    "Transactions & Spending",
    "Accounts",
    "Retirement Plan",
    "Social Security",
    "Taxes & Roth Conversions",
)


def _money(value: Decimal) -> str:
    return f"${value:,.0f}"


def _default_plan_assumptions() -> dict[str, Decimal]:
    return {
        "monthly_spending_target": PLAN.monthly_spending_target,
        "annual_return_assumption": PLAN.annual_return_assumption,
        "annual_roth_conversion_target": (
            PLAN.annual_roth_conversion_target
        ),
    }


def _current_plan_assumptions() -> dict[str, Decimal]:
    return st.session_state.get(
        "plan_assumptions",
        _default_plan_assumptions(),
    )


def _overview_rows(
    plan_assumptions: dict[str, Decimal] | None = None,
) -> list[dict[str, object]]:
    if plan_assumptions is None:
        plan_assumptions = _default_plan_assumptions()

    results = run_real_retirement_scenario(
        monthly_spending_target=(
            plan_assumptions["monthly_spending_target"]
        ),
        annual_return_assumption=(
            plan_assumptions["annual_return_assumption"]
        ),
        annual_roth_conversion_target=(
            plan_assumptions["annual_roth_conversion_target"]
        ),
    )
    report = build_retirement_report(results)

    return [
        {
            "Year": row.year,
            "Beginning portfolio": row.beginning_portfolio,
            "Spending": row.planned_spending,
            "Outside income": row.total_income,
            "Gross withdrawal": row.gross_withdrawal,
            "Withdrawal tax": row.withdrawal_tax,
            "Roth conversion": row.roth_conversion,
            "Conversion tax": row.roth_conversion_tax,
            "Ending portfolio": row.ending_portfolio,
            "Ending account balances": dict(row.ending_balances),
            "Withdrawal sources": ", ".join(
                f"{name}: {_money(amount)}"
                for name, amount in row.withdrawal_sources.items()
            ) or "None",
            "Market decline": "Yes" if row.market_decline else "No",
        }
        for row in report
    ]


def _account_view_data(
    plan_assumptions: dict[str, Decimal] | None = None,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    if plan_assumptions is None:
        plan_assumptions = _default_plan_assumptions()

    results = run_real_retirement_scenario(
        monthly_spending_target=(
            plan_assumptions["monthly_spending_target"]
        ),
        annual_return_assumption=(
            plan_assumptions["annual_return_assumption"]
        ),
        annual_roth_conversion_target=(
            plan_assumptions["annual_roth_conversion_target"]
        ),
    )
    if not results:
        return [], [], []

    metadata = {
        account.name: account
        for account in RETIREMENT_ACCOUNTS
    }
    account_names = list(results[0].beginning_balances)
    total_withdrawals = {
        name: sum(
            (result.withdrawal_allocations.get(name, Decimal("0"))
             for result in results),
            Decimal("0"),
        )
        for name in account_names
    }
    summary_rows = []
    balance_rows = []
    withdrawal_rows = []

    for name in account_names:
        account = metadata.get(name)
        summary_rows.append(
            {
                "Account": name,
                "Owner": account.owner if account else "—",
                "Type": account.account_type if account else "—",
                "Tax treatment": account.tax_treatment if account else "—",
                "Starting balance": results[0].beginning_balances[name],
                "Ending balance": results[-1].ending_balances[name],
                "Total withdrawals": total_withdrawals[name],
            }
        )

    for result in results:
        for name, balance in result.ending_balances.items():
            balance_rows.append(
                {"Year": result.year, "Account": name, "Balance": balance}
            )
        for name, amount in result.withdrawal_allocations.items():
            withdrawal_rows.append(
                {"Year": result.year, "Account": name, "Withdrawal": amount}
            )

    return summary_rows, balance_rows, withdrawal_rows


def _show_accounts() -> None:
    summary_rows, balance_rows, withdrawal_rows = _account_view_data(
        _current_plan_assumptions()
    )

    st.title("Accounts")
    st.caption("Starting balances, projected balances, and modeled withdrawal sources · 2027–2040")

    if not summary_rows:
        st.info("No account projection is available.")
        return

    st.subheader("Account summary")
    st.dataframe(
        pd.DataFrame(summary_rows),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Starting balance": st.column_config.NumberColumn(format="$%.2f"),
            "Ending balance": st.column_config.NumberColumn(format="$%.2f"),
            "Total withdrawals": st.column_config.NumberColumn(format="$%.2f"),
        },
    )

    st.subheader("Projected balances by year")
    balance_frame = pd.DataFrame(balance_rows)
    balance_chart = balance_frame.pivot(
        index="Year", columns="Account", values="Balance"
    ).astype(float)
    st.line_chart(balance_chart, y_label="Balance ($)")
    st.dataframe(
        balance_frame.pivot(index="Year", columns="Account", values="Balance")
        .reset_index(),
        hide_index=True,
        use_container_width=True,
        column_config={
            name: st.column_config.NumberColumn(format="$%.2f")
            for name in balance_frame["Account"].unique()
        },
    )

    st.subheader("Withdrawal sources by year")
    if withdrawal_rows:
        st.dataframe(
            pd.DataFrame(withdrawal_rows),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Withdrawal": st.column_config.NumberColumn(format="$%.2f"),
            },
        )
    else:
        st.info("The current projection has no account withdrawals.")


def _available_transaction_years(database_path=DATABASE_PATH) -> list[int]:
    if not database_path.exists():
        return []

    database_uri = f"file:{database_path.as_posix()}?mode=ro"
    try:
        with closing(sqlite3.connect(database_uri, uri=True)) as connection:
            rows = connection.execute(
                """
                SELECT DISTINCT CAST(strftime('%Y', transaction_date) AS INTEGER)
                FROM transactions
                WHERE transaction_date IS NOT NULL
                ORDER BY 1
                """
            ).fetchall()
    except sqlite3.OperationalError:
        return []

    return [row[0] for row in rows if row[0] is not None]


def _transaction_view_data(
    year: int,
    month: int,
    database_path=DATABASE_PATH,
) -> dict[str, object]:
    if not database_path.exists():
        return {
            "transactions": [],
            "categories": [],
            "monthly_spending": Decimal("0"),
            "monthly_income": Decimal("0"),
            "annual_spending": Decimal("0"),
            "annual_income": Decimal("0"),
        }

    database_uri = f"file:{database_path.as_posix()}?mode=ro"
    try:
        with closing(sqlite3.connect(database_uri, uri=True)) as connection:
            rows = connection.execute(
                """
                SELECT
                    transaction_date,
                    description,
                    amount,
                    COALESCE(category_override, category, 'Uncategorized'),
                    COALESCE(merchant_override, merchant, ''),
                    COALESCE(account.name, '—')
                FROM transactions AS t
                LEFT JOIN accounts AS account
                    ON account.id = t.account_id
                WHERE strftime('%Y', t.transaction_date) = ?
                ORDER BY t.transaction_date DESC, t.id DESC
                """,
                (str(year),),
            ).fetchall()
    except sqlite3.OperationalError:
        rows = []

    transactions = []
    categories: dict[str, Decimal] = {}
    monthly_spending = Decimal("0")
    monthly_income = Decimal("0")
    annual_spending = Decimal("0")
    annual_income = Decimal("0")

    for (
        transaction_date,
        description,
        amount,
        category,
        merchant,
        account,
    ) in rows:
        amount = Decimal(str(amount or 0))
        transaction_month = int(transaction_date[5:7])
        is_selected_month = transaction_month == month

        transactions.append(
            {
                "Date": transaction_date,
                "Description": description or "",
                "Merchant": merchant,
                "Account": account,
                "Category": category,
                "Amount": amount,
            }
        )

        if amount < 0:
            spending = abs(amount)
            annual_spending += spending
            if is_selected_month:
                monthly_spending += spending
                categories[category] = (
                    categories.get(category, Decimal("0")) + spending
                )
        elif amount > 0:
            annual_income += amount
            if is_selected_month:
                monthly_income += amount

    monthly_transactions = [
        transaction
        for transaction in transactions
        if int(transaction["Date"][5:7]) == month
    ]

    return {
        "transactions": monthly_transactions,
        "categories": [
            {"Category": category, "Spending": amount}
            for category, amount in sorted(categories.items())
        ],
        "monthly_spending": monthly_spending,
        "monthly_income": monthly_income,
        "annual_spending": annual_spending,
        "annual_income": annual_income,
    }


def _show_transactions_spending() -> None:
    st.title("Transactions & spending")
    st.caption("Review recorded transactions and compare actual spending with plan targets.")
    st.info(
        "This view reads the local CROS transaction database. Verify imported "
        "records before treating them as household data; sample transactions "
        "are not retirement income assumptions."
    )

    years = _available_transaction_years()
    if not years:
        st.info("No dated transactions are available in the local database.")
        return

    selected_year = st.selectbox("Year", years, index=len(years) - 1)
    selected_month = st.selectbox(
        "Month",
        range(1, 13),
        format_func=lambda month: (
            f"{month:02d} · "
            f"{('January February March April May June July August September October November December').split()[month - 1]}"
        ),
    )
    data = _transaction_view_data(selected_year, selected_month)

    monthly_plan = _current_plan_assumptions()["monthly_spending_target"]
    annual_plan = monthly_plan * Decimal("12")
    monthly_variance = data["monthly_spending"] - monthly_plan
    annual_variance = data["annual_spending"] - annual_plan

    st.subheader(f"{selected_year} spending summary")
    metrics = st.columns(4)
    metrics[0].metric("Month spending", _money(data["monthly_spending"]))
    metrics[1].metric(
        "Monthly plan variance",
        _money(monthly_variance),
        delta=f"Plan: {_money(monthly_plan)}",
    )
    metrics[2].metric("Year spending", _money(data["annual_spending"]))
    metrics[3].metric(
        "Annual plan variance",
        _money(annual_variance),
        delta=f"Plan: {_money(annual_plan)}",
    )

    st.caption(
        f"Selected-month inflows: {_money(data['monthly_income'])} · "
        f"Annual recorded inflows: {_money(data['annual_income'])}"
    )

    st.subheader("Selected month by category")
    if data["categories"]:
        category_frame = pd.DataFrame(data["categories"]).set_index("Category")
        st.bar_chart(category_frame, x_label="Category", y_label="Spending ($)")
    else:
        st.info("No spending transactions were recorded for this month.")

    st.subheader("Transactions for selected month")
    if data["transactions"]:
        st.dataframe(
            pd.DataFrame(data["transactions"]),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn(format="$%.2f"),
            },
        )
    else:
        st.info("No transactions were recorded for this month.")


def _show_overview() -> None:
    rows = _overview_rows(_current_plan_assumptions())
    frame = pd.DataFrame(rows)

    first = rows[0]
    last = rows[-1]
    total_withdrawal_tax = sum(
        (row["Withdrawal tax"] for row in rows),
        Decimal("0"),
    )
    total_withdrawals = sum(
        (row["Gross withdrawal"] for row in rows),
        Decimal("0"),
    )

    st.title("Retirement overview")
    st.caption("CROS projection · 2027–2040")

    st.warning(
        "This projection still uses temporary income assumptions, "
        "including the $100,000 taxable-income proxy and zero Social "
        "Security benefits. These will be replaced as the income and "
        "Social Security models are built."
    )

    metrics = st.columns(4)
    metrics[0].metric(
        "Starting portfolio",
        _money(first["Beginning portfolio"]),
    )
    metrics[1].metric(
        "Projected ending portfolio",
        _money(last["Ending portfolio"]),
    )
    metrics[2].metric(
        "Projected withdrawals",
        _money(total_withdrawals),
    )
    metrics[3].metric(
        "Projected withdrawal taxes",
        _money(total_withdrawal_tax),
    )

    st.subheader("Portfolio projection")
    chart = frame.set_index("Year")[
        ["Beginning portfolio", "Ending portfolio"]
    ].astype(float)
    st.line_chart(chart, y_label="Balance ($)")

    st.subheader("Year-by-year plan")
    st.dataframe(
        frame.drop(columns=["Beginning portfolio", "Ending account balances"]),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Spending": st.column_config.NumberColumn(format="$%.2f"),
            "Outside income": st.column_config.NumberColumn(format="$%.2f"),
            "Gross withdrawal": st.column_config.NumberColumn(format="$%.2f"),
            "Withdrawal tax": st.column_config.NumberColumn(format="$%.2f"),
            "Roth conversion": st.column_config.NumberColumn(format="$%.2f"),
            "Conversion tax": st.column_config.NumberColumn(format="$%.2f"),
            "Ending portfolio": st.column_config.NumberColumn(format="$%.2f"),
        },
    )

    st.subheader(f"Projected account balances · {last['Year']}")
    account_balances = pd.DataFrame(
        [
            {"Account": account, "Balance": balance}
            for account, balance in last["Ending account balances"].items()
        ]
    )
    st.dataframe(
        account_balances,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Balance": st.column_config.NumberColumn(format="$%.2f"),
        },
    )


def _show_retirement_plan() -> None:
    assumptions = _current_plan_assumptions()

    st.title("Retirement plan")
    st.caption("Adjust plan assumptions and apply them to the projection.")

    with st.form("retirement_plan_assumptions"):
        monthly_spending = st.number_input(
            "Monthly spending target ($)",
            min_value=0.0,
            value=float(assumptions["monthly_spending_target"]),
            step=100.0,
            format="%.2f",
            key="plan_input_monthly_spending",
        )
        annual_return_percent = st.number_input(
            "Annual return assumption (%)",
            value=float(assumptions["annual_return_assumption"] * 100),
            step=0.25,
            format="%.2f",
            key="plan_input_annual_return_percent",
        )
        annual_roth_conversion = st.number_input(
            "Annual Roth conversion target ($)",
            min_value=0.0,
            value=float(assumptions["annual_roth_conversion_target"]),
            step=1000.0,
            format="%.2f",
            key="plan_input_annual_roth_conversion",
        )
        submitted = st.form_submit_button("Apply plan settings")

    if submitted:
        st.session_state["plan_assumptions"] = {
            "monthly_spending_target": Decimal(str(monthly_spending)),
            "annual_return_assumption": (
                Decimal(str(annual_return_percent)) / Decimal("100")
            ),
            "annual_roth_conversion_target": (
                Decimal(str(annual_roth_conversion))
            ),
        }
        st.success(
            "Plan settings applied. Select Overview to see the updated projection."
        )


def main() -> None:
    st.set_page_config(
        page_title="CROS Retirement Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.sidebar.title("CROS")
    section = st.sidebar.radio("Dashboard", SECTIONS, label_visibility="collapsed")

    if section == "Overview":
        _show_overview()
        return

    if section == "Retirement Plan":
        _show_retirement_plan()
        return

    if section == "Accounts":
        _show_accounts()
        return

    if section == "Transactions & Spending":
        _show_transactions_spending()
        return

    st.title(section)
    st.info(
        "This section is part of the CROS dashboard plan and is not "
        "implemented yet."
    )


if __name__ == "__main__":
    main()
