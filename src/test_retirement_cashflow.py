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
    f"Actual income: "
    f"${result['actual_income']:,.2f}"
)

print(
    f"Net cash requirement: "
    f"${result['net_cash_requirement']:,.2f}"
)

print(
    f"Planned spending: "
    f"${result['planned_spending']:,.2f}"
)

print(
    f"Spending variance: "
    f"${result['spending_variance']:,.2f}"
)


assert (
    result["actual_spending"]
    == Decimal("438.24")
)

assert (
    result["actual_income"]
    == Decimal("4250.00")
)

assert (
    result["net_cash_requirement"]
    == Decimal("-3811.76")
)

assert (
    result["planned_spending"]
    == Decimal("11000")
)


print()
print("PASS: Retirement cash-flow calculations are correct.")