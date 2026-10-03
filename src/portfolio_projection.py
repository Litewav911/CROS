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
) -> PortfolioProjection:
    """
    Project all modeled retirement accounts for one year.

    This initial version applies zero investment gains,
    withdrawals, and Roth conversions.

    Account-specific rules will be added by later
    retirement-strategy components.
    """

    account_projections = []

    beginning_total = Decimal("0")
    investment_gain_total = Decimal("0")
    withdrawal_total = Decimal("0")
    roth_conversion_total = Decimal("0")
    ending_total = Decimal("0")

    for account in RETIREMENT_ACCOUNTS:

        projection = project_account_year(
            year=year,
            account_name=account.name,
            beginning_balance=account.balance,
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

    projection = project_portfolio_year(
        2027
    )

    print_portfolio_projection(
        projection
    )