from decimal import Decimal

from portfolio_projection import (
    project_portfolio_year,
    project_portfolio_years,
)


print("PORTFOLIO YEAR-TO-YEAR TEST")
print("============================")


# --------------------------------------------------
# Initial 2027 balances
# --------------------------------------------------

balances_2027 = {
    "Chris 401(k)": Decimal("752073"),
    "Stephanie 401(k)": Decimal("414214.61"),
    "Brokerage": Decimal("0"),
    "Roth IRA": Decimal("31387"),
    "HSA": Decimal("21464"),
    "Cash Reserve": Decimal("0"),
}


projection_2027 = project_portfolio_year(
    year=2027,
    account_balances=balances_2027,
)


print()
print(
    f"2027 beginning: "
    f"${projection_2027.beginning_total:,.2f}"
)

print(
    f"2027 ending: "
    f"${projection_2027.ending_total:,.2f}"
)


assert (
    projection_2027.beginning_total
    == Decimal("1219138.61")
)


assert (
    projection_2027.ending_total
    == Decimal("1219138.61")
)


# --------------------------------------------------
# Verify the multi-year projection
# --------------------------------------------------

projections = project_portfolio_years(
    start_year=2027,
    end_year=2040,
)


assert len(projections) == 14


assert projections[0].year == 2027
assert projections[-1].year == 2040


# Every year's beginning balance must equal
# the previous year's ending balance.

for index in range(1, len(projections)):

    previous_year = projections[index - 1]
    current_year = projections[index]

    assert (
        current_year.beginning_total
        == previous_year.ending_total
    )


print()
print(
    f"First year: "
    f"{projections[0].year}"
)

print(
    f"Last year: "
    f"{projections[-1].year}"
)

print(
    f"2027 ending: "
    f"${projections[0].ending_total:,.2f}"
)

print(
    f"2040 beginning: "
    f"${projections[-1].beginning_total:,.2f}"
)

print(
    f"2040 ending: "
    f"${projections[-1].ending_total:,.2f}"
)


print()
print(
    "PASS: Account balances correctly "
    "carry forward from one year to the next."
)