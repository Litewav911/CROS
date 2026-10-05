from decimal import Decimal

from tax_engine import (
    calculate_social_security_taxable_benefit_mfj,
)


def test_social_security_below_mfj_threshold_is_not_taxable():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("20000"),
            other_income=Decimal("20000"),
        )
    )

    assert taxable == Decimal("0")


def test_social_security_partially_taxable_for_mfj():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("20000"),
            other_income=Decimal("15000"),
        )
    )

    # Provisional income:
    #
    # 15,000 + 10,000 = 25,000
    #
    # Below $32,000.
    assert taxable == Decimal("0")


def test_social_security_50_percent_tier_for_mfj():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("30000"),
            other_income=Decimal("10000"),
        )
    )

    # Provisional income:
    #
    # 10,000 + 15,000 = 25,000
    #
    # Still below $32,000.
    assert taxable == Decimal("0")


def test_social_security_crosses_first_mfj_threshold():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("30000"),
            other_income=Decimal("20000"),
        )
    )

    # Provisional income:
    #
    # 20,000 + 15,000 = 35,000
    #
    # Taxable:
    #
    # (35,000 - 32,000) * 50%
    # = 1,500
    assert taxable == Decimal("1500.00")


def test_social_security_above_second_mfj_threshold():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("50000"),
            other_income=Decimal("100000"),
        )
    )

    # The 85% cap applies.
    assert taxable == Decimal("42500.00")


def test_social_security_taxable_amount_never_exceeds_85_percent():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("40000"),
            other_income=Decimal("500000"),
        )
    )

    assert taxable == Decimal("34000.00")


def test_zero_social_security_produces_zero_taxable_benefit():

    taxable = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("0"),
            other_income=Decimal("100000"),
        )
    )

    assert taxable == Decimal("0")


def test_negative_social_security_is_rejected():

    try:

        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("-1"),
            other_income=Decimal("100000"),
        )

    except ValueError as exc:

        assert (
            str(exc)
            == "Social Security benefits cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError."
        )


def test_negative_other_income_is_rejected():

    try:

        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits=Decimal("40000"),
            other_income=Decimal("-1"),
        )

    except ValueError as exc:

        assert (
            str(exc)
            == "Other income cannot be negative."
        )

    else:

        raise AssertionError(
            "Expected ValueError."
        )