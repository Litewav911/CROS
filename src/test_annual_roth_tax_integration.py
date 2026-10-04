from decimal import Decimal

from roth_conversion_integration import (
    calculate_roth_conversion,
)

from portfolio_projection import (
    project_portfolio_year,
    create_initial_account_balances,
)


print("ANNUAL ROTH TAX INTEGRATION TEST")
print("=================================")


YEAR = 2027
CONVERSION_AMOUNT = Decimal("80000")
ANNUAL_RETURN = Decimal("0.05")


# --------------------------------------------------
# Roth conversion tax calculation
# --------------------------------------------------

conversion = calculate_roth_conversion(
    year=YEAR,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    base_taxable_income=Decimal("100000"),
    conversion_amount=CONVERSION_AMOUNT,
)


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
    f"Total tax: "
    f"${conversion.total_tax:,.2f}"
)

print(
    f"Net Roth amount after tax: "
    f"${conversion.net_roth_amount:,.2f}"
)


# --------------------------------------------------
# Portfolio projection
# --------------------------------------------------

starting_balances = (
    create_initial_account_balances()
)


projection = project_portfolio_year(
    year=YEAR,
    account_balances=starting_balances,
    annual_return=ANNUAL_RETURN,
    withdrawals={},
    roth_conversions={
        "Chris 401(k)": CONVERSION_AMOUNT,
    },
)


ending_balances = {
    account.account_name:
        account.ending_balance
    for account in projection.accounts
}


print()
print("PORTFOLIO")
print("---------")

print(
    f"Beginning portfolio: "
    f"${projection.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection.investment_gain_total:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection.ending_total:,.2f}"
)


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
# Expected values
# --------------------------------------------------

expected_chris = (
    Decimal("752073")
    * Decimal("1.05")
    - CONVERSION_AMOUNT
)

expected_roth = (
    Decimal("31387")
    * Decimal("1.05")
    + CONVERSION_AMOUNT
)

expected_portfolio = (
    Decimal("1219138.61")
    * Decimal("1.05")
)


# --------------------------------------------------
# Roth tax assertions
# --------------------------------------------------

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


# --------------------------------------------------
# Portfolio assertions
# --------------------------------------------------

assert (
    ending_balances["Chris 401(k)"]
    == expected_chris
)

assert (
    ending_balances["Roth IRA"]
    == expected_roth
)

assert (
    projection.roth_conversion_total
    == CONVERSION_AMOUNT
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
    "PASS: Federal Roth conversion tax "
    "is correctly calculated."
)

print(
    "PASS: NC Roth conversion tax "
    "is correctly calculated."
)

print(
    "PASS: Total Roth conversion tax "
    "is correctly calculated."
)

print(
    "PASS: Net Roth conversion amount "
    "is correctly calculated."
)

print(
    "PASS: Chris 401(k) correctly reflects "
    "the conversion."
)

print(
    "PASS: Roth IRA correctly receives "
    "the conversion."
)

print(
    "PASS: Investment growth is correctly "
    "applied to both accounts."
)

print(
    "PASS: Roth conversion tax remains "
    "separate from the portfolio transfer."
)

print()
print(
    "PASS: Annual Roth tax integration "
    "is working correctly."
)