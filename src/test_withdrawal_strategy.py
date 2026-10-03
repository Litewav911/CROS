from decimal import Decimal

from withdrawal_strategy import (
    select_withdrawal_source,
)


print("WITHDRAWAL STRATEGY TEST")
print("=========================")


normal = select_withdrawal_source(
    Decimal("5000"),
    market_decline=False,
)

print()
print("NORMAL MARKET CONDITIONS")
print(
    f"Source: {normal.source}"
)
print(
    f"Amount: ${normal.amount:,.2f}"
)
print(
    f"Reason: {normal.reason}"
)


assert normal.source == "Chris 401(k)"
assert normal.amount == Decimal("5000")


reserve = select_withdrawal_source(
    Decimal("5000"),
    market_decline=True,
)

print()
print("MARKET DECLINE")
print(
    f"Source: {reserve.source}"
)
print(
    f"Amount: ${reserve.amount:,.2f}"
)
print(
    f"Reason: {reserve.reason}"
)


assert reserve.source == "Cash Reserve"
assert reserve.amount == Decimal("5000")


none = select_withdrawal_source(
    Decimal("0"),
)

print()
print("NO WITHDRAWAL")
print(
    f"Source: {none.source}"
)
print(
    f"Amount: ${none.amount:,.2f}"
)


assert none.source == "None"
assert none.amount == Decimal("0")


print()
print(
    "PASS: Withdrawal source strategy "
    "is working correctly."
)