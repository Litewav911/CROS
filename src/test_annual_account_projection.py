from decimal import Decimal

from annual_account_projection import (
    get_starting_balance,
    project_account_year,
)


print("ANNUAL ACCOUNT PROJECTION TEST")
print("================================")


starting_balance = get_starting_balance(
    "Chris 401(k)"
)


print()
print(
    f"Chris 401(k) starting balance: "
    f"${starting_balance:,.2f}"
)


projection = project_account_year(
    year=2027,
    account_name="Chris 401(k)",
    beginning_balance=starting_balance,
    investment_gain=Decimal("50000"),
    withdrawal=Decimal("60000"),
    roth_conversion=Decimal("80000"),
)


print()
print(
    f"Beginning balance: "
    f"${projection.beginning_balance:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection.investment_gain:,.2f}"
)

print(
    f"Withdrawal: "
    f"${projection.withdrawal:,.2f}"
)

print(
    f"Roth conversion: "
    f"${projection.roth_conversion:,.2f}"
)

print(
    f"Ending balance: "
    f"${projection.ending_balance:,.2f}"
)


expected = (
    starting_balance
    + Decimal("50000")
    - Decimal("60000")
    - Decimal("80000")
)


assert (
    projection.ending_balance
    == expected
)


assert (
    projection.beginning_balance
    == Decimal("752073")
)


print()
print(
    "PASS: Annual account projection "
    "correctly calculates ending balance."
)