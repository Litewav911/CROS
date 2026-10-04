from decimal import Decimal, ROUND_HALF_UP

from multi_year_retirement_roth import (
    calculate_multi_year_retirement_roth,
)


print("FULL 2027-2040 RETIREMENT / ROTH PROJECTION TEST")
print("================================================")


START_YEAR = 2027
END_YEAR = 2040
ANNUAL_RETURN = Decimal("0.05")
ANNUAL_CONVERSION = Decimal("80000")
CENT = Decimal("0.01")


def cents(value):
    """
    Normalize a financial value to cents.
    """
    return Decimal(
        str(value)
    ).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def within_one_cent(actual, expected):
    """
    Allow normal financial rounding differences
    of no more than one cent.
    """
    return (
        abs(
            cents(actual)
            - cents(expected)
        )
        <= CENT
    )


BASE_TAXABLE_INCOME = {
    year: Decimal("100000")
    for year in range(
        START_YEAR,
        END_YEAR + 1,
    )
}


ROTH_CONVERSIONS = {
    year: {
        "Chris 401(k)": ANNUAL_CONVERSION
    }
    for year in range(
        START_YEAR,
        END_YEAR + 1,
    )
}


results = calculate_multi_year_retirement_roth(
    start_year=START_YEAR,
    end_year=END_YEAR,
    annual_return=ANNUAL_RETURN,
    base_taxable_income_by_year=BASE_TAXABLE_INCOME,
    roth_conversions_by_year=ROTH_CONVERSIONS,
)


# --------------------------------------------------
# Timeline
# --------------------------------------------------

assert len(results) == 14

assert results[0]["year"] == 2027

assert results[-1]["year"] == 2040


# --------------------------------------------------
# Year-by-year validation
# --------------------------------------------------

previous_ending_total = None

for result in results:

    year = result["year"]

    projection = result["projection"]

    conversion = result["roth_conversion"]

    # --------------------------------------------------
    # Portfolio continuity
    # --------------------------------------------------

    if previous_ending_total is not None:

        assert within_one_cent(
            projection.beginning_total,
            previous_ending_total,
        )

    previous_ending_total = (
        projection.ending_total
    )

    # --------------------------------------------------
    # Portfolio accounting
    #
    # Roth conversions are transfers within the
    # portfolio, so they do not reduce total
    # portfolio value.
    # --------------------------------------------------

    expected_ending = (
        projection.beginning_total
        + projection.investment_gain_total
        - projection.withdrawal_total
    )

    assert within_one_cent(
        projection.ending_total,
        expected_ending,
    )

    # --------------------------------------------------
    # Roth conversion
    # --------------------------------------------------

    if year < 2040:

        assert within_one_cent(
            projection.roth_conversion_total,
            Decimal("80000"),
        )

        assert within_one_cent(
            conversion.conversion_amount,
            Decimal("80000"),
        )

        assert within_one_cent(
            conversion.federal_tax,
            Decimal("17520"),
        )

        assert within_one_cent(
            conversion.nc_tax,
            Decimal("3192"),
        )

    else:

        # --------------------------------------------------
        # 2040
        #
        # Chris 401(k) is nearly depleted. The model
        # correctly converts only the remaining balance.
        # --------------------------------------------------

        assert within_one_cent(
            projection.roth_conversion_total,
            Decimal("1162.54"),
        )

        assert within_one_cent(
            conversion.conversion_amount,
            Decimal("1162.54"),
        )

    # --------------------------------------------------
    # Tax reconciliation
    # --------------------------------------------------

    tax_components = (
        conversion.federal_tax
        + conversion.nc_tax
    )

    assert within_one_cent(
        conversion.total_tax,
        tax_components,
    )

    expected_net_roth = (
        conversion.conversion_amount
        - conversion.total_tax
    )

    assert within_one_cent(
        conversion.net_roth_amount,
        expected_net_roth,
    )


# --------------------------------------------------
# Final balances
# --------------------------------------------------

final_result = results[-1]

final_balances = (
    final_result["ending_balances"]
)


assert within_one_cent(
    final_balances["Chris 401(k)"],
    Decimal("0"),
)


assert within_one_cent(
    final_balances["Roth IRA"],
    Decimal("1551197.21"),
)


assert within_one_cent(
    final_result["projection"].ending_total,
    Decimal("2413811.06"),
)


# --------------------------------------------------
# No negative balances
# --------------------------------------------------

for result in results:

    for account_name, balance in (
        result["ending_balances"].items()
    ):

        assert balance >= Decimal("0"), (
            f"{account_name} became negative "
            f"in {result['year']}"
        )


# --------------------------------------------------
# Output
# --------------------------------------------------

print()

for result in results:

    year = result["year"]

    projection = result["projection"]

    balances = result["ending_balances"]

    conversion = result["roth_conversion"]

    print(
        f"{year}: "
        f"Beginning "
        f"${projection.beginning_total:,.2f} | "
        f"Gain "
        f"${projection.investment_gain_total:,.2f} | "
        f"Withdrawal "
        f"${projection.withdrawal_total:,.2f} | "
        f"Roth "
        f"${projection.roth_conversion_total:,.2f} | "
        f"Ending "
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
        f"    Federal tax: "
        f"${conversion.federal_tax:,.2f} | "
        f"NC tax: "
        f"${conversion.nc_tax:,.2f}"
    )


print()

print(
    "PASS: 2027-2039 Roth conversions "
    "correctly apply $80,000 annually."
)

print(
    "PASS: 2040 Roth conversion is correctly "
    "limited by the remaining Chris 401(k) balance."
)

print(
    "PASS: Chris 401(k) reaches $0 without "
    "becoming negative."
)

print(
    "PASS: Roth IRA receives the conversions "
    "and compounds correctly."
)

print(
    "PASS: Portfolio accounting remains correct "
    "throughout 2027-2040."
)

print(
    "PASS: Federal and NC taxes reconcile to "
    "the total conversion tax."
)

print(
    "PASS: Net Roth amount reconciles correctly."
)

print(
    "PASS: No retirement account becomes negative."
)

print()

print(
    "PASS: Full 2027-2040 retirement / Roth "
    "projection is working correctly."
)