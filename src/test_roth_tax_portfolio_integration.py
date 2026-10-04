from decimal import Decimal

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)

from roth_conversion_integration import (
    calculate_roth_conversion,
)


print("ROTH TAX / PORTFOLIO INTEGRATION TEST")
print("=======================================")


# --------------------------------------------------
# Test parameters
# --------------------------------------------------

YEAR = 2027
BASE_TAXABLE_INCOME = Decimal("100000")
CONVERSION_AMOUNT = Decimal("80000")
ANNUAL_RETURN = Decimal("0")


# --------------------------------------------------
# Roth conversion tax calculation
# --------------------------------------------------

conversion = calculate_roth_conversion(
    year=YEAR,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    base_taxable_income=BASE_TAXABLE_INCOME,
    conversion_amount=CONVERSION_AMOUNT,
)


print()
print("ROTH CONVERSION")
print("----------------")

print(
    f"Conversion: "
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
    f"Net Roth amount: "
    f"${conversion.net_roth_amount:,.2f}"
)

print(
    f"Effective tax rate: "
    f"{conversion.effective_tax_rate:.3%}"
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


print()
print("PORTFOLIO")
print("---------")

print(
    f"Beginning portfolio: "
    f"${projection.beginning_total:,.2f}"
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
# Account balances
# --------------------------------------------------

ending_balances = {
    account.account_name:
        account.ending_balance
    for account in projection.accounts
}


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
    - CONVERSION_AMOUNT
)

expected_roth = (
    Decimal("31387")
    + CONVERSION_AMOUNT
)

expected_portfolio = (
    Decimal("1219138.61")
)


# --------------------------------------------------
# Tax assertions
# --------------------------------------------------

assert (
    conversion.year
    == YEAR
)

assert (
    conversion.source_account
    == "Chris 401(k)"
)

assert (
    conversion.destination_account
    == "Roth IRA"
)

assert (
    conversion.base_taxable_income
    == BASE_TAXABLE_INCOME
)

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

# $20,712 / $80,000 = 0.2589 exactly.
assert (
    conversion.effective_tax_rate
    == Decimal("0.2589")
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
    "PASS: Roth conversion reduces "
    "the source 401(k) correctly."
)

print(
    "PASS: Roth conversion increases "
    "the Roth IRA correctly."
)

print(
    "PASS: Roth conversion does not "
    "reduce total portfolio value."
)

print(
    "PASS: Federal conversion tax is "
    "calculated correctly."
)

print(
    "PASS: North Carolina conversion tax "
    "is calculated correctly."
)

print(
    "PASS: Conversion tax is tracked "
    "separately from the portfolio transfer."
)

print(
    "PASS: Effective tax rate is "
    "calculated correctly."
)

print()
print(
    "PASS: Roth tax and portfolio "
    "integration is working correctly."
)