from decimal import Decimal

from monthly_spending import get_month_summary
from rental_cashflow import monthly_rental_cashflow
from retirement_plan import PLAN


def calculate_cashflow(year: int, month: int):
    """
    Calculate household retirement cash flow.

    Includes:
        - actual transaction spending
        - actual transaction income
        - planned rental cash flow
        - planned retirement spending target

    Taxes, Social Security, Roth conversions,
    and portfolio withdrawal rules are handled
    by later components.
    """

    summary = get_month_summary(
        year,
        month,
    )

    rental = monthly_rental_cashflow()

    actual_spending = summary["total_spending"]

    transaction_income = summary["total_income"]

    rental_income = rental[
        "net_rental_cashflow"
    ]

    total_cash_available = (
        transaction_income
        + rental_income
    )

    preliminary_portfolio_requirement = (
        actual_spending
        - total_cash_available
    )

    spending_variance = (
        actual_spending
        - PLAN.monthly_spending_target
    )

    return {
        "year": year,
        "month": month,

        "planned_spending":
            PLAN.monthly_spending_target,

        "actual_spending":
            actual_spending,

        "transaction_income":
            transaction_income,

        "rental_income":
            rental_income,

        "total_cash_available":
            total_cash_available,

        "preliminary_portfolio_requirement":
            preliminary_portfolio_requirement,

        "spending_variance":
            spending_variance,
    }


def print_cashflow(year: int, month: int):

    result = calculate_cashflow(
        year,
        month,
    )

    print()
    print(
        f"RETIREMENT CASH FLOW: "
        f"{year}-{month:02d}"
    )
    print("=" * 55)

    print(
        f"{'Planned spending':30}"
        f"${result['planned_spending']:,.2f}"
    )

    print(
        f"{'Actual spending':30}"
        f"${result['actual_spending']:,.2f}"
    )

    print()

    print("CASH AVAILABLE")
    print("-" * 55)

    print(
        f"{'Transaction income':30}"
        f"${result['transaction_income']:,.2f}"
    )

    print(
        f"{'Rental cash flow':30}"
        f"${result['rental_income']:,.2f}"
    )

    print(
        f"{'Total cash available':30}"
        f"${result['total_cash_available']:,.2f}"
    )

    print()

    print(
        f"{'Preliminary portfolio requirement':30}"
        f"${result['preliminary_portfolio_requirement']:,.2f}"
    )

    print(
        f"{'Spending variance':30}"
        f"${result['spending_variance']:,.2f}"
    )

    print()

    if result[
        "preliminary_portfolio_requirement"
    ] > 0:

        print(
            "STATUS: Portfolio funds may be "
            "needed."
        )

    else:

        print(
            "STATUS: Current cash sources "
            "cover spending."
        )


if __name__ == "__main__":

    print_cashflow(
        2027,
        1,
    )