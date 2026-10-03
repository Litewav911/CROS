from decimal import Decimal

from retirement_accounts import get_account
from account_ledger import (
    get_account_entries,
    entry_effect,
)


def calculate_projected_balance(
    account_name: str,
) -> Decimal:
    """
    Calculate an account's projected balance by
    starting with the modeled account balance and
    applying ledger entries.

    The ledger may contain a starting_balance entry
    for testing or historical reconstruction.

    A starting_balance ledger entry is therefore
    excluded here because the retirement account
    already contains the authoritative starting balance.
    """

    account = get_account(account_name)

    balance = Decimal(str(account.balance))

    for entry in get_account_entries(account_name):

        if entry.entry_type == "starting_balance":
            continue

        balance += entry_effect(entry)

    return balance


def print_account_balance(account_name: str):

    account = get_account(account_name)

    balance = calculate_projected_balance(
        account_name
    )

    print()
    print(
        f"ACCOUNT BALANCE: {account_name}"
    )
    print("=" * 60)

    print(
        f"Modeled starting balance"
        f"      ${account.balance:,.2f}"
    )

    print(
        f"Ledger-adjusted balance"
        f"       ${balance:,.2f}"
    )


if __name__ == "__main__":

    print_account_balance(
        "Chris 401(k)"
    )