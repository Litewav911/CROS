from decimal import Decimal
from dataclasses import dataclass
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
    Consolidated household portfolio projection
    for one year.
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
    roth_conversions: dict[str, Decimal] | None = None,
) -> PortfolioProjection:
    """
    Project all modeled accounts for one year.

    Investment growth is applied first.

    Withdrawals and Roth conversions are then applied
    against the account value after investment growth.

    Roth conversions are internal portfolio transfers:

        - traditional source account decreases
        - Roth IRA increases by the same gross amount

    Roth conversion taxes are calculated separately by
    the tax engine and are NOT deducted here.
    """

    if withdrawals is None:
        withdrawals = {}

    if roth_conversions is None:
        roth_conversions = {}

    annual_return = Decimal(
        str(annual_return)
    )

    if annual_return < 0:
        raise ValueError(
            "Annual return cannot be negative."
        )

    account_projections = []

    beginning_total = Decimal("0")
    investment_gain_total = Decimal("0")
    withdrawal_total = Decimal("0")
    roth_conversion_total = Decimal("0")
    ending_total = Decimal("0")

    # --------------------------------------------------
    # Project each account
    # --------------------------------------------------

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

        roth_conversion = Decimal(
            str(
                roth_conversions.get(
                    account.name,
                    Decimal("0"),
                )
            )
        )

        if beginning_balance < 0:
            raise ValueError(
                f"Beginning balance cannot be negative "
                f"for {account.name}."
            )

        if withdrawal < 0:
            raise ValueError(
                f"Withdrawal cannot be negative "
                f"for {account.name}."
            )

        if roth_conversion < 0:
            raise ValueError(
                f"Roth conversion cannot be negative "
                f"for {account.name}."
            )

        # --------------------------------------------------
        # Investment growth occurs before withdrawals and
        # Roth conversions.
        # --------------------------------------------------

        investment_gain = (
            beginning_balance
            * annual_return
        )

        available_after_growth = (
            beginning_balance
            + investment_gain
        )

        total_outflow = (
            withdrawal
            + roth_conversion
        )

        if total_outflow > available_after_growth:
            raise ValueError(
                f"Withdrawal plus Roth conversion exceeds "
                f"the available balance after investment "
                f"growth for {account.name}. "
                f"Available: "
                f"${available_after_growth:,.2f}; "
                f"Required: "
                f"${total_outflow:,.2f}."
            )

        projection = project_account_year(
            year=year,
            account_name=account.name,
            beginning_balance=beginning_balance,
            investment_gain=investment_gain,
            withdrawal=withdrawal,
            roth_conversion=roth_conversion,
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

    # --------------------------------------------------
    # Roth conversion destination
    #
    # The source account has already been reduced by the
    # conversion above.
    #
    # Add the gross conversion to the Roth IRA.
    #
    # Because the source was reduced by the same amount,
    # the total portfolio value remains unchanged.
    # --------------------------------------------------

    total_conversion = sum(
        (
            Decimal(str(amount))
            for amount in roth_conversions.values()
        ),
        Decimal("0"),
    )

    if total_conversion > 0:

        roth_found = False

        for account in account_projections:

            if account.account_name == "Roth IRA":

                account.ending_balance += (
                    total_conversion
                )

                ending_total += (
                    total_conversion
                )

                roth_found = True
                break

        if not roth_found:
            raise ValueError(
                "Roth IRA account is required "
                "for Roth conversions."
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


def apply_roth_conversion_destination(
    account_balances: dict[str, Decimal],
    source_account: str,
    destination_account: str,
    conversion_amount: Decimal,
):
    """
    Compatibility helper for Roth conversion integration.

    Roth conversions are already fully applied by
    project_portfolio_year():

        - source account is reduced
        - destination Roth IRA is increased
        - total portfolio value is unchanged

    This function therefore verifies that the requested
    accounts exist and returns the balances unchanged.

    It intentionally does not apply the conversion a second
    time. This prevents double-counting when an integration
    test or older calling component invokes this helper
    after project_portfolio_year().
    """

    conversion_amount = Decimal(
        str(conversion_amount)
    )

    if conversion_amount < 0:
        raise ValueError(
            "Roth conversion amount cannot be negative."
        )

    if source_account not in account_balances:
        raise ValueError(
            f"Source account not found: "
            f"{source_account}"
        )

    if destination_account not in account_balances:
        raise ValueError(
            f"Destination account not found: "
            f"{destination_account}"
        )

    if conversion_amount == 0:
        return account_balances

    return account_balances


def create_initial_account_balances():
    """
    Create the initial account-balance dictionary
    from the retirement account model.
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
    roth_conversions_by_year=None,
    market_declines_by_year=None,
):
    """
    Project the portfolio across multiple years.

    Explicit annual withdrawals take precedence over
    the annual withdrawal engine.

    If no explicit withdrawal exists for a year,
    calculate_annual_withdrawal() determines the
    withdrawal source and amount.

    Roth conversions are supplied as:

        {
            2027: {
                "Chris 401(k)": Decimal("80000")
            },
            2028: {
                "Chris 401(k)": Decimal("80000")
            }
        }

    Roth conversion taxes are calculated separately
    by the tax/conversion engine and are not deducted
    from portfolio balances.
    """

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    annual_return = Decimal(
        str(annual_return)
    )

    if annual_return < 0:
        raise ValueError(
            "Annual return cannot be negative."
        )

    if withdrawals_by_year is None:
        withdrawals_by_year = {}

    if roth_conversions_by_year is None:
        roth_conversions_by_year = {}

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

        # --------------------------------------------------
        # Determine withdrawals
        # --------------------------------------------------

        if year in withdrawals_by_year:

            withdrawals = {
                account: Decimal(str(amount))
                for account, amount
                in withdrawals_by_year[year].items()
            }

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

        # --------------------------------------------------
        # Determine Roth conversions
        # --------------------------------------------------

        roth_conversions = {
            account: Decimal(str(amount))
            for account, amount
            in roth_conversions_by_year.get(
                year,
                {},
            ).items()
        }

        # --------------------------------------------------
        # Project the year
        # --------------------------------------------------

        projection = project_portfolio_year(
            year=year,
            account_balances=account_balances,
            annual_return=annual_return,
            withdrawals=withdrawals,
            roth_conversions=roth_conversions,
        )

        projections.append(
            projection
        )

        # --------------------------------------------------
        # Carry ending balances into the next year
        # --------------------------------------------------

        account_balances = {
            account.account_name:
                account.ending_balance
            for account in projection.accounts
        }

    return projections


def print_portfolio_projection(
    projection: PortfolioProjection,
):
    """
    Print a detailed single-year portfolio projection.
    """

    print()
    print(
        f"PORTFOLIO PROJECTION: "
        f"{projection.year}"
    )

    print("=" * 120)

    print(
        f"{'Account':30}"
        f"{'Beginning':>18}"
        f"{'Gain':>18}"
        f"{'Withdrawal':>18}"
        f"{'Roth Conv.':>18}"
        f"{'Ending':>18}"
    )

    print("-" * 120)

    for account in projection.accounts:

        print(
            f"{account.account_name:30}"
            f"${account.beginning_balance:>16,.2f}"
            f"${account.investment_gain:>16,.2f}"
            f"${account.withdrawal:>16,.2f}"
            f"${account.roth_conversion:>16,.2f}"
            f"${account.ending_balance:>16,.2f}"
        )

    print("-" * 120)

    print(
        f"{'TOTAL PORTFOLIO':30}"
        f"${projection.beginning_total:>16,.2f}"
        f"${projection.investment_gain_total:>16,.2f}"
        f"${projection.withdrawal_total:>16,.2f}"
        f"${projection.roth_conversion_total:>16,.2f}"
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
            f" - Roth conversion "
            f"${projection.roth_conversion_total:,.2f}"
            f" = "
            f"${projection.ending_total:,.2f}"
        )