from decimal import Decimal

from spending_variance import calculate_spending_variance


result = calculate_spending_variance(
    2027,
    1,
)


print("SPENDING VARIANCE TEST")
print("======================")

print(
    f"Planned: "
    f"${result['planned_spending']:,.2f}"
)

print(
    f"Actual: "
    f"${result['actual_spending']:,.2f}"
)

print(
    f"Variance: "
    f"${result['dollar_variance']:,.2f}"
)

print(
    f"Percentage: "
    f"{result['percentage_variance']:,.2f}%"
)


assert (
    result["planned_spending"]
    == Decimal("11000")
)

assert (
    result["actual_spending"]
    == Decimal("438.24")
)

assert (
    result["dollar_variance"]
    == Decimal("-10561.76")
)


expected_percentage = (
    Decimal("-10561.76")
    / Decimal("11000")
) * Decimal("100")


assert (
    abs(
        result["percentage_variance"]
        - expected_percentage
    )
    < Decimal("0.000001")
)


print()
print(
    "PASS: Spending variance calculation "
    "is correct."
)