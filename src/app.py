from decimal import Decimal

import pandas as pd
import streamlit as st

from real_retirement_scenario import run_real_retirement_scenario
from retirement_report import build_retirement_report


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


def _overview_rows() -> list[dict[str, object]]:
    results = run_real_retirement_scenario()
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


def _show_overview() -> None:
    rows = _overview_rows()
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

    st.title(section)
    st.info(
        "This section is part of the CROS dashboard plan and is not "
        "implemented yet."
    )


if __name__ == "__main__":
    main()
