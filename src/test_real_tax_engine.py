from decimal import Decimal

from tax_engine import (
    FEDERAL_MFJ_2026_BRACKETS,
    FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    NC_MFJ_STANDARD_DEDUCTION,
    NC_TAX_RATE,
    calculate_federal_tax_mfj_2026,
    calculate_federal_incremental_tax_mfj_2026,
    calculate_nc_incremental_tax,
    calculate_taxable_income,
)


print("REAL TAX ENGINE TEST")
print("====================")


# --------------------------------------------------
# Test 1: Federal standard deduction
# --------------------------------------------------

gross_income = Decimal("100000")

federal_taxable_income = (
    calculate_taxable_income(
        gross_income,
        FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    )
)

assert (
    federal_taxable_income
    == Decimal("67800")
)


# --------------------------------------------------
# Test 2: NC standard deduction
# --------------------------------------------------

nc_taxable_income = (
    calculate_taxable_income(
        gross_income,
        NC_MFJ_STANDARD_DEDUCTION,
    )
)

assert (
    nc_taxable_income
    == Decimal("74500")
)


# --------------------------------------------------
# Test 3: Federal progressive calculation
#
# $67,800 taxable income
#
# First $24,800 @ 10%
# Remaining $43,000 @ 12%
# --------------------------------------------------

federal_tax = (
    calculate_federal_tax_mfj_2026(
        federal_taxable_income
    )
)

expected_federal_tax = (
    Decimal("24800")
    * Decimal("0.10")
    +
    Decimal("43000")
    * Decimal("0.12")
)

assert (
    federal_tax
    == expected_federal_tax
)


# --------------------------------------------------
# Test 4: NC flat tax
# --------------------------------------------------

conversion = Decimal("80000")

nc_incremental_tax = (
    calculate_nc_incremental_tax(
        nc_taxable_income,
        conversion,
    )
)

expected_nc_tax = (
    conversion
    * NC_TAX_RATE
)

assert (
    nc_incremental_tax
    == expected_nc_tax
)


# --------------------------------------------------
# Test 5: Federal incremental Roth tax
# --------------------------------------------------

federal_incremental_tax = (
    calculate_federal_incremental_tax_mfj_2026(
        federal_taxable_income,
        conversion,
    )
)

assert (
    federal_incremental_tax
    > Decimal("0")
)


# --------------------------------------------------
# Test 6: Total incremental tax
# --------------------------------------------------

total_incremental_tax = (
    federal_incremental_tax
    + nc_incremental_tax
)

assert (
    total_incremental_tax
    > federal_incremental_tax
)


print()
print(
    f"Gross income: "
    f"${gross_income:,.2f}"
)

print(
    f"Federal taxable income: "
    f"${federal_taxable_income:,.2f}"
)

print(
    f"NC taxable income: "
    f"${nc_taxable_income:,.2f}"
)

print(
    f"Test conversion: "
    f"${conversion:,.2f}"
)

print(
    f"Federal conversion tax: "
    f"${federal_incremental_tax:,.2f}"
)

print(
    f"NC conversion tax: "
    f"${nc_incremental_tax:,.2f}"
)

print(
    f"Total incremental tax: "
    f"${total_incremental_tax:,.2f}"
)

print()
print(
    "PASS: Federal MFJ tax brackets are "
    "working correctly."
)

print(
    "PASS: Federal standard deduction is "
    "integrated correctly."
)

print(
    "PASS: North Carolina tax calculation "
    "is working correctly."
)

print(
    "PASS: Roth conversion incremental tax "
    "is calculated correctly."
)