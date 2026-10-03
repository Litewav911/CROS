from decimal import Decimal

from retirement_accounts import (
    RETIREMENT_ACCOUNTS,
    get_account,
    total_modeled_assets,
)


print("RETIREMENT ACCOUNT TEST")
print("=======================")

print()
print("Accounts:")
for account in RETIREMENT_ACCOUNTS:
    print(
        f"{account.name}: "
        f"${account.balance:,.2f}"
    )


chris_401k = get_account("Chris 401(k)")

print()
print("Chris 401(k) properties:")
print(
    f"Rule of 55 eligible: "
    f"{chris_401k.rule_of_55_eligible}"
)
print(
    f"Subject to RMD: "
    f"{chris_401k.subject_to_rmd}"
)
print(
    f"Intended use: "
    f"{chris_401k.intended_use}"
)


assert chris_401k.rule_of_55_eligible is True
assert chris_401k.subject_to_rmd is True
assert (
    chris_401k.intended_use
    == "primary_early_retirement_withdrawal"
)

assert (
    total_modeled_assets()
    == Decimal("1219138.61")
)


print()
print(
    "PASS: Retirement account model "
    "is working correctly."
)