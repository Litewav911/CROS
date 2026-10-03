from decimal import Decimal

from withdrawal_engine import (
    calculate_portfolio_withdrawal,
)

from withdrawal_strategy import (
    select_withdrawal_source,
)


def calculate_withdrawal_recommendation(
    year: int,
    month: int,
    market_decline: bool = False,
):
    """
    Combine the portfolio withdrawal calculation
    with the withdrawal-source strategy.

    This produces a preliminary recommendation.

    Tax optimization, Roth conversions, RMDs,
    Social Security, and account balances will
    be incorporated by later components.
    """

    withdrawal = calculate_portfolio_withdrawal(
        year,
        month,
    )

    amount = withdrawal[
        "portfolio_withdrawal"
    ]

    decision = select_withdrawal_source(
        amount,
        market_decline=market_decline,
    )

    return {
        "year": year,
        "month": month,

        "actual_spending":
            withdrawal["actual_spending"],

        "transaction_income":
            withdrawal["transaction_income"],

        "rental_income":
            withdrawal["rental_income"],

        "portfolio_withdrawal":
            amount,

        "recommended_source":
            decision.source,

        "reason":
            decision.reason,

        "market_decline":
            market_decline,
    }


def print_recommendation(
    year: int,
    month: int,
    market_decline: bool = False,
):

    result = calculate_withdrawal_recommendation(
        year,
        month,
        market_decline,
    )

    print()
    print(
        f"WITHDRAWAL RECOMMENDATION: "
        f"{year}-{month:02d}"
    )
    print("=" * 65)

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

    print()

    print(
        f"{'Portfolio withdrawal required':35}"
        f"${result['portfolio_withdrawal']:,.2f}"
    )

    print(
        f"{'Recommended source':35}"
        f"{result['recommended_source']}"
    )

    print()

    print(
        f"Reason: {result['reason']}"
    )


if __name__ == "__main__":

    print_recommendation(
        2027,
        1,
        market_decline=False,
    )