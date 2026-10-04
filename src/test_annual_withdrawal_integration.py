from decimal import Decimal

from withdrawal_recommendation import (
    calculate_account_withdrawal,
)

from portfolio_projection import (
    project_portfolio_year,
    create_initial_account_balances,
)


print("ANNUAL WITHDRAWAL / PORTFOLIO INTEGRATION TEST")
print("===============================================")


# --------------------------------------------------
# Get the actual withdrawal recommendation for
# January 2027.
# --------------------------------------------------

result = calculate_account_withdrawal(
    2027,
    1,
    market_decline=False,
)


recommendation = result[
    "recommendation"
]

account_withdrawal = result[
    "account_withdrawal"
]


print()
print("WITHDRAWAL RECOMMENDATION")
print("--------------------------")

print(
    f"Portfolio withdrawal: "
    f"${recommendation['portfolio_withdrawal']:,.2f}"
)

print(
    f"Recommended source: "
    f"{recommendation['recommended_source']}"
)

print(
    f"Account withdrawal: "
    f"{account_withdrawal}"
)


# --------------------------------------------------
# Project the portfolio using the recommendation.
# --------------------------------------------------

balances = create_initial_account_balances()


projection = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0.05"),
    withdrawals=account_withdrawal,
)


print()
print("PORTFOLIO PROJECTION")
print("--------------------")

print(
    f"Beginning portfolio: "
    f"${projection.beginning_total:,.2f}"
)

print(
    f"Investment gain: "
    f"${projection.investment_gain_total:,.2f}"
)

print(
    f"Withdrawal: "
    f"${projection.withdrawal_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection.ending_total:,.2f}"
)


# --------------------------------------------------
# Verify the projection actually used the
# recommended withdrawal.
# --------------------------------------------------

assert (
    projection.withdrawal_total
    == recommendation[
        "portfolio_withdrawal"
    ]
)


print()
print(
    "PASS: Annual portfolio projection correctly "
    "uses the withdrawal recommendation."
)