from dataclasses import dataclass
from decimal import Decimal
from typing import List

from retirement_accounts import RETIREMENT_ACCOUNTS

from annual_account_projection import (
    AnnualAccountProjection,
    project_account_year,
)

from annual_withdrawal import (
    calculate_annual_withdrawal,
)


@dataclass
class PortfolioProjection:
    """
    Represents the consolidated household portfolio
    for one projection year.
    """

    year: int
    accounts: List[AnnualAccountProjection]
    beginning_total: Decimal
    investment_gain_total: Decimal
    withdrawal_total: Decimal
    roth_conversion_total: Decimal
    ending_total: Decimal


def project_portfolio_year(
    year: int,
    account_balances: dict[str, Decimal],
    annual_return: Decimal = Decimal("0"),
    withdrawals: dict[str, Decimal] | None = None,
) -> PortfolioProjection:
    """
    Project all modeled retirement accounts for one year.

    withdrawals maps account names to withdrawal amounts.
    """

    if withdrawals is None:
        withdrawals = {}

    account_projections = []

    beginning_total = Decimal("0")
    investment_gain_total = Decimal("0")
    withdrawal_total = Decimal("0")
    roth_conversion_total = Decimal("0")
    ending_total = Decimal("0")

    for account in RETIREMENT_ACCOUNTS:

        beginning_balance = Decimal(
            str(
                account_balances.get(
                    account.name,
                    account.balance,
                )
            )
        )

        withdrawal = Decimal(
            str(
                withdrawals.get(
                    account.name,
                    Decimal("0"),
                )
            )
        )

        if withdrawal < 0:
            raise ValueError(
                "Withdrawal cannot be negative."
            )

        if withdrawal > beginning_balance:
            raise ValueError(
                f"Withdrawal of ${withdrawal:,.2f} "
                f"exceeds the beginning balance of "
                f"${beginning_balance:,.2f} for "
                f"{account.name}."
            )

        investment_gain = (
            beginning_balance
            * annual_return
        )

        projection = project_account_year(
            year=year,
            account_name=account.name,
            beginning_balance=beginning_balance,
            investment_gain=investment_gain,
            withdrawal=withdrawal,
            roth_conversion=Decimal("0"),
        )

        account_projections.append(
            projection
        )

        beginning_total += (
            projection.beginning_balance
        )

        investment_gain_total += (
            projection.investment_gain
        )

        withdrawal_total += (
            projection.withdrawal
        )

        roth_conversion_total += (
            projection.roth_conversion
        )

        ending_total += (
            projection.ending_balance
        )

    return PortfolioProjection(
        year=year,
        accounts=account_projections,
        beginning_total=beginning_total,
        investment_gain_total=investment_gain_total,
        withdrawal_total=withdrawal_total,
        roth_conversion_total=roth_conversion_total,
        ending_total=ending_total,
    )


def create_initial_account_balances():
    """
    Create the initial beginning balances from the
    retirement account model.
    """

    return {
        account.name: Decimal(
            str(account.balance)
        )
        for account in RETIREMENT_ACCOUNTS
    }


def project_portfolio_years(
    start_year: int,
    end_year: int,
    annual_return: Decimal = Decimal("0"),
    withdrawals_by_year=None,
    market_declines_by_year=None,
):
    """
    Project the portfolio across multiple years.

    If withdrawals_by_year is supplied, those explicit
    withdrawals are used.

    Otherwise the annual withdrawal engine determines
    the withdrawal for each year.

    market_declines_by_year allows the existing
    withdrawal strategy to select the cash reserve
    during specified market-decline years.
    """

    if withdrawals_by_year is None:
        withdrawals_by_year = {}

    if market_declines_by_year is None:
        market_declines_by_year = {}

    account_balances = (
        create_initial_account_balances()
    )

    projections = []

    for year in range(
        start_year,
        end_year + 1,
    ):

        if year in withdrawals_by_year:

            withdrawals = withdrawals_by_year[
                year
            ]

        else:

            annual_withdrawal = (
                calculate_annual_withdrawal(
                    year=year,
                    market_decline=(
                        market_declines_by_year.get(
                            year,
                            False,
                        )
                    ),
                )
            )

            source = (
                annual_withdrawal[
                    "recommended_source"
                ]
            )

            amount = Decimal(
                str(
                    annual_withdrawal[
                        "annual_portfolio_requirement"
                    ]
                )
            )

            if (
                source == "None"
                or amount <= 0
            ):
                withdrawals = {}

            else:
                withdrawals = {
                    source: amount
                }

        projection = project_portfolio_year(
            year=year,
            account_balances=account_balances,
            annual_return=annual_return,
            withdrawals=withdrawals,
        )

        projections.append(
            projection
        )

        account_balances = {
            account.account_name:
                account.ending_balance
            for account in projection.accounts
        }

    return projections


def print_portfolio_projection(
    projection: PortfolioProjection,
):

    print()
    print(
        f"PORTFOLIO PROJECTION: "
        f"{projection.year}"
    )

    print("=" * 105)

    print(
        f"{'Account':30}"
        f"{'Beginning':>18}"
        f"{'Gain':>18}"
        f"{'Withdrawal':>18}"
        f"{'Ending':>18}"
    )

    print("-" * 105)

    for account in projection.accounts:

        print(
            f"{account.account_name:30}"
            f"${account.beginning_balance:>16,.2f}"
            f"${account.investment_gain:>16,.2f}"
            f"${account.withdrawal:>16,.2f}"
            f"${account.ending_balance:>16,.2f}"
        )

    print("-" * 105)

    print(
        f"{'TOTAL PORTFOLIO':30}"
        f"${projection.beginning_total:>16,.2f}"
        f"${projection.investment_gain_total:>16,.2f}"
        f"${projection.withdrawal_total:>16,.2f}"
        f"${projection.ending_total:>16,.2f}"
    )


if __name__ == "__main__":

    projections = project_portfolio_years(
        start_year=2027,
        end_year=2040,
        annual_return=Decimal("0.05"),
    )

    for projection in projections:

        print(
            f"{projection.year}: "
            f"${projection.beginning_total:,.2f}"
            f" - withdrawal "
            f"${projection.withdrawal_total:,.2f}"
            f" = "
            f"${projection.ending_total:,.2f}"
        )