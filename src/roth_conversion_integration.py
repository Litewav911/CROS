from decimal import Decimal
from dataclasses import dataclass

from tax_engine import (
    calculate_federal_incremental_tax_mfj_2026,
    calculate_federal_tax_with_social_security_mfj_2026,
    calculate_social_security_taxable_benefit_mfj,
)


# North Carolina 2026 flat income-tax rate.
#
# The current model uses this rate for the
# incremental tax created by a Roth conversion.
NC_2026_RATE = Decimal("0.0399")


@dataclass
class RothConversionIntegration:
    year: int
    source_account: str
    destination_account: str
    base_taxable_income: Decimal
    conversion_amount: Decimal
    federal_tax: Decimal
    nc_tax: Decimal
    total_tax: Decimal
    net_roth_amount: Decimal
    effective_tax_rate: Decimal


def calculate_roth_conversion(
    year: int,
    source_account: str,
    destination_account: str,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    social_security_benefits: Decimal = Decimal("0"),
    provisional_other_income: Decimal | None = None,
):
    """
    Calculate the tax consequences of a Roth conversion.

    The conversion amount is the gross amount moved from
    the traditional account to the Roth account.

    Taxes are calculated separately and are NOT deducted
    from the portfolio projection.

    Returns:
        RothConversionIntegration
    """

    base_taxable_income = Decimal(
        str(base_taxable_income)
    )

    conversion_amount = Decimal(
        str(conversion_amount)
    )

    social_security_benefits = Decimal(
        str(social_security_benefits)
    )

    if provisional_other_income is None:
        provisional_other_income = base_taxable_income
    else:
        provisional_other_income = Decimal(
            str(provisional_other_income)
        )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if conversion_amount < 0:
        raise ValueError(
            "Conversion amount cannot be negative."
        )

    # --------------------------------------------------
    # Federal incremental tax
    # --------------------------------------------------

    taxable_social_security_before = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits,
            provisional_other_income,
        )
    )

    taxable_social_security_after = (
        calculate_social_security_taxable_benefit_mfj(
            social_security_benefits,
            provisional_other_income + conversion_amount,
        )
    )

    if (
        taxable_social_security_before
        == taxable_social_security_after
    ):

        federal_tax = calculate_federal_incremental_tax_mfj_2026(
            base_taxable_income
            + taxable_social_security_before,
            conversion_amount,
        )

    else:

        federal_tax = (
            calculate_federal_tax_with_social_security_mfj_2026(
                base_taxable_income
                + conversion_amount,
                social_security_benefits,
                provisional_other_income + conversion_amount,
            )
            - calculate_federal_tax_with_social_security_mfj_2026(
                base_taxable_income,
                social_security_benefits,
                provisional_other_income,
            )
        )

    # --------------------------------------------------
    # North Carolina incremental tax
    #
    # NC is modeled as a flat rate, so the incremental
    # tax created by the conversion is the conversion
    # amount multiplied by the NC rate.
    # --------------------------------------------------

    nc_tax = (
        conversion_amount
        * NC_2026_RATE
    )

    # --------------------------------------------------
    # Total conversion tax
    # --------------------------------------------------

    total_tax = (
        federal_tax
        + nc_tax
    )

    # --------------------------------------------------
    # Amount remaining after conversion tax
    #
    # This is informational. The portfolio engine still
    # transfers the full gross conversion amount.
    # --------------------------------------------------

    net_roth_amount = (
        conversion_amount
        - total_tax
    )

    # --------------------------------------------------
    # Effective tax rate
    # --------------------------------------------------

    if conversion_amount > 0:

        effective_tax_rate = (
            total_tax
            / conversion_amount
        )

    else:

        effective_tax_rate = Decimal("0")

    return RothConversionIntegration(
        year=year,
        source_account=source_account,
        destination_account=destination_account,
        base_taxable_income=base_taxable_income,
        conversion_amount=conversion_amount,
        federal_tax=federal_tax,
        nc_tax=nc_tax,
        total_tax=total_tax,
        net_roth_amount=net_roth_amount,
        effective_tax_rate=effective_tax_rate,
    )
