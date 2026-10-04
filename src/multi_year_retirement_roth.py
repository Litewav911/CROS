from decimal import Decimal

from annual_withdrawal import calculate_annual_withdrawal
from monthly_spending import get_month_summary
from rental_cashflow import monthly_rental_cashflow
from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)
from roth_conversion_integration import calculate_roth_conversion


def calculate_multi_year_retirement_roth(
    start_year: int,
    end_year: int,
    annual_return: Decimal = Decimal("0"),
    base_taxable_income_by_year=None,
    roth_conversions_by_year=None,
    withdrawals_by_year=None,
    market_declines_by_year=None,
):
    """
    Project the integrated retirement plan across
    multiple years.

    Retirement cash flow is calculated for every year,
    but portfolio withdrawals are only applied when
    explicitly supplied through withdrawals_by_year.

    This keeps the retirement cash-flow requirement
    separate from the portfolio withdrawal decision.

    Roth conversions are applied independently of
    spending withdrawals.

    In the final modeled year, if no explicit Chris 401(k)
    conversion is supplied, the remaining Chris 401(k)
    balance after investment growth and any explicit
    withdrawal is automatically converted.
    """

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    annual_return = Decimal(str(annual_return))

    if annual_return < 0:
        raise ValueError(
            "Annual return cannot be negative."
        )

    if base_taxable_income_by_year is None:
        base_taxable_income_by_year = {}

    if roth_conversions_by_year is None:
        roth_conversions_by_year = {}

    if withdrawals_by_year is None:
        withdrawals_by_year = {}

    if market_declines_by_year is None:
        market_declines_by_year = {}

    account_balances = create_initial_account_balances()
    annual_results = []

    for year in range(start_year, end_year + 1):

        annual_withdrawal = calculate_annual_withdrawal(
            year=year,
            market_decline=market_declines_by_year.get(
                year,
                False,
            ),
        )

        portfolio_requirement = Decimal(
            str(
                annual_withdrawal[
                    "annual_portfolio_requirement"
                ]
            )
        )

        withdrawal_source = annual_withdrawal[
            "recommended_source"
        ]

        # --------------------------------------------------
        # Portfolio withdrawals
        #
        # IMPORTANT:
        # Do not automatically turn the calculated annual
        # portfolio requirement into an account withdrawal.
        #
        # The cash-flow engine determines how much spending
        # would require portfolio funding. The caller controls
        # whether and from which account that withdrawal is
        # actually modeled.
        # --------------------------------------------------

        if year in withdrawals_by_year:

            withdrawals = {
                account: Decimal(str(amount))
                for account, amount
                in withdrawals_by_year[year].items()
            }

        else:

            withdrawals = {}

        # --------------------------------------------------
        # Annual spending / income totals
        # --------------------------------------------------

        annual_spending = Decimal("0")
        transaction_income = Decimal("0")
        rental_income = Decimal("0")

        for month in range(1, 13):

            summary = get_month_summary(
                year,
                month,
            )

            rental = monthly_rental_cashflow()

            annual_spending += Decimal(
                str(
                    summary["total_spending"]
                )
            )

            transaction_income += Decimal(
                str(
                    summary["total_income"]
                )
            )

            rental_income += Decimal(
                str(
                    rental["net_rental_cashflow"]
                )
            )

        # --------------------------------------------------
        # Roth conversions
        # --------------------------------------------------

        explicit_conversions = (
            roth_conversions_by_year.get(
                year,
                {},
            )
        )

        roth_conversions = {
            account: Decimal(str(amount))
            for account, amount
            in explicit_conversions.items()
        }

        # --------------------------------------------------
        # Final-year dynamic conversion
        #
        # If the final year does not already specify a Chris
        # 401(k) conversion, convert whatever remains after
        # investment growth and any explicitly modeled
        # withdrawal.
        # --------------------------------------------------

        if (
            year == end_year
            and "Chris 401(k)"
            not in roth_conversions
        ):

            chris_beginning = Decimal(
                str(
                    account_balances.get(
                        "Chris 401(k)",
                        Decimal("0"),
                    )
                )
            )

            chris_gain = (
                chris_beginning
                * annual_return
            )

            chris_withdrawal = Decimal(
                str(
                    withdrawals.get(
                        "Chris 401(k)",
                        Decimal("0"),
                    )
                )
            )

            chris_available = (
                chris_beginning
                + chris_gain
                - chris_withdrawal
            )

            if chris_available < 0:
                chris_available = Decimal("0")

            if chris_available > 0:
                roth_conversions[
                    "Chris 401(k)"
                ] = chris_available

        # --------------------------------------------------
        # Calculate conversion tax
        # --------------------------------------------------

        conversion_amount = Decimal("0")

        if "Chris 401(k)" in roth_conversions:

            conversion_amount = Decimal(
                str(
                    roth_conversions[
                        "Chris 401(k)"
                    ]
                )
            )

        base_taxable_income = Decimal(
            str(
                base_taxable_income_by_year.get(
                    year,
                    Decimal("0"),
                )
            )
        )

        conversion = calculate_roth_conversion(
            year=year,
            source_account="Chris 401(k)",
            destination_account="Roth IRA",
            base_taxable_income=base_taxable_income,
            conversion_amount=conversion_amount,
        )

        # --------------------------------------------------
        # Project portfolio balances
        # --------------------------------------------------

        projection = project_portfolio_year(
            year=year,
            account_balances=account_balances,
            annual_return=annual_return,
            withdrawals=withdrawals,
            roth_conversions=roth_conversions,
        )

        ending_balances = {
            account.account_name:
                account.ending_balance
            for account in projection.accounts
        }

        # --------------------------------------------------
        # Store annual result
        # --------------------------------------------------

        annual_results.append(
            {
                "year": year,

                "annual_spending":
                    annual_spending,

                "transaction_income":
                    transaction_income,

                "rental_income":
                    rental_income,

                "portfolio_requirement":
                    portfolio_requirement,

                "withdrawal_source":
                    withdrawal_source,

                "withdrawals":
                    withdrawals,

                "roth_conversion":
                    conversion,

                "projection":
                    projection,

                "ending_balances":
                    ending_balances,
            }
        )

        account_balances = ending_balances

    return annual_results


def print_multi_year_retirement_roth(results):

    print()
    print(
        "MULTI-YEAR RETIREMENT / ROTH PROJECTION"
    )
    print("=" * 110)

    print(
        f"{'Year':<8}"
        f"{'Beginning':>18}"
        f"{'Gain':>16}"
        f"{'Withdrawal':>16}"
        f"{'Roth Conv.':>16}"
        f"{'Ending':>18}"
    )

    print("-" * 110)

    for result in results:

        projection = result["projection"]

        print(
            f"{result['year']:<8}"
            f"${projection.beginning_total:>16,.2f}"
            f"${projection.investment_gain_total:>14,.2f}"
            f"${projection.withdrawal_total:>14,.2f}"
            f"${projection.roth_conversion_total:>14,.2f}"
            f"${projection.ending_total:>16,.2f}"
        )


if __name__ == "__main__":

    results = calculate_multi_year_retirement_roth(
        start_year=2027,
        end_year=2040,
        annual_return=Decimal("0.05"),
        base_taxable_income_by_year={
            year: Decimal("100000")
            for year in range(2027, 2041)
        },
        roth_conversions_by_year={
            year: {
                "Chris 401(k)": Decimal("80000")
            }
            for year in range(2027, 2040)
        },
    )

    print_multi_year_retirement_roth(results)