from decimal import Decimal

from roth_conversion_integration import (
    calculate_roth_conversion,
)


print("ROTH CONVERSION / TAX INTEGRATION TEST")
print("=======================================")


# --------------------------------------------------
# Test inputs
# --------------------------------------------------

YEAR = 2027
BASE_TAXABLE_INCOME = Decimal("100000")
CONVERSION_AMOUNT = Decimal("80000")


# --------------------------------------------------
# Calculate Roth conversion
# --------------------------------------------------

result = calculate_roth_conversion(
    year=YEAR,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    base_taxable_income=BASE_TAXABLE_INCOME,
    conversion_amount=CONVERSION_AMOUNT,
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print()
print(
    f"Year: {result.year}"
)

print(
    f"Source: {result.source_account}"
)

print(
    f"Destination: {result.destination_account}"
)

print(
    f"Base taxable income: "
    f"${result.base_taxable_income:,.2f}"
)

print(
    f"Conversion amount: "
    f"${result.conversion_amount:,.2f}"
)

print(
    f"Federal tax: "
    f"${result.federal_tax:,.2f}"
)

print(
    f"NC tax: "
    f"${result.nc_tax:,.2f}"
)

print(
    f"Total tax: "
    f"${result.total_tax:,.2f}"
)

print(
    f"Net Roth amount: "
    f"${result.net_roth_amount:,.2f}"
)

print(
    f"Effective tax rate: "
    f"{result.effective_tax_rate:.3%}"
)


# --------------------------------------------------
# Basic conversion assertions
# --------------------------------------------------

assert (
    result.year
    == YEAR
)

assert (
    result.source_account
    == "Chris 401(k)"
)

assert (
    result.destination_account
    == "Roth IRA"
)

assert (
    result.base_taxable_income
    == BASE_TAXABLE_INCOME
)

assert (
    result.conversion_amount
    == CONVERSION_AMOUNT
)


# --------------------------------------------------
# Current real tax-engine results
# --------------------------------------------------

assert (
    result.federal_tax
    == Decimal("17520")
)

assert (
    result.nc_tax
    == Decimal("3192")
)

assert (
    result.total_tax
    == Decimal("20712")
)

assert (
    result.net_roth_amount
    == Decimal("59288")
)


# --------------------------------------------------
# Effective tax rate
# --------------------------------------------------

expected_effective_rate = (
    Decimal("20712")
    / Decimal("80000")
)


assert (
    result.effective_tax_rate
    == expected_effective_rate
)


# --------------------------------------------------
# Final results
# --------------------------------------------------

print()
print(
    "PASS: Roth conversion inputs are "
    "correctly recorded."
)

print(
    "PASS: Federal tax is correctly "
    "calculated by the real tax engine."
)

print(
    "PASS: North Carolina tax is correctly "
    "calculated by the real tax engine."
)

print(
    "PASS: Total incremental tax is correct."
)

print(
    "PASS: Net Roth amount is correct."
)

print(
    "PASS: Effective tax rate is correct."
)

print()
print(
    "PASS: Roth conversion integration "
    "with the tax engine is working correctly."
)