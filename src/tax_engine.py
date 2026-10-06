from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class TaxBracket:
    """
    Progressive tax bracket.

    upper_limit is the top of the bracket.
    None means unlimited.
    """

    upper_limit: Decimal | None
    rate: Decimal


@dataclass
class TaxResult:
    """
    Result of a tax calculation.
    """

    taxable_income: Decimal
    tax: Decimal


# ============================================================
# 2026 FEDERAL TAX RULES
#
# Married Filing Jointly.
#
# These are the currently published 2026 values.
# 2027 values will be updated when officially published.
# ============================================================

FEDERAL_MFJ_2026_BRACKETS = [
    TaxBracket(
        Decimal("24800"),
        Decimal("0.10"),
    ),
    TaxBracket(
        Decimal("100800"),
        Decimal("0.12"),
    ),
    TaxBracket(
        Decimal("211400"),
        Decimal("0.22"),
    ),
    TaxBracket(
        Decimal("403550"),
        Decimal("0.24"),
    ),
    TaxBracket(
        Decimal("512450"),
        Decimal("0.32"),
    ),
    TaxBracket(
        Decimal("768700"),
        Decimal("0.35"),
    ),
    TaxBracket(
        None,
        Decimal("0.37"),
    ),
]


FEDERAL_STANDARD_DEDUCTION_MFJ_2026 = Decimal(
    "32200"
)

FEDERAL_MFJ_2026_CAPITAL_GAINS_ZERO_RATE_LIMIT = Decimal(
    "98900"
)

FEDERAL_MFJ_2026_CAPITAL_GAINS_15_RATE_LIMIT = Decimal(
    "613700"
)


# ============================================================
# NORTH CAROLINA
# ============================================================

NC_MFJ_STANDARD_DEDUCTION = Decimal(
    "25500"
)

NC_TAX_RATE = Decimal(
    "0.0399"
)


# ============================================================
# SOCIAL SECURITY
#
# Married Filing Jointly.
#
# Provisional income:
#
#     other income
#     + 50% of Social Security benefits
#
# First threshold:
#     $32,000
#
# Second threshold:
#     $44,000
#
# Maximum taxable Social Security:
#     85% of benefits
# ============================================================

SOCIAL_SECURITY_MFJ_FIRST_THRESHOLD = Decimal(
    "32000"
)

SOCIAL_SECURITY_MFJ_SECOND_THRESHOLD = Decimal(
    "44000"
)

SOCIAL_SECURITY_TAXABLE_RATE_FIRST_TIER = Decimal(
    "0.50"
)

SOCIAL_SECURITY_TAXABLE_RATE_SECOND_TIER = Decimal(
    "0.85"
)


def calculate_progressive_tax(
    taxable_income: Decimal,
    brackets: List[TaxBracket],
) -> Decimal:
    """
    Calculate progressive income tax.
    """

    taxable_income = Decimal(
        str(taxable_income)
    )

    if taxable_income <= 0:
        return Decimal("0")

    tax = Decimal("0")
    lower_limit = Decimal("0")

    for bracket in brackets:

        if bracket.upper_limit is None:

            amount_in_bracket = (
                taxable_income
                - lower_limit
            )

        else:

            amount_in_bracket = (
                min(
                    taxable_income,
                    bracket.upper_limit,
                )
                - lower_limit
            )

        if amount_in_bracket > 0:

            tax += (
                amount_in_bracket
                * bracket.rate
            )

        if (
            bracket.upper_limit is not None
            and taxable_income
            <= bracket.upper_limit
        ):
            break

        if bracket.upper_limit is not None:

            lower_limit = (
                bracket.upper_limit
            )

    return tax


def calculate_flat_tax(
    taxable_income: Decimal,
    rate: Decimal,
) -> Decimal:
    """
    Calculate a flat-rate tax.
    """

    taxable_income = Decimal(
        str(taxable_income)
    )

    rate = Decimal(
        str(rate)
    )

    if taxable_income <= 0:
        return Decimal("0")

    return (
        taxable_income
        * rate
    )


def calculate_incremental_tax(
    base_taxable_income: Decimal,
    additional_income: Decimal,
    brackets: List[TaxBracket],
) -> Decimal:
    """
    Calculate the additional tax caused by
    additional taxable income.

    Tax(base income + additional income)
    minus
    Tax(base income)
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    additional_income = Decimal(
        str(additional_income)
    )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if additional_income < 0:
        raise ValueError(
            "Additional income cannot be negative."
        )

    base_tax = calculate_progressive_tax(
        base_taxable_income,
        brackets,
    )

    combined_tax = calculate_progressive_tax(
        base_taxable_income
        + additional_income,
        brackets,
    )

    return (
        combined_tax
        - base_tax
    )


def calculate_nc_incremental_tax(
    base_taxable_income: Decimal,
    additional_income: Decimal,
) -> Decimal:
    """
    Calculate incremental North Carolina tax
    caused by additional taxable income.
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    additional_income = Decimal(
        str(additional_income)
    )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if additional_income < 0:
        raise ValueError(
            "Additional income cannot be negative."
        )

    base_tax = calculate_flat_tax(
        base_taxable_income,
        NC_TAX_RATE,
    )

    combined_tax = calculate_flat_tax(
        base_taxable_income
        + additional_income,
        NC_TAX_RATE,
    )

    return (
        combined_tax
        - base_tax
    )


def calculate_taxable_income(
    gross_income: Decimal,
    standard_deduction: Decimal,
) -> Decimal:
    """
    Calculate taxable income after the
    supplied standard deduction.
    """

    gross_income = Decimal(
        str(gross_income)
    )

    standard_deduction = Decimal(
        str(standard_deduction)
    )

    if gross_income < 0:
        raise ValueError(
            "Gross income cannot be negative."
        )

    if standard_deduction < 0:
        raise ValueError(
            "Standard deduction cannot be negative."
        )

    return max(
        Decimal("0"),
        gross_income
        - standard_deduction,
    )


def calculate_federal_tax_mfj_2026(
    taxable_income: Decimal,
) -> Decimal:
    """
    Calculate federal income tax using the
    currently published 2026 MFJ brackets.
    """

    return calculate_progressive_tax(
        taxable_income,
        FEDERAL_MFJ_2026_BRACKETS,
    )


def calculate_federal_incremental_tax_mfj_2026(
    base_taxable_income: Decimal,
    additional_income: Decimal,
) -> Decimal:
    """
    Calculate incremental federal tax caused by
    additional taxable income.
    """

    return calculate_incremental_tax(
        base_taxable_income,
        additional_income,
        FEDERAL_MFJ_2026_BRACKETS,
    )


def calculate_social_security_taxable_benefit_mfj(
    social_security_benefits: Decimal,
    other_income: Decimal,
) -> Decimal:
    """
    Calculate the taxable portion of Social Security
    benefits for Married Filing Jointly.

    Provisional income is:

        other income
        + 50% of Social Security benefits

    Taxable Social Security is calculated using the
    standard MFJ $32,000 / $44,000 thresholds and
    cannot exceed 85% of total benefits.
    """

    social_security_benefits = Decimal(
        str(social_security_benefits)
    )

    other_income = Decimal(
        str(other_income)
    )

    if social_security_benefits < 0:
        raise ValueError(
            "Social Security benefits cannot be negative."
        )

    if other_income < 0:
        raise ValueError(
            "Other income cannot be negative."
        )

    if social_security_benefits == 0:
        return Decimal("0")

    provisional_income = (
        other_income
        + (
            social_security_benefits
            * Decimal("0.50")
        )
    )

    if (
        provisional_income
        <= SOCIAL_SECURITY_MFJ_FIRST_THRESHOLD
    ):
        return Decimal("0")

    first_tier_income = min(
        provisional_income
        - SOCIAL_SECURITY_MFJ_FIRST_THRESHOLD,
        SOCIAL_SECURITY_MFJ_SECOND_THRESHOLD
        - SOCIAL_SECURITY_MFJ_FIRST_THRESHOLD,
    )

    taxable = (
        min(
            social_security_benefits
            * SOCIAL_SECURITY_TAXABLE_RATE_FIRST_TIER,
            first_tier_income
            * SOCIAL_SECURITY_TAXABLE_RATE_FIRST_TIER,
        )
    )

    if (
        provisional_income
        > SOCIAL_SECURITY_MFJ_SECOND_THRESHOLD
    ):

        second_tier_income = (
            provisional_income
            - SOCIAL_SECURITY_MFJ_SECOND_THRESHOLD
        )

        taxable += (
            second_tier_income
            * SOCIAL_SECURITY_TAXABLE_RATE_SECOND_TIER
        )

    maximum_taxable = (
        social_security_benefits
        * SOCIAL_SECURITY_TAXABLE_RATE_SECOND_TIER
    )

    return min(
        taxable,
        maximum_taxable,
    ).quantize(
        Decimal("0.01")
    )


def calculate_federal_tax_with_social_security_mfj_2026(
    other_income: Decimal,
    social_security_benefits: Decimal,
    provisional_other_income: Decimal | None = None,
) -> Decimal:
    """Calculate federal tax including taxable Social Security."""

    return calculate_federal_tax_with_preferential_income_mfj_2026(
        taxable_income=other_income,
        preferential_income=Decimal("0"),
        social_security_benefits=social_security_benefits,
        provisional_other_income=provisional_other_income,
    )


def calculate_federal_tax_with_preferential_income_mfj_2026(
    taxable_income: Decimal,
    preferential_income: Decimal,
    social_security_benefits: Decimal = Decimal("0"),
    provisional_other_income: Decimal | None = None,
) -> Decimal:
    """Calculate tax on ordinary and qualified dividend/long-term gain income.

    ``taxable_income`` is total taxable income before taxable Social
    Security. ``preferential_income`` is the gross amount eligible for
    long-term capital-gain rates; it is capped at total taxable income.
    """

    taxable_income = Decimal(str(taxable_income))
    preferential_income = Decimal(str(preferential_income))

    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative.")
    if preferential_income < 0:
        raise ValueError("Preferential income cannot be negative.")

    if provisional_other_income is None:
        provisional_other_income = taxable_income
    else:
        provisional_other_income = Decimal(
            str(provisional_other_income)
        )

    taxable_social_security = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits,
            provisional_other_income,
        )
    )

    taxable_income_with_benefits = (
        taxable_income + taxable_social_security
    )
    taxable_preferential_income = min(
        preferential_income,
        taxable_income_with_benefits,
    )
    ordinary_taxable_income = (
        taxable_income_with_benefits
        - taxable_preferential_income
    )

    zero_rate_income = min(
        taxable_preferential_income,
        max(
            Decimal("0"),
            FEDERAL_MFJ_2026_CAPITAL_GAINS_ZERO_RATE_LIMIT
            - ordinary_taxable_income,
        ),
    )
    remaining_preferential_income = (
        taxable_preferential_income - zero_rate_income
    )
    fifteen_rate_income = min(
        remaining_preferential_income,
        max(
            Decimal("0"),
            FEDERAL_MFJ_2026_CAPITAL_GAINS_15_RATE_LIMIT
            - max(
                ordinary_taxable_income,
                FEDERAL_MFJ_2026_CAPITAL_GAINS_ZERO_RATE_LIMIT,
            ),
        ),
    )
    twenty_rate_income = (
        remaining_preferential_income - fifteen_rate_income
    )

    preferential_tax = (
        fifteen_rate_income * Decimal("0.15")
        + twenty_rate_income * Decimal("0.20")
    )
    ordinary_tax = calculate_federal_tax_mfj_2026(
        ordinary_taxable_income
    )

    return ordinary_tax + preferential_tax


def calculate_withdrawal_tax_mfj_2026(
    base_taxable_income: Decimal,
    conversion_amount: Decimal = Decimal("0"),
    withdrawal_amount: Decimal | None = None,
    social_security_benefits: Decimal = Decimal("0"),
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = Decimal("0"),
) -> Decimal:
    """
    Calculate the combined federal and North Carolina
    incremental tax caused by a traditional tax-deferred
    retirement-account withdrawal.

    When conversion_amount is supplied, the withdrawal
    tax is calculated on top of the Roth conversion so
    that the conversion occupies the appropriate tax
    brackets first.

    Backward compatibility:
        When only two arguments are supplied, the second
        argument is treated as withdrawal_amount.
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    conversion_amount = Decimal(
        str(conversion_amount)
    )

    if withdrawal_amount is None:

        withdrawal_amount = conversion_amount
        conversion_amount = Decimal("0")

    else:

        withdrawal_amount = Decimal(
            str(withdrawal_amount)
        )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if conversion_amount < 0:
        raise ValueError(
            "Conversion amount cannot be negative."
        )

    if withdrawal_amount < 0:
        raise ValueError(
            "Withdrawal amount cannot be negative."
        )

    if withdrawal_amount == 0:
        return Decimal("0")

    if provisional_other_income is None:
        provisional_other_income = base_taxable_income
    else:
        provisional_other_income = Decimal(
            str(provisional_other_income)
        )

    taxable_income_before_withdrawal = (
        base_taxable_income
        + conversion_amount
    )

    federal_tax = (
        calculate_federal_tax_with_preferential_income_mfj_2026(
            taxable_income_before_withdrawal + withdrawal_amount,
            preferential_income,
            social_security_benefits,
            provisional_other_income
            + conversion_amount
            + withdrawal_amount,
        )
        - calculate_federal_tax_with_preferential_income_mfj_2026(
            taxable_income_before_withdrawal,
            preferential_income,
            social_security_benefits,
            provisional_other_income + conversion_amount,
        )
    )

    nc_tax = calculate_nc_incremental_tax(
        base_taxable_income
        + conversion_amount,
        withdrawal_amount,
    )

    return (
        federal_tax
        + nc_tax
    )


def calculate_conversion_tax_mfj_2026(
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    social_security_benefits: Decimal = Decimal("0"),
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = Decimal("0"),
) -> TaxResult:
    """
    Calculate combined federal and NC
    incremental Roth-conversion tax.
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    conversion_amount = Decimal(
        str(conversion_amount)
    )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if conversion_amount < 0:
        raise ValueError(
            "Conversion amount cannot be negative."
        )

    if provisional_other_income is None:
        provisional_other_income = base_taxable_income
    else:
        provisional_other_income = Decimal(
            str(provisional_other_income)
        )

    federal_tax = (
        calculate_federal_tax_with_preferential_income_mfj_2026(
            base_taxable_income + conversion_amount,
            preferential_income,
            social_security_benefits,
            provisional_other_income + conversion_amount,
        )
        - calculate_federal_tax_with_preferential_income_mfj_2026(
            base_taxable_income,
            preferential_income,
            social_security_benefits,
            provisional_other_income,
        )
    )

    nc_tax = calculate_nc_incremental_tax(
        base_taxable_income,
        conversion_amount,
    )

    return TaxResult(
        taxable_income=(
            base_taxable_income
            + conversion_amount
            + calculate_social_security_taxable_benefit_mfj(
                social_security_benefits,
                provisional_other_income
                + conversion_amount,
            )
        ),
        tax=(
            federal_tax
            + nc_tax
        ),
    )


if __name__ == "__main__":

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

    conversion = Decimal("80000")

    federal_conversion_tax = (
        calculate_federal_incremental_tax_mfj_2026(
            federal_taxable_income,
            conversion,
        )
    )

    nc_conversion_tax = calculate_nc_incremental_tax(
        nc_taxable_income,
        conversion,
    )

    withdrawal = Decimal("80000")

    withdrawal_tax = (
        calculate_withdrawal_tax_mfj_2026(
            federal_taxable_income,
            Decimal("0"),
            withdrawal,
        )
    )

    print()
    print("REAL TAX ENGINE")
    print("=" * 65)

    print(
        f"{'Gross income':35}"
        f"${gross_income:,.2f}"
    )

    print(
        f"{'Federal taxable income':35}"
        f"${federal_taxable_income:,.2f}"
    )

    print(
        f"{'NC taxable income':35}"
        f"${nc_taxable_income:,.2f}"
    )

    print(
        f"{'Test Roth conversion':35}"
        f"${conversion:,.2f}"
    )

    print(
        f"{'Federal conversion tax':35}"
        f"${federal_conversion_tax:,.2f}"
    )

    print(
        f"{'NC conversion tax':35}"
        f"${nc_conversion_tax:,.2f}"
    )

    print(
        f"{'Total conversion tax':35}"
        f"${(
            federal_conversion_tax
            + nc_conversion_tax
        ):,.2f}"
    )

    print(
        f"{'Test 401(k) withdrawal':35}"
        f"${withdrawal:,.2f}"
    )

    print(
        f"{'Total withdrawal tax':35}"
        f"${withdrawal_tax:,.2f}"
    )
