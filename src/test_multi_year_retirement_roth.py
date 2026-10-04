from decimal import Decimal

from multi_year_retirement_roth import (
    calculate_multi_year_retirement_roth,
)


print("MULTI-YEAR RETIREMENT / ROTH INTEGRATION TEST")
print("===============================================")


results = calculate_multi_year_retirement_roth(
    start_year=2027,
    end_year=2028,
    annual_return=Decimal("0.05"),
    base_taxable_income_by_year={
        2027: Decimal("100000"),
        2028: Decimal("100000"),
    },
    roth_conversions_by_year={
        2027: {
            "Chris 401(k)": Decimal("80000"),
        },
        2028: {
            "Chris 401(k)": Decimal("80000"),
        },
    },
    withdrawals_by_year={
        2027: {},
        2028: {},
    },
)


result_2027 = results[0]
result_2028 = results[1]


projection_2027 = (
    result_2027["projection"]
)

projection_2028 = (
    result_2028["projection"]
)

balances_2027 = (
    result_2027["ending_balances"]
)

balances_2028 = (
    result_2028["ending_balances"]
)


# --------------------------------------------------
# Display 2027
# --------------------------------------------------

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

print(
    f"Federal conversion tax: "
    f"${result_2027['roth_conversion'].federal_tax:,.2f}"
)

print(
    f"NC conversion tax: "
    f"${result_2027['roth_conversion'].nc_tax:,.2f}"
)


# --------------------------------------------------
# Display 2028
# --------------------------------------------------

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

print(
    f"Federal conversion tax: "
    f"${result_2028['roth_conversion'].federal_tax:,.2f}"
)

print(
    f"NC conversion tax: "
    f"${result_2028['roth_conversion'].nc_tax:,.2f}"
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
    len(results)
    == 2
)

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


# --------------------------------------------------
# Year-to-year carry-forward
# --------------------------------------------------

assert (
    projection_2027.ending_total
    == projection_2028.beginning_total
)


# --------------------------------------------------
# Roth conversion assertions
# --------------------------------------------------

assert (
    projection_2027.roth_conversion_total
    == Decimal("80000")
)

assert (
    projection_2028.roth_conversion_total
    == Decimal("80000")
)


assert (
    result_2027["roth_conversion"].total_tax
    == Decimal("20712")
)

assert (
    result_2028["roth_conversion"].total_tax
    == Decimal("20712")
)


# --------------------------------------------------
# Portfolio accounting
# --------------------------------------------------

expected_2027_portfolio = (
    projection_2027.beginning_total
    + projection_2027.investment_gain_total
    - projection_2027.withdrawal_total
)

expected_2028_portfolio = (
    projection_2028.beginning_total
    + projection_2028.investment_gain_total
    - projection_2028.withdrawal_total
)


assert (
    projection_2027.ending_total
    == expected_2027_portfolio
)

assert (
    projection_2028.ending_total
    == expected_2028_portfolio
)


# --------------------------------------------------
# Final results
# --------------------------------------------------

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
    "PASS: 2028 begins with the correct "
    "2027 ending balances."
)

print(
    "PASS: 2028 Roth conversion is applied "
    "exactly once."
)

print(
    "PASS: Roth IRA investment growth compounds "
    "correctly across both years."
)

print(
    "PASS: Roth conversion taxes are calculated "
    "for each year."
)

print(
    "PASS: Portfolio accounting remains correct "
    "across multiple years."
)

print()
print(
    "PASS: Multi-year retirement / Roth "
    "integration is working correctly."
)