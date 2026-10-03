from decimal import Decimal

from retirement_cashflow import calculate_cashflow


result = calculate_cashflow(
    2027,
    1,
)


print("RETIREMENT CASH FLOW TEST")
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
    f"Total cash available: "
    f"${result['total_cash_available']:,.2f}"
)

print(
    f"Preliminary portfolio requirement: "
    f"${result['preliminary_portfolio_requirement']:,.2f}"
)


assert (
    result["actual_spending"]
    == Decimal("438.24")
)

assert (
    result["transaction_income"]
    == Decimal("4250.00")
)

assert (
    result["rental_income"].quantize(
        Decimal("0.01")
    )
    == Decimal("2886.34")
)

assert (
    result["total_cash_available"].quantize(
        Decimal("0.01")
    )
    == Decimal("7136.34")
)

assert (
    result["preliminary_portfolio_requirement"].quantize(
        Decimal("0.01")
    )
    == Decimal("-6698.10")
)


print()
print(
    "PASS: Retirement cash-flow calculations "
    "include rental cash flow correctly."
)