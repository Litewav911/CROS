from dataclasses import dataclass
from decimal import Decimal

from retirement_engine import RetirementYearResult


@dataclass
class RetirementReportRow:
    """
    Presentation-ready annual retirement-plan row.

    This layer does not perform calculations. It converts the
    authoritative RetirementYearResult into a clean annual ledger.
    """

    year: int
    beginning_portfolio: Decimal
    planned_spending: Decimal
    total_income: Decimal
    gross_withdrawal: Decimal
    withdrawal_tax: Decimal
    net_withdrawal: Decimal
    roth_conversion: Decimal
    roth_conversion_tax: Decimal
    investment_gain: Decimal
    ending_portfolio: Decimal
    withdrawal_sources: dict[str, Decimal]
    ending_balances: dict[str, Decimal]
    market_decline: bool


def build_retirement_report(
    results: list[RetirementYearResult],
) -> list[RetirementReportRow]:
    """
    Convert retirement-engine results into presentation rows.

    The retirement engine remains the single source of truth.
    No financial calculations are changed here.
    """

    rows: list[RetirementReportRow] = []

    for result in results:

        total_income = (
            result.transaction_income
            + result.rental_income
            + result.social_security
        )

        net_withdrawal = (
            result.gross_withdrawal
            - result.withdrawal_tax
        )

        rows.append(
            RetirementReportRow(
                year=result.year,
                beginning_portfolio=result.beginning_total,
                planned_spending=result.planned_spending,
                total_income=total_income,
                gross_withdrawal=result.gross_withdrawal,
                withdrawal_tax=result.withdrawal_tax,
                net_withdrawal=net_withdrawal,
                roth_conversion=result.conversion_amount,
                roth_conversion_tax=result.conversion_tax,
                investment_gain=result.investment_gain_total,
                ending_portfolio=result.ending_total,
                withdrawal_sources=dict(
                    result.withdrawal_allocations
                ),
                ending_balances=dict(
                    result.ending_balances
                ),
                market_decline=result.market_decline,
            )
        )

    return rows


def print_retirement_report(
    rows: list[RetirementReportRow],
) -> None:
    """
    Print the annual 2027-2040 retirement-plan ledger.
    """

    print()
    print("CROS RETIREMENT PLAN REPORT")
    print("=" * 175)

    print(
        f"{'Year':<7}"
        f"{'Beginning':>17}"
        f"{'Spending':>15}"
        f"{'Income':>15}"
        f"{'Withdrawal':>17}"
        f"{'W/D Tax':>15}"
        f"{'Roth Conv.':>17}"
        f"{'Conv. Tax':>15}"
        f"{'Investment Gain':>18}"
        f"{'Ending':>18}"
    )

    print("-" * 175)

    for row in rows:

        print(
            f"{row.year:<7}"
            f"${row.beginning_portfolio:>15,.2f}"
            f"${row.planned_spending:>13,.2f}"
            f"${row.total_income:>13,.2f}"
            f"${row.gross_withdrawal:>15,.2f}"
            f"${row.withdrawal_tax:>13,.2f}"
            f"${row.roth_conversion:>15,.2f}"
            f"${row.roth_conversion_tax:>13,.2f}"
            f"${row.investment_gain:>16,.2f}"
            f"${row.ending_portfolio:>16,.2f}"
        )

        if row.withdrawal_sources:

            sources = ", ".join(
                f"{name}: ${amount:,.2f}"
                for name, amount
                in row.withdrawal_sources.items()
            )

            print(
                f"        Withdrawal sources: {sources}"
            )

        if row.market_decline:

            print(
                "        MARKET DECLINE: "
                "cash-reserve priority active"
            )

    print("-" * 175)

    if rows:

        first = rows[0]
        last = rows[-1]

        total_spending = sum(
            (
                row.planned_spending
                for row in rows
            ),
            Decimal("0"),
        )

        total_income = sum(
            (
                row.total_income
                for row in rows
            ),
            Decimal("0"),
        )

        total_withdrawals = sum(
            (
                row.gross_withdrawal
                for row in rows
            ),
            Decimal("0"),
        )

        total_withdrawal_tax = sum(
            (
                row.withdrawal_tax
                for row in rows
            ),
            Decimal("0"),
        )

        total_conversions = sum(
            (
                row.roth_conversion
                for row in rows
            ),
            Decimal("0"),
        )

        total_conversion_tax = sum(
            (
                row.roth_conversion_tax
                for row in rows
            ),
            Decimal("0"),
        )

        total_investment_gain = sum(
            (
                row.investment_gain
                for row in rows
            ),
            Decimal("0"),
        )

        print()
        print("PERIOD TOTALS")
        print("-------------")

        print(
            f"Years:                 "
            f"{first.year}-{last.year}"
        )

        print(
            f"Beginning portfolio:   "
            f"${first.beginning_portfolio:,.2f}"
        )

        print(
            f"Total planned spending: "
            f"${total_spending:,.2f}"
        )

        print(
            f"Total outside income:  "
            f"${total_income:,.2f}"
        )

        print(
            f"Total gross withdrawals: "
            f"${total_withdrawals:,.2f}"
        )

        print(
            f"Total withdrawal tax:  "
            f"${total_withdrawal_tax:,.2f}"
        )

        print(
            f"Total Roth conversions: "
            f"${total_conversions:,.2f}"
        )

        print(
            f"Total conversion tax:  "
            f"${total_conversion_tax:,.2f}"
        )

        print(
            f"Total investment gain: "
            f"${total_investment_gain:,.2f}"
        )

        print(
            f"Ending portfolio:      "
            f"${last.ending_portfolio:,.2f}"
        )


if __name__ == "__main__":

    from retirement_engine import (
        RetirementEngineConfig,
        run_retirement_engine,
    )

    results = run_retirement_engine(
        RetirementEngineConfig()
    )

    rows = build_retirement_report(
        results
    )

    print_retirement_report(
        rows
    )