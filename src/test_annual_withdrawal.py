from decimal import Decimal

from annual_withdrawal import (
    calculate_annual_withdrawal,
)

from rental_cashflow import (
    monthly_rental_cashflow,
)


print("ANNUAL WITHDRAWAL TEST")
print("=======================")


result = calculate_annual_withdrawal(
    2027,
    market_decline=False,
)


print()
print(
    f"Months processed: "
    f"{len(result['monthly_results'])}"
)

print(
    f"Annual spending: "
    f"${result['total_spending']:,.2f}"
)

print(
    f"Transaction income: "
    f"${result['total_transaction_income']:,.2f}"
)

print(
    f"Rental income: "
    f"${result['total_rental_income']:,.2f}"
)

print(
    f"Total cash available: "
    f"${result['total_cash_available']:,.2f}"
)

print(
    f"Annual portfolio requirement: "
    f"${result['annual_portfolio_requirement']:,.2f}"
)

print(
    f"Recommended source: "
    f"{result['recommended_source']}"
)


# --------------------------------------------------
# Verify all twelve months were processed.
# --------------------------------------------------

assert (
    len(result["monthly_results"])
    == 12
)


# --------------------------------------------------
# Get the authoritative monthly rental value from
# the existing rental engine.
#
# Do not hard-code a rounded annual multiplication.
# --------------------------------------------------

monthly_rental = Decimal(
    str(
        monthly_rental_cashflow()[
            "net_rental_cashflow"
        ]
    )
)


expected_rental_income = Decimal("0")

for month in range(1, 13):

    expected_rental_income += monthly_rental


assert (
    result["total_rental_income"]
    == expected_rental_income
)


# --------------------------------------------------
# The current test data does not create an annual
# portfolio requirement because the actual spending
# recorded in the test environment is covered by
# available cash sources.
# --------------------------------------------------

assert (
    result["annual_portfolio_requirement"]
    == Decimal("0")
)


assert (
    result["recommended_source"]
    == "None"
)


print()
print(
    f"Authoritative monthly rental cash flow: "
    f"${monthly_rental:,.2f}"
)

print(
    f"Expected annual rental cash flow: "
    f"${expected_rental_income:,.2f}"
)

print()
print(
    "PASS: Annual withdrawal engine processes "
    "all 12 months and aggregates cash flow correctly."
)