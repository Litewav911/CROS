from decimal import Decimal

from portfolio_projection import (
    project_portfolio_year,
    project_portfolio_years,
)


print("PORTFOLIO WITHDRAWAL TEST")
print("==========================")


balances_2027 = {
    "Chris 401(k)": Decimal("752073"),
    "Stephanie 401(k)": Decimal("414214.61"),
    "Brokerage": Decimal("0"),
    "Roth IRA": Decimal("31387"),
    "HSA": Decimal("21464"),
    "Cash Reserve": Decimal("0"),
}


# --------------------------------------------------
# Test a $60,000 withdrawal from Chris 401(k).
# --------------------------------------------------

withdrawals = {
    "Chris 401(k)": Decimal("60000"),
}


projection = project_portfolio_year(
    year=2027,
    account_balances=balances_2027,
    annual_return=Decimal("0.05"),
    withdrawals=withdrawals,
)


print()
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
    f"Ending portfolio: "
    f"${projection.ending_total:,.2f}"
)


# --------------------------------------------------
# Find the individual account results.
# --------------------------------------------------

chris = next(
    account
    for account in projection.accounts
    if account.account_name
    == "Chris 401(k)"
)


stephanie = next(
    account
    for account in projection.accounts
    if account.account_name
    == "Stephanie 401(k)"
)


print()
print(
    f"Chris 401(k) ending: "
    f"${chris.ending_balance:,.2f}"
)

print(
    f"Stephanie 401(k) ending: "
    f"${stephanie.ending_balance:,.2f}"
)


# Chris:
# $752,073 + $37,603.65 gain - $60,000
# = $729,676.65

expected_chris = (
    Decimal("752073")
    + (
        Decimal("752073")
        * Decimal("0.05")
    )
    - Decimal("60000")
)


assert (
    chris.ending_balance
    == expected_chris
)


# Stephanie was not withdrawn from.

expected_stephanie = (
    Decimal("414214.61")
    + (
        Decimal("414214.61")
        * Decimal("0.05")
    )
)


assert (
    stephanie.ending_balance
    == expected_stephanie
)


assert (
    projection.withdrawal_total
    == Decimal("60000")
)


# --------------------------------------------------
# Verify the withdrawal carries into the following
# year's beginning balance.
# --------------------------------------------------

withdrawals_by_year = {
    2027: {
        "Chris 401(k)": Decimal("60000"),
    }
}


projections = project_portfolio_years(
    start_year=2027,
    end_year=2028,
    annual_return=Decimal("0.05"),
    withdrawals_by_year=withdrawals_by_year,
)


assert len(projections) == 2


assert (
    projections[1].beginning_total
    == projections[0].ending_total
)


print()
print(
    f"2027 ending portfolio: "
    f"${projections[0].ending_total:,.2f}"
)

print(
    f"2028 beginning portfolio: "
    f"${projections[1].beginning_total:,.2f}"
)


print()
print(
    "PASS: Account-specific withdrawals correctly "
    "reduce the designated account and carry forward."
)