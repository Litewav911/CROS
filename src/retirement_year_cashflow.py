from decimal import Decimal

from retirement_cashflow import calculate_cashflow


def calculate_year_cashflow(
    year: int,
    planned_annual_spending: Decimal,
):
    """
    Calculate retirement cash flow for one year.

    The existing monthly retirement cash-flow engine
    remains the source of truth for:

        - actual transaction spending
        - transaction income
        - rental cash flow
        - preliminary portfolio requirement
        - spending variance

    Portfolio withdrawal strategy, taxes, Social Security,
    Roth conversions, and investment returns are handled
    by later components.
    """

    planned_annual_spending = Decimal(
        str(planned_annual_spending)
    )

    monthly_planned_spending = (
        planned_annual_spending / Decimal("12")
    )

    total_actual_spending = Decimal("0")
    total_transaction_income = Decimal("0")
    total_rental_income = Decimal("0")
    total_portfolio_requirement = Decimal("0")

    monthly_results = []

    for month in range(1, 13):

        result = calculate_cashflow(
            year,
            month,
        )

        actual_spending = Decimal(
            str(result["actual_spending"])
        )

        transaction_income = Decimal(
            str(result["transaction_income"])
        )

        rental_income = Decimal(
            str(result["rental_income"])
        )

        portfolio_requirement = Decimal(
            str(
                result[
                    "preliminary_portfolio_requirement"
                ]
            )
        )

        total_actual_spending += (
            actual_spending
        )

        total_transaction_income += (
            transaction_income
        )

        total_rental_income += (
            rental_income
        )

        # A negative requirement means current
        # cash sources exceed spending.
        #
        # For the annual portfolio requirement,
        # only positive monthly requirements count.
        if portfolio_requirement > 0:
            total_portfolio_requirement += (
                portfolio_requirement
            )

        monthly_results.append(result)

    return {
        "year": year,

        "planned_spending":
            planned_annual_spending,

        "actual_spending":
            total_actual_spending,

        "transaction_income":
            total_transaction_income,

        "rental_income":
            total_rental_income,

        "portfolio_requirement":
            total_portfolio_requirement,

        "monthly_results":
            monthly_results,
    }


def print_year_cashflow(
    year: int,
    planned_annual_spending: Decimal,
):

    result = calculate_year_cashflow(
        year,
        planned_annual_spending,
    )

    print()
    print(
        f"RETIREMENT YEAR CASH FLOW: {year}"
    )
    print("=" * 65)

    print(
        f"{'Planned spending':35}"
        f"${result['planned_spending']:,.2f}"
    )

    print(
        f"{'Actual spending':35}"
        f"${result['actual_spending']:,.2f}"
    )

    print(
        f"{'Transaction income':35}"
        f"${result['transaction_income']:,.2f}"
    )

    print(
        f"{'Rental cash flow':35}"
        f"${result['rental_income']:,.2f}"
    )

    print(
        f"{'Portfolio requirement':35}"
        f"${result['portfolio_requirement']:,.2f}"
    )


if __name__ == "__main__":

    print_year_cashflow(
        2027,
        Decimal("132000"),
    )