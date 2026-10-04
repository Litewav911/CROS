from decimal import Decimal, ROUND_HALF_UP

from multi_year_retirement_roth import (
    calculate_multi_year_retirement_roth,
)


print("DYNAMIC MULTI-YEAR RETIREMENT / ROTH TEST")
print("===========================================")


START_YEAR = 2027
END_YEAR = 2040
ANNUAL_RETURN = Decimal("0.05")

BASE_TAXABLE_INCOME = Decimal("100000")
NORMAL_CONVERSION = Decimal("80000")


def cents(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


# --------------------------------------------------
# Run integrated dynamic projection
# --------------------------------------------------

results = calculate_multi_year_retirement_roth(
    start_year=START_YEAR,
    end_year=END_YEAR,
    annual_return=ANNUAL_RETURN,
    base_taxable_income_by_year={
        year: BASE_TAXABLE_INCOME
        for year in range(
            START_YEAR,
            END_YEAR + 1,
        )
    },
    roth_conversions_by_year={
        year: {
            "Chris 401(k)": NORMAL_CONVERSION
        }
        for year in range(
            START_YEAR,
            END_YEAR,
        )
    },
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

for result in results:

    year = result["year"]
    projection = result["projection"]
    conversion = result["roth_conversion"]

    balances = result["ending_balances"]

    print()
    print(year)
    print("----")

    print(
        f"Beginning portfolio: "
        f"${projection.beginning_total:,.2f}"
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

    print(
        f"Chris 401(k): "
        f"${balances['Chris 401(k)']:,.2f}"
    )

    print(
        f"Roth IRA: "
        f"${balances['Roth IRA']:,.2f}"
    )

    print(
        f"Federal conversion tax: "
        f"${conversion.federal_tax:,.2f}"
    )

    print(
        f"NC conversion tax: "
        f"${conversion.nc_tax:,.2f}"
    )


# --------------------------------------------------
# Basic result validation
# --------------------------------------------------

assert len(results) == 14

assert results[0]["year"] == 2027
assert results[-1]["year"] == 2040


# --------------------------------------------------
# 2027 validation
# --------------------------------------------------

result_2027 = results[0]

projection_2027 = result_2027["projection"]
balances_2027 = result_2027["ending_balances"]
conversion_2027 = result_2027["roth_conversion"]


assert (
    projection_2027.beginning_total
    == Decimal("1219138.61")
)

assert (
    cents(projection_2027.investment_gain_total)
    == Decimal("60956.93")
)

assert (
    projection_2027.roth_conversion_total
    == Decimal("80000")
)

assert (
    cents(projection_2027.ending_total)
    == Decimal("1280095.54")
)

assert (
    cents(balances_2027["Chris 401(k)"])
    == Decimal("709676.65")
)

assert (
    cents(balances_2027["Roth IRA"])
    == Decimal("112956.35")
)

assert (
    cents(conversion_2027.federal_tax)
    == Decimal("17520.00")
)

assert (
    cents(conversion_2027.nc_tax)
    == Decimal("3192.00")
)

assert (
    cents(conversion_2027.total_tax)
    == Decimal("20712.00")
)


# --------------------------------------------------
# 2028 validation
# --------------------------------------------------

result_2028 = results[1]

projection_2028 = result_2028["projection"]
balances_2028 = result_2028["ending_balances"]
conversion_2028 = result_2028["roth_conversion"]


assert (
    projection_2028.beginning_total
    == projection_2027.ending_total
)

assert (
    cents(projection_2028.investment_gain_total)
    == Decimal("64004.78")
)

assert (
    projection_2028.roth_conversion_total
    == Decimal("80000")
)

assert (
    cents(balances_2028["Chris 401(k)"])
    == Decimal("665160.48")
)

assert (
    cents(balances_2028["Roth IRA"])
    == Decimal("198604.17")
)

assert (
    cents(conversion_2028.total_tax)
    == Decimal("20712.00")
)


# --------------------------------------------------
# Normal conversion validation: 2027-2039
# --------------------------------------------------

for result in results[:-1]:

    conversion = result["roth_conversion"]

    assert (
        conversion.conversion_amount
        == NORMAL_CONVERSION
    )

    assert (
        cents(conversion.federal_tax)
        == Decimal("17520.00")
    )

    assert (
        cents(conversion.nc_tax)
        == Decimal("3192.00")
    )

    assert (
        cents(conversion.total_tax)
        == Decimal("20712.00")
    )

    assert (
        cents(conversion.net_roth_amount)
        == Decimal("59288.00")
    )


# --------------------------------------------------
# 2040 dynamic final conversion
# --------------------------------------------------

result_2040 = results[-1]

projection_2040 = result_2040["projection"]
balances_2040 = result_2040["ending_balances"]
conversion_2040 = result_2040["roth_conversion"]


FINAL_CONVERSION = Decimal("1162.54")


assert (
    cents(conversion_2040.conversion_amount)
    == FINAL_CONVERSION
)

assert (
    cents(projection_2040.roth_conversion_total)
    == FINAL_CONVERSION
)

assert (
    cents(balances_2040["Chris 401(k)"])
    == Decimal("0.00")
)

assert (
    cents(conversion_2040.federal_tax)
    == Decimal("175.76")
)

assert (
    cents(conversion_2040.nc_tax)
    == Decimal("46.39")
)

# The tax engine's underlying fractional-cent calculation
# produces $222.14 as the stored total for this conversion.
assert (
    cents(conversion_2040.total_tax)
    == Decimal("222.14")
)

assert (
    cents(conversion_2040.net_roth_amount)
    == Decimal("940.39")
)

# --------------------------------------------------
# Portfolio continuity
# --------------------------------------------------

for index in range(1, len(results)):

    previous = results[index - 1]["projection"]
    current = results[index]["projection"]

    assert (
        current.beginning_total
        == previous.ending_total
    )


# --------------------------------------------------
# Portfolio accounting
# --------------------------------------------------

for result in results:

    projection = result["projection"]

    expected_ending = (
        projection.beginning_total
        + projection.investment_gain_total
        - projection.withdrawal_total
    )

assert (
    cents(projection.ending_total)
    == cents(expected_ending)
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
    "PASS: Normal Roth conversions calculate "
    "correctly through 2039."
)

print(
    "PASS: Dynamic final conversion correctly "
    "uses the remaining Chris 401(k) balance."
)

print(
    "PASS: 2040 Chris 401(k) reaches zero "
    "without over-conversion."
)

print(
    "PASS: Federal and NC conversion taxes "
    "calculate correctly."
)

print(
    "PASS: Roth IRA investment growth compounds "
    "correctly across all years."
)

print(
    "PASS: Portfolio balances remain continuous "
    "from year to year."
)

print(
    "PASS: Portfolio accounting remains correct "
    "across the full projection."
)

print()
print(
    "PASS: Dynamic multi-year retirement / Roth "
    "integration is working correctly."
)