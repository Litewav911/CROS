from decimal import Decimal

from withdrawal_recommendation import (
    build_account_withdrawal,
)


print("WITHDRAWAL / PORTFOLIO INTEGRATION TEST")
print("========================================")


# --------------------------------------------------
# Normal market conditions
# --------------------------------------------------

normal_recommendation = {
    "portfolio_withdrawal": Decimal("60000"),
    "recommended_source": "Chris 401(k)",
}


normal_withdrawal = (
    build_account_withdrawal(
        normal_recommendation
    )
)


print()
print("NORMAL MARKET CONDITIONS")
print("------------------------")

print(
    f"Recommended source: "
    f"{normal_recommendation['recommended_source']}"
)

print(
    f"Withdrawal amount: "
    f"${normal_recommendation['portfolio_withdrawal']:,.2f}"
)

print(
    f"Account withdrawal: "
    f"{normal_withdrawal}"
)


assert normal_withdrawal == {
    "Chris 401(k)": Decimal("60000")
}


# --------------------------------------------------
# Market decline conditions
# --------------------------------------------------

decline_recommendation = {
    "portfolio_withdrawal": Decimal("60000"),
    "recommended_source": "Cash Reserve",
}


decline_withdrawal = (
    build_account_withdrawal(
        decline_recommendation
    )
)


print()
print("MARKET DECLINE CONDITIONS")
print("-------------------------")

print(
    f"Recommended source: "
    f"{decline_recommendation['recommended_source']}"
)

print(
    f"Withdrawal amount: "
    f"${decline_recommendation['portfolio_withdrawal']:,.2f}"
)

print(
    f"Account withdrawal: "
    f"{decline_withdrawal}"
)


assert decline_withdrawal == {
    "Cash Reserve": Decimal("60000")
}


# --------------------------------------------------
# No withdrawal
# --------------------------------------------------

no_withdrawal_recommendation = {
    "portfolio_withdrawal": Decimal("0"),
    "recommended_source": "None",
}


no_withdrawal = (
    build_account_withdrawal(
        no_withdrawal_recommendation
    )
)


print()
print("NO WITHDRAWAL")
print("-------------")

print(
    f"Account withdrawal: "
    f"{no_withdrawal}"
)


assert no_withdrawal == {}


print()
print(
    "PASS: Withdrawal recommendations correctly "
    "translate into account-specific portfolio withdrawals."
)