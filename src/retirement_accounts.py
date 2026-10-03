from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class RetirementAccount:
    """
    Represents an account used by the retirement plan.
    """

    name: str
    owner: str
    account_type: str
    tax_treatment: str
    balance: Decimal

    withdrawal_allowed: bool = True
    roth_conversion_allowed: bool = False
    rule_of_55_eligible: bool = False

    notes: Optional[str] = None


RETIREMENT_ACCOUNTS = [
    RetirementAccount(
        name="Chris 401(k)",
        owner="Chris",
        account_type="401k",
        tax_treatment="tax_deferred",
        balance=Decimal("752073"),
        withdrawal_allowed=True,
        roth_conversion_allowed=True,
        rule_of_55_eligible=True,
        notes="Primary early-retirement withdrawal account.",
    ),

    RetirementAccount(
        name="Stephanie 401(k)",
        owner="Stephanie",
        account_type="401k",
        tax_treatment="tax_deferred",
        balance=Decimal("414214.61"),
        withdrawal_allowed=True,
        roth_conversion_allowed=True,
        rule_of_55_eligible=False,
        notes="Continue growing while Stephanie works.",
    ),

    RetirementAccount(
        name="Brokerage",
        owner="Joint",
        account_type="brokerage",
        tax_treatment="taxable",
        balance=Decimal("0"),
        withdrawal_allowed=True,
        roth_conversion_allowed=False,
        rule_of_55_eligible=False,
        notes="Balance will be populated from actual account data.",
    ),

    RetirementAccount(
        name="Roth IRA",
        owner="Chris",
        account_type="roth_ira",
        tax_treatment="tax_free",
        balance=Decimal("31387"),
        withdrawal_allowed=True,
        roth_conversion_allowed=False,
        rule_of_55_eligible=False,
        notes="Tax-free retirement account.",
    ),

    RetirementAccount(
        name="HSA",
        owner="Chris",
        account_type="hsa",
        tax_treatment="tax_advantaged",
        balance=Decimal("21464"),
        withdrawal_allowed=True,
        roth_conversion_allowed=False,
        rule_of_55_eligible=False,
        notes="Health savings account.",
    ),

    RetirementAccount(
        name="Cash Reserve",
        owner="Joint",
        account_type="cash",
        tax_treatment="taxable",
        balance=Decimal("0"),
        withdrawal_allowed=True,
        roth_conversion_allowed=False,
        rule_of_55_eligible=False,
        notes="Cash/T-bill reserve.",
    ),
]


def print_accounts():

    print()
    print("CROS RETIREMENT ACCOUNTS")
    print("=" * 70)

    total = Decimal("0")

    for account in RETIREMENT_ACCOUNTS:

        print(
            f"{account.name:25} "
            f"{account.owner:10} "
            f"{account.account_type:12} "
            f"${account.balance:,.2f}"
        )

        total += account.balance

    print("-" * 70)

    print(
        f"{'Total modeled assets':25} "
        f"${total:,.2f}"
    )


if __name__ == "__main__":
    print_accounts()