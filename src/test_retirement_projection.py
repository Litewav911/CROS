from decimal import Decimal

from retirement_projection import (
    create_retirement_year,
    project_years,
)


print("RETIREMENT PROJECTION TEST")
print("===========================")


projection = create_retirement_year(
    year=2027,
    starting_total_assets=Decimal(
        "1000000"
    ),
    planned_spending=Decimal(
        "132000"
    ),
    rental_cash_flow=Decimal(
        "34636.08"
    ),
    portfolio_withdrawal=Decimal(
        "50000"
    ),
    roth_conversion=Decimal(
        "80000"
    ),
    investment_gain=Decimal(
        "60000"
    ),
)


print()
print(
    f"Starting assets: "
    f"${projection.starting_total_assets:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection.investment_gain:,.2f}"
)

print(
    f"Portfolio withdrawal: "
    f"${projection.portfolio_withdrawal:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection.roth_conversion:,.2f}"
)

print(
    f"Ending assets: "
    f"${projection.ending_total_assets:,.2f}"
)


expected = (
    Decimal("1000000")
    + Decimal("60000")
    - Decimal("50000")
    - Decimal("80000")
)


assert (
    projection.ending_total_assets
    == expected
)


timeline = project_years(
    start_year=2027,
    end_year=2040,
    starting_total_assets=Decimal(
        "1219138.61"
    ),
    planned_annual_spending=Decimal(
        "132000"
    ),
    annual_rental_cash_flow=Decimal(
        "34636.08"
    ),
)


assert len(timeline) == 14

assert timeline[0].year == 2027
assert timeline[-1].year == 2040

assert (
    timeline[0].starting_total_assets
    == Decimal("1219138.61")
)


print()
print(
    f"Projection years: "
    f"{timeline[0].year}"
    f"-"
    f"{timeline[-1].year}"
)

print(
    f"Number of years: "
    f"{len(timeline)}"
)

print()
print(
    "PASS: Retirement projection "
    "timeline is working correctly."
)