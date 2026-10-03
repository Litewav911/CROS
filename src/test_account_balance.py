from datetime import date
from decimal import Decimal

from account_ledger import (
    LEDGER_ENTRIES,
    add_entry,
)

from account_balance import (
    calculate_projected_balance,
)


print("ACCOUNT BALANCE INTEGRATION TEST")
print("================================")


# Start with a clean ledger.
LEDGER_ENTRIES.clear()


# The actual modeled Chris 401(k)
# balance is $752,073.


# Investment gain
add_entry(
    account_name="Chris 401(k)",
    entry_date=date(2027, 1, 31),
    entry_type="investment_gain",
    amount=Decimal("10000"),
    description="January investment gain",
)


# Retirement withdrawal
add_entry(
    account_name="Chris 401(k)",
    entry_date=date(2027, 2, 1),
    entry_type="withdrawal",
    amount=Decimal("5000"),
    description="Retirement spending withdrawal",
)


# Roth conversion
add_entry(
    account_name="Chris 401(k)",
    entry_date=date(2027, 2, 15),
    entry_type="roth_conversion_out",
    amount=Decimal("20000"),
    description="Roth conversion",
)


balance = calculate_projected_balance(
    "Chris 401(k)"
)


expected = (
    Decimal("752073")
    + Decimal("10000")
    - Decimal("5000")
    - Decimal("20000")
)


print()
print(
    "Modeled starting balance: "
    "$752,073.00"
)

print(
    "Investment gain: "
    "$10,000.00"
)

print(
    "Withdrawal: "
    "$5,000.00"
)

print(
    "Roth conversion: "
    "$20,000.00"
)

print(
    f"Projected balance: "
    f"${balance:,.2f}"
)


assert balance == expected


# Verify that a starting_balance ledger
# entry does not get counted twice.

add_entry(
    account_name="Chris 401(k)",
    entry_date=date(2027, 1, 1),
    entry_type="starting_balance",
    amount=Decimal("752073"),
    description="Historical starting balance",
)


balance_after_starting_entry = (
    calculate_projected_balance(
        "Chris 401(k)"
    )
)


assert (
    balance_after_starting_entry
    == expected
)


print()
print(
    "PASS: Retirement account balances "
    "are correctly integrated with the ledger."
)