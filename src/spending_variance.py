from decimal import Decimal, ROUND_HALF_UP

from monthly_spending import get_month_summary
from retirement_plan import PLAN


CENT = Decimal("0.01")


def calculate_spending_variance(
    year: int,
    month: int,
):
    """
    Compare actual monthly spending with
    the retirement spending target.
    """

    summary = get_month_summary(
        year,
        month,
    )

    actual = summary["total_spending"]

    planned = PLAN.monthly_spending_target

    dollar_variance = actual - planned

    if planned == 0:
        percentage_variance = Decimal("0")
    else:
        percentage_variance = (
            dollar_variance / planned
        ) * Decimal("100")

    return {
        "year": year,
        "month": month,
        "planned_spending": planned,
        "actual_spending": actual,
        "dollar_variance": dollar_variance,
        "percentage_variance": percentage_variance,
    }


def print_variance(year: int, month: int):

    result = calculate_spending_variance(
        year,
        month,
    )

    print()
    print(
        f"SPENDING VARIANCE: "
        f"{year}-{month:02d}"
    )
    print("=" * 50)

    print(
        f"{'Planned spending':30}"
        f"${result['planned_spending']:,.2f}"
    )

    print(
        f"{'Actual spending':30}"
        f"${result['actual_spending']:,.2f}"
    )

    print(
        f"{'Dollar variance':30}"
        f"${result['dollar_variance']:,.2f}"
    )

    print(
        f"{'Percentage variance':30}"
        f"{result['percentage_variance']:,.2f}%"
    )

    print()

    if result["dollar_variance"] > 0:

        print(
            "STATUS: Spending is ABOVE "
            "the retirement target."
        )

    elif result["dollar_variance"] < 0:

        print(
            "STATUS: Spending is BELOW "
            "the retirement target."
        )

    else:

        print(
            "STATUS: Spending exactly matches "
            "the retirement target."
        )


if __name__ == "__main__":

    print_variance(
        2027,
        1,
    )