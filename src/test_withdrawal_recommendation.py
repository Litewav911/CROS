from decimal import Decimal

from withdrawal_strategy import (
    select_withdrawal_source,
)


print("WITHDRAWAL RECOMMENDATION TEST")
print("================================")


print()
print("NORMAL MARKET CONDITIONS")
print("------------------------")

normal = select_withdrawal_source(
    Decimal("5000"),
    market_decline=False,
)

print(
    f"Withdrawal required: "
    f"${normal.amount:,.2f}"
)

print(
    f"Recommended source: "
    f"{normal.source}"
)

print(
    f"Reason: "
    f"{normal.reason}"
)


assert normal.amount == Decimal("5000")
assert normal.source == "Chris 401(k)"


print()
print("MARKET DECLINE CONDITIONS")
print("--------------------------")

decline = select_withdrawal_source(
    Decimal("5000"),
    market_decline=True,
)

print(
    f"Withdrawal required: "
    f"${decline.amount:,.2f}"
)

print(
    f"Recommended source: "
    f"{decline.source}"
)

print(
    f"Reason: "
    f"{decline.reason}"
)


assert decline.amount == Decimal("5000")
assert decline.source == "Cash Reserve"


print()
print(
    "PASS: Withdrawal recommendation "
    "logic is working correctly."
)