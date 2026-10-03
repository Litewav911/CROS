from decimal import Decimal

from monthly_spending import get_month_summary
from retirement_plan import PLAN


def calculate_cashflow(year: int, month: int):
    """
    Calculate actual household cash flow for a month.

    Spending comes from categorized transactions.
    Income comes from positive transaction amounts.

    The retirement spending target is shown separately
    from actual spending.
    """

    summary = get_month_summary(
        year,
        month,
    )

    actual_spending = summary["total_spending"]
    actual_income = summary["total_income"]

    net_cash_requirement = (
        actual_spending
        - actual_income
    )

    spending_variance = (
        actual_spending
        - PLAN.monthly_spending_target
    )

    return {
        "year": year,
        "month": month,
        "actual_spending": actual_spending,
        "actual_income": actual_income,
        "net_cash_requirement": net_cash_requirement,
        "planned_spending": (
            PLAN.monthly_spending_target
        ),
        "spending_variance": spending_variance,
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
    print("=" * 50)

    print(
        f"{'Planned spending':25}"
        f"${result['planned_spending']:,.2f}"
    )

    print(
        f"{'Actual spending':25}"
        f"${result['actual_spending']:,.2f}"
    )

    print(
        f"{'Actual income':25}"
        f"${result['actual_income']:,.2f}"
    )

    print(
        f"{'Net cash requirement':25}"
        f"${result['net_cash_requirement']:,.2f}"
    )

    print(
        f"{'Spending variance':25}"
        f"${result['spending_variance']:,.2f}"
    )

    print()

    if result["spending_variance"] > 0:

        print(
            "STATUS: Spending is above the "
            "retirement target."
        )

    elif result["spending_variance"] < 0:

        print(
            "STATUS: Spending is below the "
            "retirement target."
        )

    else:

        print(
            "STATUS: Spending exactly matches "
            "the retirement target."
        )


if __name__ == "__main__":

    print_cashflow(
        2027,
        1,
    )