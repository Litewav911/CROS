from decimal import Decimal

from portfolio_projection import (
    project_portfolio_years,
)


print("PORTFOLIO ANNUAL WITHDRAWAL INTEGRATION TEST")
print("=============================================")


projections = project_portfolio_years(
    start_year=2027,
    end_year=2040,
    annual_return=Decimal("0.05"),
)


print()

for projection in projections:

    print(
        f"{projection.year}: "
        f"Beginning "
        f"${projection.beginning_total:,.2f}"
        f" | Gain "
        f"${projection.investment_gain_total:,.2f}"
        f" | Withdrawal "
        f"${projection.withdrawal_total:,.2f}"
        f" | Ending "
        f"${projection.ending_total:,.2f}"
    )


# --------------------------------------------------
# Verify the complete 2027-2040 timeline.
# --------------------------------------------------

assert len(projections) == 14


# --------------------------------------------------
# Verify that each year begins with the prior year's
# ending portfolio.
# --------------------------------------------------

for index in range(1, len(projections)):

    previous_year = projections[index - 1]
    current_year = projections[index]

    assert (
        current_year.beginning_total
        == previous_year.ending_total
    )


# --------------------------------------------------
# Current test data produces no portfolio withdrawal.
# The portfolio should therefore simply compound
# at the 5% test return.
# --------------------------------------------------

assert (
    projections[0].withdrawal_total
    == Decimal("0")
)


assert (
    projections[-1].withdrawal_total
    == Decimal("0")
)


# --------------------------------------------------
# Verify the first year's return.
# --------------------------------------------------

expected_2027_gain = (
    Decimal("1219138.61")
    * Decimal("0.05")
)


assert (
    projections[0].investment_gain_total
    == expected_2027_gain
)


print()
print(
    f"2027 ending portfolio: "
    f"${projections[0].ending_total:,.2f}"
)

print(
    f"2040 ending portfolio: "
    f"${projections[-1].ending_total:,.2f}"
)

print()
print(
    "PASS: 2027-2040 portfolio projection "
    "is now driven by the annual withdrawal engine."
)