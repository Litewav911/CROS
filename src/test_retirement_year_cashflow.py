from decimal import Decimal

from retirement_year_cashflow import (
    calculate_year_cashflow,
)


print("RETIREMENT YEAR CASH FLOW TEST")
print("===============================")


result = calculate_year_cashflow(
    2027,
    Decimal("132000"),
)


print()
print(
    f"Planned spending: "
    f"${result['planned_spending']:,.2f}"
)

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
    f"Portfolio requirement: "
    f"${result['portfolio_requirement']:,.2f}"
)


# --------------------------------------------------
# Basic annual projection checks
# --------------------------------------------------

assert (
    result["planned_spending"]
    == Decimal("132000")
)


# January contains the five test transactions.
assert (
    result["actual_spending"]
    == Decimal("438.24")
)


assert (
    result["transaction_income"]
    == Decimal("4250")
)


# --------------------------------------------------
# Verify the annual rental total by summing the
# actual monthly results rather than assuming that
# a rounded monthly number multiplied by 12 will
# exactly equal the annual result.
# --------------------------------------------------

monthly_rental_total = sum(
    (
        month["rental_income"]
        for month in result["monthly_results"]
    ),
    Decimal("0"),
)


assert (
    result["rental_income"]
    == monthly_rental_total
)


# --------------------------------------------------
# Current test transactions do not require a
# portfolio withdrawal.
# --------------------------------------------------

assert (
    result["portfolio_requirement"]
    == Decimal("0")
)


# --------------------------------------------------
# Verify that all 12 months were processed.
# --------------------------------------------------

assert (
    len(result["monthly_results"])
    == 12
)


print()
print(
    f"Projection months: "
    f"{len(result['monthly_results'])}"
)

print(
    f"Summed monthly rental income: "
    f"${monthly_rental_total:,.2f}"
)

print()
print(
    "PASS: Annual retirement cash flow "
    "correctly incorporates the monthly "
    "cash-flow engine."
)