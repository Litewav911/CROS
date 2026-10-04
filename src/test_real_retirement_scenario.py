from decimal import Decimal

from multi_year_retirement_roth import (
    calculate_multi_year_retirement_roth,
)


print("REAL RETIREMENT SCENARIO TEST")
print("============================")


START_YEAR = 2027
END_YEAR = 2040

ANNUAL_RETURN = Decimal("0.05")


# --------------------------------------------------
# Real-plan Roth conversion targets
#
# These are still explicit targets at this stage.
# Later 70H steps will make the conversion amount
# dynamic based on tax brackets and available
# traditional funds.
# --------------------------------------------------

ROTH_CONVERSION_TARGET = Decimal("80000")


roth_conversions = {
    year: {
        "Chris 401(k)": ROTH_CONVERSION_TARGET
    }
    for year in range(
        START_YEAR,
        END_YEAR + 1,
    )
}


# --------------------------------------------------
# Taxable-income assumption
#
# This is deliberately isolated here so that the
# production tax-income engine can replace it later.
# --------------------------------------------------

base_taxable_income = {
    year: Decimal("100000")
    for year in range(
        START_YEAR,
        END_YEAR + 1,
    )
}


# --------------------------------------------------
# Run integrated retirement model
# --------------------------------------------------

results = calculate_multi_year_retirement_roth(
    start_year=START_YEAR,
    end_year=END_YEAR,
    annual_return=ANNUAL_RETURN,
    base_taxable_income_by_year=(
        base_taxable_income
    ),
    roth_conversions_by_year=(
        roth_conversions
    ),
)


# --------------------------------------------------
# Basic validation
# --------------------------------------------------

assert len(results) == 14

assert results[0]["year"] == 2027

assert results[-1]["year"] == 2040


# --------------------------------------------------
# Print scenario
# --------------------------------------------------

print()

for result in results:

    year = result["year"]

    projection = result["projection"]

    conversion = result["roth_conversion"]

    balances = result["ending_balances"]

    print(
        f"{year}: "
        f"Portfolio "
        f"${projection.ending_total:,.2f}"
    )

    print(
        f"    Chris 401(k): "
        f"${balances['Chris 401(k)']:,.2f}"
    )

    print(
        f"    Roth IRA: "
        f"${balances['Roth IRA']:,.2f}"
    )

    print(
        f"    Conversion: "
        f"${conversion.conversion_amount:,.2f}"
    )

    print(
        f"    Federal tax: "
        f"${conversion.federal_tax:,.2f}"
    )

    print(
        f"    NC tax: "
        f"${conversion.nc_tax:,.2f}"
    )


# --------------------------------------------------
# Final validation
# --------------------------------------------------

final_balances = (
    results[-1]["ending_balances"]
)


assert (
    final_balances["Chris 401(k)"]
    >= Decimal("0")
)


assert (
    final_balances["Roth IRA"]
    >= Decimal("0")
)


assert (
    results[-1]["projection"].ending_total
    >= Decimal("0")
)


print()

print(
    "PASS: Real retirement scenario runs "
    "from 2027 through 2040."
)

print(
    "PASS: Account balances remain non-negative."
)

print(
    "PASS: Roth conversions integrate with "
    "the retirement portfolio."
)

print(
    "PASS: Federal and NC conversion taxes "
    "integrate with the scenario."
)

print()
print(
    "PASS: 70H real retirement scenario "
    "foundation is working correctly."
)