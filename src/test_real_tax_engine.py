from decimal import Decimal

from tax_engine import (
    FEDERAL_MFJ_2026_BRACKETS,
    FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    NC_MFJ_STANDARD_DEDUCTION,
    NC_TAX_RATE,
    TaxBracket,
    calculate_conversion_tax_mfj_2026,
    calculate_federal_incremental_tax_mfj_2026,
    calculate_federal_tax_mfj_2026,
    calculate_federal_tax_with_preferential_income_mfj_2026,
    calculate_flat_tax,
    calculate_incremental_tax,
    calculate_nc_incremental_tax,
    calculate_progressive_tax,
    calculate_taxable_income,
)


# ============================================================
# CROS REAL TAX ENGINE TESTS
# ============================================================


def test_progressive_tax_zero_income():

    result = calculate_progressive_tax(
        Decimal("0"),
        FEDERAL_MFJ_2026_BRACKETS,
    )

    assert result == Decimal("0")


def test_progressive_tax_negative_income_is_zero():

    result = calculate_progressive_tax(
        Decimal("-1000"),
        FEDERAL_MFJ_2026_BRACKETS,
    )

    assert result == Decimal("0")


def test_progressive_tax_first_bracket():

    result = calculate_progressive_tax(
        Decimal("10000"),
        [
            TaxBracket(
                Decimal("24800"),
                Decimal("0.10"),
            ),
            TaxBracket(
                Decimal("100800"),
                Decimal("0.12"),
            ),
        ],
    )

    assert result == Decimal("1000.00")


def test_progressive_tax_crosses_multiple_brackets():

    result = calculate_progressive_tax(
        Decimal("100000"),
        FEDERAL_MFJ_2026_BRACKETS,
    )

    expected = (
        Decimal("24800") * Decimal("0.10")
        + (
            Decimal("100000")
            - Decimal("24800")
        ) * Decimal("0.12")
    )

    assert result == expected


def test_qualified_dividends_and_long_term_gains_use_preferential_rates():
    tax = calculate_federal_tax_with_preferential_income_mfj_2026(
        taxable_income=Decimal("100000"),
        preferential_income=Decimal("20000"),
    )

    assert tax == Decimal("9269.00")
    assert tax < calculate_federal_tax_mfj_2026(Decimal("100000"))


def test_flat_tax():

    result = calculate_flat_tax(
        Decimal("100000"),
        Decimal("0.0399"),
    )

    assert result == Decimal("3990.0000")


def test_flat_tax_negative_income_is_zero():

    result = calculate_flat_tax(
        Decimal("-1000"),
        NC_TAX_RATE,
    )

    assert result == Decimal("0")


def test_taxable_income_applies_standard_deduction():

    result = calculate_taxable_income(
        Decimal("100000"),
        FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    )

    assert result == Decimal("67800")


def test_taxable_income_cannot_be_negative():

    result = calculate_taxable_income(
        Decimal("20000"),
        FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    )

    assert result == Decimal("0")


def test_taxable_income_rejects_negative_gross_income():

    try:
        calculate_taxable_income(
            Decimal("-1"),
            FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
        )

    except ValueError as exc:

        assert str(exc) == (
            "Gross income cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError for negative gross income."
        )


def test_taxable_income_rejects_negative_standard_deduction():

    try:
        calculate_taxable_income(
            Decimal("100000"),
            Decimal("-1"),
        )

    except ValueError as exc:

        assert str(exc) == (
            "Standard deduction cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError for negative standard deduction."
        )


def test_federal_tax_uses_2026_mfj_brackets():

    taxable_income = Decimal("67800")

    result = calculate_federal_tax_mfj_2026(
        taxable_income
    )

    expected = (
        Decimal("24800") * Decimal("0.10")
        + (
            Decimal("67800")
            - Decimal("24800")
        ) * Decimal("0.12")
    )

    assert result == expected


def test_incremental_tax_equals_tax_difference():

    base_income = Decimal("67800")
    conversion = Decimal("80000")

    base_tax = calculate_progressive_tax(
        base_income,
        FEDERAL_MFJ_2026_BRACKETS,
    )

    combined_tax = calculate_progressive_tax(
        base_income + conversion,
        FEDERAL_MFJ_2026_BRACKETS,
    )

    incremental_tax = calculate_incremental_tax(
        base_income,
        conversion,
        FEDERAL_MFJ_2026_BRACKETS,
    )

    assert incremental_tax == (
        combined_tax - base_tax
    )


def test_federal_incremental_tax_for_eighty_thousand_conversion():

    base_taxable_income = Decimal("67800")
    conversion_amount = Decimal("80000")

    result = (
        calculate_federal_incremental_tax_mfj_2026(
            base_taxable_income,
            conversion_amount,
        )
    )

    expected = (
        calculate_federal_tax_mfj_2026(
            base_taxable_income
            + conversion_amount
        )
        - calculate_federal_tax_mfj_2026(
            base_taxable_income
        )
    )

    assert result == expected


def test_nc_incremental_tax_for_eighty_thousand_conversion():

    base_taxable_income = Decimal("74500")
    conversion_amount = Decimal("80000")

    result = calculate_nc_incremental_tax(
        base_taxable_income,
        conversion_amount,
    )

    expected = (
        conversion_amount
        * NC_TAX_RATE
    )

    assert result == expected


def test_conversion_tax_combines_federal_and_nc_tax():

    base_taxable_income = Decimal("67800")
    conversion_amount = Decimal("80000")

    result = calculate_conversion_tax_mfj_2026(
        base_taxable_income,
        conversion_amount,
    )

    federal_tax = (
        calculate_federal_incremental_tax_mfj_2026(
            base_taxable_income,
            conversion_amount,
        )
    )

    nc_tax = calculate_nc_incremental_tax(
        base_taxable_income,
        conversion_amount,
    )

    assert result.taxable_income == (
        base_taxable_income
        + conversion_amount
    )

    assert result.tax == (
        federal_tax
        + nc_tax
    )


def test_conversion_tax_is_zero_when_conversion_is_zero():

    result = calculate_conversion_tax_mfj_2026(
        Decimal("67800"),
        Decimal("0"),
    )

    assert result.tax == Decimal("0")


def test_incremental_tax_rejects_negative_base_income():

    try:
        calculate_incremental_tax(
            Decimal("-1"),
            Decimal("80000"),
            FEDERAL_MFJ_2026_BRACKETS,
        )

    except ValueError as exc:

        assert str(exc) == (
            "Base taxable income cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError for negative base income."
        )


def test_incremental_tax_rejects_negative_conversion():

    try:
        calculate_incremental_tax(
            Decimal("67800"),
            Decimal("-1"),
            FEDERAL_MFJ_2026_BRACKETS,
        )

    except ValueError as exc:

        assert str(exc) == (
            "Additional income cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError for negative conversion."
        )


def test_real_retirement_tax_scenario():

    gross_income = Decimal("100000")

    federal_taxable_income = (
        calculate_taxable_income(
            gross_income,
            FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
        )
    )

    nc_taxable_income = (
        calculate_taxable_income(
            gross_income,
            NC_MFJ_STANDARD_DEDUCTION,
        )
    )

    conversion_amount = Decimal("80000")

    federal_conversion_tax = (
        calculate_federal_incremental_tax_mfj_2026(
            federal_taxable_income,
            conversion_amount,
        )
    )

    nc_conversion_tax = (
        calculate_nc_incremental_tax(
            nc_taxable_income,
            conversion_amount,
        )
    )

    total_conversion_tax = (
        federal_conversion_tax
        + nc_conversion_tax
    )

    result = calculate_conversion_tax_mfj_2026(
        federal_taxable_income,
        conversion_amount,
    )

    assert federal_taxable_income == (
        Decimal("67800")
    )

    assert nc_taxable_income == (
        Decimal("74500")
    )

    assert federal_conversion_tax > Decimal("0")

    assert nc_conversion_tax == (
        Decimal("3192.0000")
    )

    assert total_conversion_tax == (
        result.tax
    )


def test_tax_engine_handles_decimal_string_inputs():

    result = calculate_flat_tax(
        "100000",
        "0.0399",
    )

    assert result == Decimal("3990.0000")


def test_conversion_tax_increases_when_conversion_increases():

    base_income = Decimal("67800")

    tax_40000 = calculate_conversion_tax_mfj_2026(
        base_income,
        Decimal("40000"),
    ).tax

    tax_80000 = calculate_conversion_tax_mfj_2026(
        base_income,
        Decimal("80000"),
    ).tax

    assert tax_80000 > tax_40000


def test_conversion_tax_is_progressive():

    base_income = Decimal("67800")

    first_conversion = Decimal("40000")
    second_conversion = Decimal("40000")

    first_tax = calculate_conversion_tax_mfj_2026(
        base_income,
        first_conversion,
    ).tax

    combined_tax = calculate_conversion_tax_mfj_2026(
        base_income,
        first_conversion + second_conversion,
    ).tax

    second_incremental_tax = (
        combined_tax
        - first_tax
    )

    assert second_incremental_tax > Decimal("0")
