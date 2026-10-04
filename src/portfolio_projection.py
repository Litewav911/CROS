from dataclasses import dataclass
from decimal import Decimal
from typing import List

from retirement_accounts import RETIREMENT_ACCOUNTS
from annual_account_projection import (
    AnnualAccountProjection,
    project_account_year,
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
) -> PortfolioProjection:
    """
    Project all modeled retirement accounts for one year.

    account_balances contains the beginning balance
    for each account.

    The ending balances can then be passed into the
    next year's projection.
    """

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

        projection = project_account_year(
            year=year,
            account_name=account.name,
            beginning_balance=beginning_balance,
            investment_gain=Decimal("0"),
            withdrawal=Decimal("0"),
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
):
    """
    Project the portfolio across multiple years.

    Each year's ending account balances become the
    following year's beginning balances.
    """

    account_balances = (
        create_initial_account_balances()
    )

    projections = []

    for year in range(
        start_year,
        end_year + 1,
    ):

        projection = project_portfolio_year(
            year=year,
            account_balances=account_balances,
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

    print("=" * 80)

    print(
        f"{'Account':30}"
        f"{'Beginning':>18}"
        f"{'Ending':>18}"
    )

    print("-" * 80)

    for account in projection.accounts:

        print(
            f"{account.account_name:30}"
            f"${account.beginning_balance:>16,.2f}"
            f"${account.ending_balance:>16,.2f}"
        )

    print("-" * 80)

    print(
        f"{'TOTAL PORTFOLIO':30}"
        f"${projection.beginning_total:>16,.2f}"
        f"${projection.ending_total:>16,.2f}"
    )


if __name__ == "__main__":

    projections = project_portfolio_years(
        start_year=2027,
        end_year=2040,
    )

    for projection in projections:

        print(
            f"{projection.year}: "
            f"${projection.beginning_total:,.2f}"
            f" -> "
            f"${projection.ending_total:,.2f}"
        )