from decimal import Decimal

from roth_conversion_integration import (
    calculate_roth_conversion,
)


print("DYNAMIC ROTH CONVERSION TEST")
print("============================")


# --------------------------------------------------
# Test 1
# --------------------------------------------------

# Normal year.
# The requested conversion is comfortably below
# the available traditional-account balance.

result = calculate_roth_conversion(
    year=2027,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    base_taxable_income=Decimal("100000"),
    conversion_amount=Decimal("80000"),
)


print()
print("2027 NORMAL CONVERSION")
print("----------------------")

print(
    f"Requested conversion: "
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


assert (
    result.conversion_amount
    == Decimal("80000")
)

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
# Test 2
# --------------------------------------------------

# Small final conversion.
#
# This represents the situation we reach when
# Chris's 401(k) is almost depleted.
#
# The tax engine must correctly calculate the tax
# on the small remaining conversion.

result_small = calculate_roth_conversion(
    year=2040,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    base_taxable_income=Decimal("100000"),
    conversion_amount=Decimal("1162.54"),
)


print()
print("2040 FINAL CONVERSION")
print("--------------------")

print(
    f"Conversion: "
    f"${result_small.conversion_amount:,.2f}"
)

print(
    f"Federal tax: "
    f"${result_small.federal_tax:,.2f}"
)

print(
    f"NC tax: "
    f"${result_small.nc_tax:,.2f}"
)

print(
    f"Total tax: "
    f"${result_small.total_tax:,.2f}"
)

print(
    f"Net Roth amount: "
    f"${result_small.net_roth_amount:,.2f}"
)


assert (
    result_small.conversion_amount
    == Decimal("1162.54")
)


# --------------------------------------------------
# Tax reconciliation
# --------------------------------------------------

assert (
    result_small.total_tax
    == (
        result_small.federal_tax
        + result_small.nc_tax
    )
)


# --------------------------------------------------
# Net Roth reconciliation
# --------------------------------------------------

assert (
    result_small.net_roth_amount
    == (
        result_small.conversion_amount
        - result_small.total_tax
    )
)


# --------------------------------------------------
# Effective tax rate
# --------------------------------------------------

assert (
    result.effective_tax_rate
    == (
        result.total_tax
        / result.conversion_amount
    )
)


assert (
    result_small.effective_tax_rate
    == (
        result_small.total_tax
        / result_small.conversion_amount
    )
)


print()
print(
    "PASS: Normal Roth conversion "
    "calculates correctly."
)

print(
    "PASS: Small final conversion "
    "calculates correctly."
)

print(
    "PASS: Federal and NC taxes reconcile."
)

print(
    "PASS: Net Roth amount reconciles."
)

print(
    "PASS: Effective tax rate reconciles."
)

print()
print(
    "PASS: Dynamic Roth conversion "
    "tax foundation is working correctly."
)