from decimal import Decimal

from annual_retirement_roth_integration import (
    calculate_annual_retirement_roth,
)


print("ANNUAL RETIREMENT / ROTH INTEGRATION TEST")
print("===========================================")


YEAR = 2027
ANNUAL_RETURN = Decimal("0.05")
BASE_TAXABLE_INCOME = Decimal("100000")
CONVERSION_AMOUNT = Decimal("80000")


# --------------------------------------------------
# Run the actual integration engine
# --------------------------------------------------

result = calculate_annual_retirement_roth(
    year=YEAR,
    annual_return=ANNUAL_RETURN,
    base_taxable_income=BASE_TAXABLE_INCOME,
    roth_conversion_amount=CONVERSION_AMOUNT,
    market_decline=False,
)


conversion = result[
    "roth_conversion"
]

projection = result[
    "projection"
]

ending_balances = result[
    "ending_balances"
]


# --------------------------------------------------
# Display retirement cash flow
# --------------------------------------------------

print()
print("RETIREMENT CASH FLOW")
print("--------------------")

print(
    f"Annual spending: "
    f"${result['annual_spending']:,.2f}"
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

print(
    f"Withdrawal source: "
    f"{result['withdrawal_source']}"
)


# --------------------------------------------------
# Display Roth conversion
# --------------------------------------------------

print()
print("ROTH CONVERSION")
print("----------------")

print(
    f"Conversion amount: "
    f"${conversion.conversion_amount:,.2f}"
)

print(
    f"Federal tax: "
    f"${conversion.federal_tax:,.2f}"
)

print(
    f"NC tax: "
    f"${conversion.nc_tax:,.2f}"
)

print(
    f"Total conversion tax: "
    f"${conversion.total_tax:,.2f}"
)

print(
    f"Net Roth amount: "
    f"${conversion.net_roth_amount:,.2f}"
)


# --------------------------------------------------
# Display portfolio
# --------------------------------------------------

print()
print("PORTFOLIO PROJECTION")
print("--------------------")

print(
    f"Beginning portfolio: "
    f"${projection.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection.investment_gain_total:,.2f}"
)

print(
    f"Portfolio withdrawal: "
    f"${projection.withdrawal_total:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection.ending_total:,.2f}"
)


# --------------------------------------------------
# Display account balances
# --------------------------------------------------

print()
print("ACCOUNT BALANCES")
print("----------------")

print(
    f"Chris 401(k): "
    f"${ending_balances['Chris 401(k)']:,.2f}"
)

print(
    f"Roth IRA: "
    f"${ending_balances['Roth IRA']:,.2f}"
)


# --------------------------------------------------
# Roth tax assertions
# --------------------------------------------------

assert (
    conversion.conversion_amount
    == CONVERSION_AMOUNT
)

assert (
    conversion.federal_tax
    == Decimal("17520")
)

assert (
    conversion.nc_tax
    == Decimal("3192")
)

assert (
    conversion.total_tax
    == Decimal("20712")
)

assert (
    conversion.net_roth_amount
    == Decimal("59288")
)

assert (
    conversion.effective_tax_rate
    == Decimal("0.2589")
)


# --------------------------------------------------
# Roth portfolio assertions
# --------------------------------------------------

assert (
    projection.roth_conversion_total
    == CONVERSION_AMOUNT
)


expected_roth = (
    Decimal("31387")
    * Decimal("1.05")
    + CONVERSION_AMOUNT
)

assert (
    ending_balances["Roth IRA"]
    == expected_roth
)


# --------------------------------------------------
# Chris 401(k) verification
# --------------------------------------------------

expected_chris = (
    Decimal("752073")
    * Decimal("1.05")
    - CONVERSION_AMOUNT
)

if (
    result["withdrawal_source"]
    == "Chris 401(k)"
):

    expected_chris -= (
        result["portfolio_requirement"]
    )


assert (
    ending_balances["Chris 401(k)"]
    == expected_chris
)


# --------------------------------------------------
# Portfolio accounting verification
# --------------------------------------------------

expected_portfolio = (
    projection.beginning_total
    + projection.investment_gain_total
    - projection.withdrawal_total
)

assert (
    projection.ending_total
    == expected_portfolio
)


# --------------------------------------------------
# Final results
# --------------------------------------------------

print()
print(
    "PASS: Annual cash-flow engine feeds "
    "the annual retirement/Roth engine."
)

print(
    "PASS: Roth conversion tax is calculated "
    "from the tax engine."
)

print(
    "PASS: Chris 401(k) correctly reflects "
    "investment growth, withdrawals, and "
    "Roth conversion."
)

print(
    "PASS: Roth IRA correctly receives the "
    "conversion and investment growth."
)

print(
    "PASS: Roth conversion tax is tracked "
    "separately from the portfolio transfer."
)

print(
    "PASS: Portfolio accounting remains correct "
    "after the Roth conversion."
)

print()
print(
    "PASS: Annual retirement / Roth "
    "integration is working correctly."
)