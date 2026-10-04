from dataclasses import dataclass
from decimal import Decimal

from tax_engine import (
    calculate_federal_incremental_tax_mfj_2026,
    calculate_nc_incremental_tax,
)


@dataclass
class RothConversion:
    """
    Represents one Roth conversion from a
    tax-deferred retirement account to a Roth account.
    """

    year: int
    source_account: str
    destination_account: str

    base_taxable_income: Decimal
    conversion_amount: Decimal

    federal_tax: Decimal
    nc_tax: Decimal

    @property
    def total_tax(self) -> Decimal:
        return (
            self.federal_tax
            + self.nc_tax
        )

    @property
    def net_roth_amount(self) -> Decimal:
        """
        Informational amount after conversion tax.

        The actual tax payment source is handled
        separately by the retirement plan.
        """

        return max(
            Decimal("0"),
            self.conversion_amount
            - self.total_tax,
        )

    @property
    def effective_tax_rate(self) -> Decimal:
        """
        Effective tax rate attributable to
        this Roth conversion.
        """

        if self.conversion_amount <= 0:
            return Decimal("0")

        return (
            self.total_tax
            / self.conversion_amount
        )


def create_roth_conversion(
    year: int,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    source_account: str = "Chris 401(k)",
    destination_account: str = "Roth IRA",
) -> RothConversion:
    """
    Create a Roth conversion using the real tax engine.

    Current tax rules:
        - Federal MFJ 2026 brackets
        - North Carolina current rate

    The tax-year configuration will be updated when
    official 2027 tax parameters are available.
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

    return RothConversion(
        year=year,
        source_account=source_account,
        destination_account=destination_account,
        base_taxable_income=base_taxable_income,
        conversion_amount=conversion_amount,
        federal_tax=federal_tax,
        nc_tax=nc_tax,
    )


def print_roth_conversion(
    conversion: RothConversion,
):

    print()
    print(
        f"ROTH CONVERSION: "
        f"{conversion.year}"
    )
    print("=" * 65)

    print(
        f"{'Source account':35}"
        f"{conversion.source_account}"
    )

    print(
        f"{'Destination account':35}"
        f"{conversion.destination_account}"
    )

    print(
        f"{'Base taxable income':35}"
        f"${conversion.base_taxable_income:,.2f}"
    )

    print(
        f"{'Conversion amount':35}"
        f"${conversion.conversion_amount:,.2f}"
    )

    print(
        f"{'Federal tax':35}"
        f"${conversion.federal_tax:,.2f}"
    )

    print(
        f"{'NC tax':35}"
        f"${conversion.nc_tax:,.2f}"
    )

    print(
        f"{'Total tax':35}"
        f"${conversion.total_tax:,.2f}"
    )

    print(
        f"{'Net Roth amount':35}"
        f"${conversion.net_roth_amount:,.2f}"
    )

    print(
        f"{'Effective tax rate':35}"
        f"{conversion.effective_tax_rate:.2%}"
    )


if __name__ == "__main__":

    conversion = create_roth_conversion(
        year=2027,
        base_taxable_income=Decimal("67800"),
        conversion_amount=Decimal("80000"),
    )

    print_roth_conversion(
        conversion
    )