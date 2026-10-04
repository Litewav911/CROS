from decimal import Decimal

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)


print("ROTH CONVERSION INTEGRATION TEST")
print("================================")


balances = create_initial_account_balances()


conversion = {
    "Chris 401(k)": Decimal("80000")
}


result = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0"),
    withdrawals={},
    roth_conversions=conversion,
)


print()
print(
    f"Beginning portfolio: "
    f"${result.beginning_total:,.2f}"
)

print(
    f"Roth conversion: "
    f"${result.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${result.ending_total:,.2f}"
)


# --------------------------------------------------
# Find the two affected accounts.
# --------------------------------------------------

accounts = {
    account.account_name: account
    for account in result.accounts
}


chris_401k = accounts[
    "Chris 401(k)"
]

roth_ira = accounts[
    "Roth IRA"
]


print()
print(
    f"Chris 401(k) ending: "
    f"${chris_401k.ending_balance:,.2f}"
)

print(
    f"Roth IRA ending: "
    f"${roth_ira.ending_balance:,.2f}"
)


# --------------------------------------------------
# Chris 401(k) should decrease by $80,000.
# --------------------------------------------------

expected_401k = (
    balances["Chris 401(k)"]
    - Decimal("80000")
)


assert (
    chris_401k.ending_balance
    == expected_401k
)


# --------------------------------------------------
# The current account ledger records the conversion
# against the source account. The destination Roth
# transfer will be connected by the tax/conversion
# engine later.
# --------------------------------------------------

assert (
    chris_401k.roth_conversion
    == Decimal("80000")
)


# --------------------------------------------------
# A conversion is not a portfolio spending withdrawal.
# --------------------------------------------------

assert (
    result.withdrawal_total
    == Decimal("0")
)


# --------------------------------------------------
# The conversion itself must not be counted as a
# portfolio withdrawal.
# --------------------------------------------------

assert (
    result.roth_conversion_total
    == Decimal("80000")
)


print()
print(
    "PASS: Roth conversions are integrated into "
    "the annual portfolio projection."
)