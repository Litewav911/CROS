from decimal import Decimal

from retirement_cashflow import calculate_cashflow


def calculate_portfolio_withdrawal(
    year: int,
    month: int,
):
    """
    Calculate the amount the investment portfolio
    needs to provide for a month.

    Positive values represent a required withdrawal.

    Negative cash requirements are converted to
    zero because excess household cash is not
    automatically treated as a portfolio contribution.
    """

    cashflow = calculate_cashflow(
        year,
        month,
    )

    preliminary_requirement = (
        cashflow[
            "preliminary_portfolio_requirement"
        ]
    )

    portfolio_withdrawal = max(
        Decimal("0"),
        preliminary_requirement,
    )

    excess_cash = max(
        Decimal("0"),
        -preliminary_requirement,
    )

    return {
        "year": year,
        "month": month,
        "actual_spending":
            cashflow["actual_spending"],
        "transaction_income":
            cashflow["transaction_income"],
        "rental_income":
            cashflow["rental_income"],
        "total_cash_available":
            cashflow["total_cash_available"],
        "portfolio_withdrawal":
            portfolio_withdrawal,
        "excess_cash":
            excess_cash,
    }


def print_withdrawal(
    year: int,
    month: int,
):

    result = calculate_portfolio_withdrawal(
        year,
        month,
    )

    print()
    print(
        f"PORTFOLIO WITHDRAWAL: "
        f"{year}-{month:02d}"
    )
    print("=" * 55)

    print(
        f"{'Actual spending':30}"
        f"${result['actual_spending']:,.2f}"
    )

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
        f"{'Portfolio withdrawal':30}"
        f"${result['portfolio_withdrawal']:,.2f}"
    )

    print(
        f"{'Excess cash':30}"
        f"${result['excess_cash']:,.2f}"
    )

    print()

    if result["portfolio_withdrawal"] > 0:

        print(
            "STATUS: Portfolio withdrawal "
            "required."
        )

    else:

        print(
            "STATUS: No portfolio withdrawal "
            "required."
        )


if __name__ == "__main__":

    print_withdrawal(
        2027,
        1,
    )