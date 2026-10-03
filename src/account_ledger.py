from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class AccountLedgerEntry:
    """
    Represents one balance-changing event
    affecting a retirement account.
    """

    account_name: str
    entry_date: date
    entry_type: str
    amount: Decimal
    description: str
    reference: Optional[str] = None


LEDGER_ENTRIES = []


VALID_ENTRY_TYPES = {
    "starting_balance",
    "contribution",
    "investment_gain",
    "investment_loss",
    "withdrawal",
    "roth_conversion_out",
    "roth_conversion_in",
    "fee",
}


def add_entry(
    account_name: str,
    entry_date: date,
    entry_type: str,
    amount: Decimal,
    description: str,
    reference: Optional[str] = None,
):
    """
    Add a balance-changing ledger entry.

    Amounts are always stored as positive values.
    The entry type determines whether the amount
    increases or decreases the account.
    """

    if entry_type not in VALID_ENTRY_TYPES:
        raise ValueError(
            f"Invalid ledger entry type: "
            f"{entry_type}"
        )

    amount = Decimal(str(amount))

    if amount < 0:
        raise ValueError(
            "Ledger amounts must be positive. "
            "Use the entry type to indicate direction."
        )

    entry = AccountLedgerEntry(
        account_name=account_name,
        entry_date=entry_date,
        entry_type=entry_type,
        amount=amount,
        description=description,
        reference=reference,
    )

    LEDGER_ENTRIES.append(entry)

    return entry


def entry_effect(entry: AccountLedgerEntry) -> Decimal:
    """
    Return the balance effect of a ledger entry.
    """

    if entry.entry_type in {
        "starting_balance",
        "contribution",
        "investment_gain",
        "roth_conversion_in",
    }:
        return entry.amount

    if entry.entry_type in {
        "investment_loss",
        "withdrawal",
        "roth_conversion_out",
        "fee",
    }:
        return -entry.amount

    raise ValueError(
        f"Unknown ledger entry type: "
        f"{entry.entry_type}"
    )


def calculate_balance(
    account_name: str,
) -> Decimal:
    """
    Calculate the balance represented by
    all ledger entries for an account.
    """

    balance = Decimal("0")

    for entry in LEDGER_ENTRIES:

        if entry.account_name != account_name:
            continue

        balance += entry_effect(entry)

    return balance


def get_account_entries(
    account_name: str,
):
    """
    Return all ledger entries for an account.
    """

    return [
        entry
        for entry in LEDGER_ENTRIES
        if entry.account_name == account_name
    ]