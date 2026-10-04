from decimal import Decimal

from portfolio_projection import (
    project_portfolio_year,
    project_portfolio_years,
)


print("PORTFOLIO INVESTMENT RETURN TEST")
print("=================================")


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
    annual_return=Decimal("0.05"),
)


print()
print(
    f"Beginning portfolio: "
    f"${projection_2027.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection_2027.investment_gain_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection_2027.ending_total:,.2f}"
)


expected_gain = (
    Decimal("1219138.61")
    * Decimal("0.05")
)


expected_ending = (
    Decimal("1219138.61")
    + expected_gain
)


assert (
    projection_2027.beginning_total
    == Decimal("1219138.61")
)


assert (
    projection_2027.investment_gain_total
    == expected_gain
)


assert (
    projection_2027.ending_total
    == expected_ending
)


# --------------------------------------------------
# Verify that returns compound year-to-year.
# --------------------------------------------------

projections = project_portfolio_years(
    start_year=2027,
    end_year=2040,
    annual_return=Decimal("0.05"),
)


assert len(projections) == 14


for index in range(1, len(projections)):

    previous_year = projections[index - 1]
    current_year = projections[index]

    assert (
        current_year.beginning_total
        == previous_year.ending_total
    )


print()
print(
    f"2027 ending: "
    f"${projections[0].ending_total:,.2f}"
)

print(
    f"2040 ending: "
    f"${projections[-1].ending_total:,.2f}"
)


print()
print(
    "PASS: Investment returns correctly "
    "compound through the multi-year projection."
)