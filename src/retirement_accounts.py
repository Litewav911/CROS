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

    subject_to_rmd: bool = False
    intended_use: str = "general"
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
        subject_to_rmd=True,

        intended_use="primary_early_retirement_withdrawal",

        notes=(
            "Primary early-retirement withdrawal account. "
            "Rule of 55 strategy."
        ),
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
        subject_to_rmd=True,

        intended_use="preserve_and_convert",

        notes=(
            "Continue growing while Stephanie works. "
            "Planned future Roth conversion source."
        ),
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
        subject_to_rmd=False,

        intended_use="taxable_retirement_spending",

        notes=(
            "Balance will be populated from actual "
            "account data."
        ),
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
        subject_to_rmd=False,

        intended_use="long_term_tax_free_reserve",

        notes=(
            "Preserve when possible for tax-free growth "
            "and future flexibility."
        ),
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
        subject_to_rmd=False,

        intended_use="healthcare",

        notes=(
            "Primarily intended for qualified healthcare "
            "expenses and long-term tax-advantaged growth."
        ),
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
        subject_to_rmd=False,

        intended_use="market_decline_reserve",

        notes=(
            "Cash/T-bill reserve. Used primarily when "
            "market-decline conditions are triggered."
        ),
    ),
]


def get_account(name: str) -> RetirementAccount:
    """
    Return an account by name.
    """

    for account in RETIREMENT_ACCOUNTS:

        if account.name == name:
            return account

    raise ValueError(
        f"Account not found: {name}"
    )


def total_modeled_assets() -> Decimal:
    """
    Return the total of all currently modeled
    account balances.

    Brokerage and Cash Reserve are currently
    zero until actual balances are entered.
    """

    return sum(
        (
            account.balance
            for account in RETIREMENT_ACCOUNTS
        ),
        Decimal("0"),
    )


def print_accounts():

    print()
    print("CROS RETIREMENT ACCOUNTS")
    print("=" * 85)

    total = Decimal("0")

    for account in RETIREMENT_ACCOUNTS:

        print(
            f"{account.name:25} "
            f"{account.owner:10} "
            f"{account.account_type:12} "
            f"${account.balance:>14,.2f}"
        )

        total += account.balance

    print("-" * 85)

    print(
        f"{'Total modeled assets':25} "
        f"${total:>14,.2f}"
    )


if __name__ == "__main__":
    print_accounts()