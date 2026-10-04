from decimal import Decimal

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)
from roth_conversion import create_roth_conversion


print("ANNUAL ROTH TAX INTEGRATION TEST")
print("=================================")


# --------------------------------------------------
# Roth conversion
# --------------------------------------------------

conversion = create_roth_conversion(
    year=2027,
    base_taxable_income=Decimal("67800"),
    conversion_amount=Decimal("80000"),
)

assert conversion.conversion_amount == Decimal("80000")
assert conversion.federal_tax > Decimal("0")
assert conversion.nc_tax > Decimal("0")
assert conversion.total_tax > Decimal("0")


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
#
# IMPORTANT:
#
# The portfolio receives the FULL gross conversion.
#
# $80,000 leaves the traditional account and
# $80,000 enters the Roth IRA.
#
# Therefore the conversion itself does NOT reduce
# total portfolio value.
#
# Conversion tax is handled separately.
# --------------------------------------------------

balances = create_initial_account_balances()

beginning_total = sum(
    balances.values(),
    Decimal("0"),
)

projection = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0.05"),
    withdrawals={},
    roth_conversions={
        "Chris 401(k)": Decimal("80000"),
    },
)

expected_ending_total = (
    beginning_total
    * Decimal("1.05")
)

assert (
    projection.ending_total
    == expected_ending_total
), (
    "Gross Roth conversion must be "
    "portfolio-value neutral."
)

assert (
    projection.roth_conversion_total
    == Decimal("80000")
)

assert (
    projection.withdrawal_total
    == Decimal("0")
)


# --------------------------------------------------
# Defensive compatibility check
#
# Some older integrations called a compatibility
# helper after project_portfolio_year().
#
# That helper must NOT apply the conversion a
# second time.
# --------------------------------------------------

from portfolio_projection import (
    apply_roth_conversion_destination,
)

projected_balances = {
    account.account_name:
        account.ending_balance
    for account in projection.accounts
}

before_compatibility_check = dict(
    projected_balances
)

after_compatibility_check = (
    apply_roth_conversion_destination(
        projected_balances,
        "Chris 401(k)",
        "Roth IRA",
        Decimal("80000"),
    )
)

assert (
    after_compatibility_check
    == before_compatibility_check
), (
    "Compatibility helper must not apply "
    "the Roth conversion a second time."
)


print()
print("PORTFOLIO")
print("---------")
print(
    f"Beginning portfolio: "
    f"${beginning_total:,.2f}"
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
print("DEFENSIVE COMPATIBILITY CHECK")
print("-----------------------------")
print(
    "PASS: compatibility helper did not "
    "double-apply the conversion."
)


print()
print(
    "PASS: Roth conversion is transferred "
    "at gross value."
)

print(
    "PASS: conversion tax is calculated "
    "separately."
)

print(
    "PASS: portfolio value is unchanged "
    "by the conversion itself."
)