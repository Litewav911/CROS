from datetime import date
from decimal import Decimal

from account_ledger import (
    LEDGER_ENTRIES,
    add_entry,
    calculate_balance,
)


# Start with a clean test ledger.
LEDGER_ENTRIES.clear()


print("ACCOUNT LEDGER TEST")
print("===================")


# Starting balance
add_entry(
    account_name="Chris 401(k)",
    entry_date=date(2027, 1, 1),
    entry_type="starting_balance",
    amount=Decimal("752073"),
    description="Retirement plan starting balance",
)


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


balance = calculate_balance(
    "Chris 401(k)"
)


print()
print(
    f"Starting balance: "
    f"$752,073.00"
)

print(
    f"Investment gain: "
    f"$10,000.00"
)

print(
    f"Withdrawal: "
    f"$5,000.00"
)

print(
    f"Roth conversion: "
    f"$20,000.00"
)

print(
    f"Ending balance: "
    f"${balance:,.2f}"
)


expected_balance = (
    Decimal("752073")
    + Decimal("10000")
    - Decimal("5000")
    - Decimal("20000")
)


assert balance == expected_balance


print()
print(
    "PASS: Account ledger correctly "
    "calculates balance changes."
)