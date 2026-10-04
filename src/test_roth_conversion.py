from decimal import Decimal

from roth_conversion import (
    create_roth_conversion,
)


print("ROTH CONVERSION REAL TAX ENGINE TEST")
print("====================================")


conversion = create_roth_conversion(
    year=2027,
    base_taxable_income=Decimal("67800"),
    conversion_amount=Decimal("80000"),
)


print()
print(
    f"Year: {conversion.year}"
)

print(
    f"Source: {conversion.source_account}"
)

print(
    f"Destination: {conversion.destination_account}"
)

print(
    f"Base taxable income: "
    f"${conversion.base_taxable_income:,.2f}"
)

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
    f"Net Roth amount: "
    f"${conversion.net_roth_amount:,.2f}"
)

print(
    f"Effective tax rate: "
    f"{conversion.effective_tax_rate:.2%}"
)


# --------------------------------------------------
# Expected results
#
# Federal:
#
# Base taxable income = $67,800
# Conversion = $80,000
# Combined = $147,800
#
# The incremental federal tax is $14,300.
#
# NC:
#
# $80,000 × 3.99% = $3,192
# --------------------------------------------------

assert (
    conversion.federal_tax
    == Decimal("14300")
)

assert (
    conversion.nc_tax
    == Decimal("3192")
)

assert (
    conversion.total_tax
    == Decimal("17492")
)

assert (
    conversion.net_roth_amount
    == Decimal("62508")
)

assert (
    conversion.effective_tax_rate
    == Decimal("0.21865")
)


print()
print(
    "PASS: Roth conversion automatically "
    "uses the real tax engine."
)

print(
    "PASS: Federal and NC taxes are calculated "
    "without test brackets."
)

print(
    "PASS: Total tax, net Roth amount, and "
    "effective tax rate are correct."
)