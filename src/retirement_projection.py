from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class RetirementYear:
    year: int

    starting_total_assets: Decimal
    planned_spending: Decimal
    rental_cash_flow: Decimal
    portfolio_withdrawal: Decimal
    roth_conversion: Decimal
    investment_gain: Decimal
    ending_total_assets: Decimal


def create_retirement_year(
    year: int,
    starting_total_assets: Decimal,
    planned_spending: Decimal,
    rental_cash_flow: Decimal,
    portfolio_withdrawal: Decimal,
    roth_conversion: Decimal,
    investment_gain: Decimal,
) -> RetirementYear:
    """
    Create one year of the retirement projection.

    Taxes, Social Security, RMDs, and investment
    return assumptions will be added by later engines.
    """

    starting_total_assets = Decimal(
        str(starting_total_assets)
    )

    planned_spending = Decimal(
        str(planned_spending)
    )

    rental_cash_flow = Decimal(
        str(rental_cash_flow)
    )

    portfolio_withdrawal = Decimal(
        str(portfolio_withdrawal)
    )

    roth_conversion = Decimal(
        str(roth_conversion)
    )

    investment_gain = Decimal(
        str(investment_gain)
    )

    ending_total_assets = (
        starting_total_assets
        + investment_gain
        - portfolio_withdrawal
        - roth_conversion
    )

    return RetirementYear(
        year=year,
        starting_total_assets=starting_total_assets,
        planned_spending=planned_spending,
        rental_cash_flow=rental_cash_flow,
        portfolio_withdrawal=portfolio_withdrawal,
        roth_conversion=roth_conversion,
        investment_gain=investment_gain,
        ending_total_assets=ending_total_assets,
    )


def project_years(
    start_year: int,
    end_year: int,
    starting_total_assets: Decimal,
    planned_annual_spending: Decimal,
    annual_rental_cash_flow: Decimal,
) -> List[RetirementYear]:
    """
    Create the retirement timeline.

    This initial version uses zero withdrawals,
    Roth conversions, and investment gains.

    Later versions will replace these placeholders
    with actual retirement-plan calculations.
    """

    years = []

    current_assets = Decimal(
        str(starting_total_assets)
    )

    for year in range(
        start_year,
        end_year + 1,
    ):

        projection = create_retirement_year(
            year=year,
            starting_total_assets=current_assets,
            planned_spending=planned_annual_spending,
            rental_cash_flow=annual_rental_cash_flow,
            portfolio_withdrawal=Decimal("0"),
            roth_conversion=Decimal("0"),
            investment_gain=Decimal("0"),
        )

        years.append(projection)

        current_assets = (
            projection.ending_total_assets
        )

    return years


def print_projection(
    projections: List[RetirementYear],
):

    print()
    print("RETIREMENT PROJECTION")
    print("=" * 105)

    print(
        f"{'Year':<8}"
        f"{'Beginning':>16}"
        f"{'Spending':>16}"
        f"{'Rental':>16}"
        f"{'Withdrawal':>16}"
        f"{'Roth Conv.':>16}"
        f"{'Ending':>16}"
    )

    print("-" * 105)

    for year in projections:

        print(
            f"{year.year:<8}"
            f"${year.starting_total_assets:>14,.2f}"
            f"${year.planned_spending:>14,.2f}"
            f"${year.rental_cash_flow:>14,.2f}"
            f"${year.portfolio_withdrawal:>14,.2f}"
            f"${year.roth_conversion:>14,.2f}"
            f"${year.ending_total_assets:>14,.2f}"
        )


if __name__ == "__main__":

    projections = project_years(
        start_year=2027,
        end_year=2040,
        starting_total_assets=Decimal(
            "1219138.61"
        ),
        planned_annual_spending=Decimal(
            "132000"
        ),
        annual_rental_cash_flow=Decimal(
            "34636.08"
        ),
    )

    print_projection(projections)