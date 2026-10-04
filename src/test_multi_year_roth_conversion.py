from decimal import Decimal

from portfolio_projection import (
    project_portfolio_years,
)


print("MULTI-YEAR ROTH CONVERSION TEST")
print("================================")


projections = project_portfolio_years(
    start_year=2027,
    end_year=2028,
    annual_return=Decimal("0.05"),
    withdrawals_by_year={
        2027: {},
        2028: {},
    },
    roth_conversions_by_year={
        2027: {
            "Chris 401(k)": Decimal("80000"),
        },
        2028: {
            "Chris 401(k)": Decimal("80000"),
        },
    },
)


projection_2027 = projections[0]
projection_2028 = projections[1]


balances_2027 = {
    account.account_name:
        account.ending_balance
    for account in projection_2027.accounts
}


balances_2028 = {
    account.account_name:
        account.ending_balance
    for account in projection_2028.accounts
}


print()
print("2027")
print("----")

print(
    f"Beginning portfolio: "
    f"${projection_2027.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection_2027.investment_gain_total:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection_2027.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection_2027.ending_total:,.2f}"
)

print(
    f"Chris 401(k): "
    f"${balances_2027['Chris 401(k)']:,.2f}"
)

print(
    f"Roth IRA: "
    f"${balances_2027['Roth IRA']:,.2f}"
)


print()
print("2028")
print("----")

print(
    f"Beginning portfolio: "
    f"${projection_2028.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection_2028.investment_gain_total:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection_2028.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection_2028.ending_total:,.2f}"
)

print(
    f"Chris 401(k): "
    f"${balances_2028['Chris 401(k)']:,.2f}"
)

print(
    f"Roth IRA: "
    f"${balances_2028['Roth IRA']:,.2f}"
)


# --------------------------------------------------
# Expected 2027 balances
# --------------------------------------------------

expected_2027_chris = (
    Decimal("752073")
    * Decimal("1.05")
    - Decimal("80000")
)

expected_2027_roth = (
    Decimal("31387")
    * Decimal("1.05")
    + Decimal("80000")
)


# --------------------------------------------------
# Expected 2028 balances
# --------------------------------------------------

expected_2028_chris = (
    expected_2027_chris
    * Decimal("1.05")
    - Decimal("80000")
)

expected_2028_roth = (
    expected_2027_roth
    * Decimal("1.05")
    + Decimal("80000")
)


# --------------------------------------------------
# Assertions
# --------------------------------------------------

assert (
    balances_2027["Chris 401(k)"]
    == expected_2027_chris
)

assert (
    balances_2027["Roth IRA"]
    == expected_2027_roth
)

assert (
    balances_2028["Chris 401(k)"]
    == expected_2028_chris
)

assert (
    balances_2028["Roth IRA"]
    == expected_2028_roth
)

assert (
    projection_2027.ending_total
    == projection_2028.beginning_total
)

assert (
    projection_2027.roth_conversion_total
    == Decimal("80000")
)

assert (
    projection_2028.roth_conversion_total
    == Decimal("80000")
)


print()
print(
    "PASS: 2027 Roth conversion correctly "
    "reduces Chris 401(k)."
)

print(
    "PASS: 2027 Roth conversion correctly "
    "increases Roth IRA."
)

print(
    "PASS: Roth IRA investment growth is "
    "correctly included."
)

print(
    "PASS: 2028 begins with the correct "
    "2027 ending balances."
)

print(
    "PASS: 2028 Roth conversion is applied "
    "exactly once."
)

print(
    "PASS: Investment returns compound "
    "correctly across both years."
)

print()
print(
    "PASS: Multi-year Roth conversion "
    "integration is working correctly."
)