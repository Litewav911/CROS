from decimal import Decimal

from retirement_cashflow import (
    calculate_cashflow,
)

from withdrawal_strategy import (
    select_withdrawal_source,
)


def calculate_annual_withdrawal(
    year: int,
    market_decline: bool = False,
):
    """
    Calculate the total portfolio withdrawal required
    for an entire retirement year.

    Each month is calculated independently using the
    existing monthly retirement cash-flow engine.

    The twelve monthly portfolio requirements are then
    aggregated into one annual requirement.

    The withdrawal strategy determines the account
    that should provide the annual withdrawal.
    """

    monthly_results = []

    total_spending = Decimal("0")
    total_transaction_income = Decimal("0")
    total_rental_income = Decimal("0")
    total_cash_available = Decimal("0")

    annual_portfolio_requirement = Decimal("0")

    for month in range(1, 13):

        result = calculate_cashflow(
            year,
            month,
        )

        monthly_results.append(
            result
        )

        total_spending += Decimal(
            str(result["actual_spending"])
        )

        total_transaction_income += Decimal(
            str(result["transaction_income"])
        )

        total_rental_income += Decimal(
            str(result["rental_income"])
        )

        total_cash_available += Decimal(
            str(result["total_cash_available"])
        )

        # A negative monthly requirement means
        # household cash sources exceeded spending.
        monthly_requirement = Decimal(
            str(
                result[
                    "preliminary_portfolio_requirement"
                ]
            )
        )

        if monthly_requirement > 0:
            annual_portfolio_requirement += (
                monthly_requirement
            )

    decision = select_withdrawal_source(
        annual_portfolio_requirement,
        market_decline=market_decline,
    )

    return {
        "year": year,

        "monthly_results":
            monthly_results,

        "total_spending":
            total_spending,

        "total_transaction_income":
            total_transaction_income,

        "total_rental_income":
            total_rental_income,

        "total_cash_available":
            total_cash_available,

        "annual_portfolio_requirement":
            annual_portfolio_requirement,

        "recommended_source":
            decision.source,

        "reason":
            decision.reason,

        "market_decline":
            market_decline,
    }


def print_annual_withdrawal(
    year: int,
    market_decline: bool = False,
):

    result = calculate_annual_withdrawal(
        year,
        market_decline,
    )

    print()
    print(
        f"ANNUAL WITHDRAWAL: {year}"
    )

    print("=" * 70)

    print(
        f"{'Actual spending':35}"
        f"${result['total_spending']:,.2f}"
    )

    print(
        f"{'Transaction income':35}"
        f"${result['total_transaction_income']:,.2f}"
    )

    print(
        f"{'Rental cash flow':35}"
        f"${result['total_rental_income']:,.2f}"
    )

    print(
        f"{'Total cash available':35}"
        f"${result['total_cash_available']:,.2f}"
    )

    print()

    print(
        f"{'Annual portfolio requirement':35}"
        f"${result['annual_portfolio_requirement']:,.2f}"
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

    print_annual_withdrawal(
        2027,
        market_decline=False,
    )