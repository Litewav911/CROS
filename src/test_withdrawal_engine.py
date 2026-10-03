from decimal import Decimal

from withdrawal_engine import (
    calculate_portfolio_withdrawal,
)


result = calculate_portfolio_withdrawal(
    2027,
    1,
)


print("PORTFOLIO WITHDRAWAL TEST")
print("=========================")

print(
    f"Actual spending: "
    f"${result['actual_spending']:,.2f}"
)

print(
    f"Transaction income: "
    f"${result['transaction_income']:,.2f}"
)

print(
    f"Rental income: "
    f"${result['rental_income']:,.2f}"
)

print(
    f"Portfolio withdrawal: "
    f"${result['portfolio_withdrawal']:,.2f}"
)

print(
    f"Excess cash: "
    f"${result['excess_cash']:,.2f}"
)


assert (
    result["portfolio_withdrawal"]
    == Decimal("0")
)

assert (
    result["excess_cash"].quantize(
        Decimal("0.01")
    )
    == Decimal("6698.10")
)


print()
print(
    "PASS: Portfolio withdrawal engine "
    "is working correctly."
)