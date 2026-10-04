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


# ============================================================
# NORTH CAROLINA
# ============================================================

NC_MFJ_STANDARD_DEDUCTION = Decimal(
    "25500"
)

NC_TAX_RATE = Decimal(
    "0.0399"
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
    conversion_amount: Decimal,
    brackets: List[TaxBracket],
) -> Decimal:
    """
    Calculate the additional tax created by a
    Roth conversion.

    Tax(base income + conversion)
    minus
    Tax(base income)
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

    base_tax = calculate_progressive_tax(
        base_taxable_income,
        brackets,
    )

    converted_tax = calculate_progressive_tax(
        base_taxable_income
        + conversion_amount,
        brackets,
    )

    return (
        converted_tax
        - base_tax
    )


def calculate_nc_incremental_tax(
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
) -> Decimal:
    """
    Calculate incremental North Carolina tax
    caused by a Roth conversion.
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    conversion_amount = Decimal(
        str(conversion_amount)
    )

    base_tax = calculate_flat_tax(
        base_taxable_income,
        NC_TAX_RATE,
    )

    converted_tax = calculate_flat_tax(
        base_taxable_income
        + conversion_amount,
        NC_TAX_RATE,
    )

    return (
        converted_tax
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
    conversion_amount: Decimal,
) -> Decimal:
    """
    Calculate the incremental federal tax
    caused by a Roth conversion.
    """

    return calculate_incremental_tax(
        base_taxable_income,
        conversion_amount,
        FEDERAL_MFJ_2026_BRACKETS,
    )


def calculate_conversion_tax_mfj_2026(
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
) -> TaxResult:
    """
    Calculate combined federal and NC
    incremental Roth-conversion tax.
    """

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

    return TaxResult(
        taxable_income=(
            base_taxable_income
            + conversion_amount
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

    nc_conversion_tax = (
        calculate_nc_incremental_tax(
            nc_taxable_income,
            conversion,
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