from decimal import Decimal

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
    project_portfolio_years,
)


print("PORTFOLIO PROJECTION TEST")
print("==========================")


# --------------------------------------------------
# Initial portfolio
# --------------------------------------------------

balances = create_initial_account_balances()

beginning_total = sum(
    balances.values(),
    Decimal("0"),
)

print()
print(
    f"Beginning portfolio: "
    f"${beginning_total:,.2f}"
)


# --------------------------------------------------
# Test 1: Investment return
# --------------------------------------------------

result = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0.05"),
    withdrawals={},
    roth_conversions={},
)

expected_gain = (
    beginning_total
    * Decimal("0.05")
)

expected_ending = (
    beginning_total
    + expected_gain
)

print(
    f"Investment gain: "
    f"${result.investment_gain_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${result.ending_total:,.2f}"
)

assert (
    result.investment_gain_total
    == expected_gain
)

assert (
    result.ending_total
    == expected_ending
)


# --------------------------------------------------
# Test 2: Multi-year compounding
#
# This test is specifically testing investment
# compounding. It intentionally uses zero withdrawals
# and zero Roth conversions so that retirement
# cash-flow rules do not affect the result.
# --------------------------------------------------

zero_withdrawals = {
    year: {}
    for year in range(2027, 2041)
}

zero_roth_conversions = {
    year: {}
    for year in range(2027, 2041)
}

projections = project_portfolio_years(
    start_year=2027,
    end_year=2040,
    annual_return=Decimal("0.05"),
    withdrawals_by_year=zero_withdrawals,
    roth_conversions_by_year=zero_roth_conversions,
)

assert len(projections) == 14

print()
print(
    f"2027 ending: "
    f"${projections[0].ending_total:,.2f}"
)

print(
    f"2040 ending: "
    f"${projections[-1].ending_total:,.2f}"
)


# --------------------------------------------------
# Verify year-to-year carry forward
# --------------------------------------------------

for index in range(1, len(projections)):

    previous = projections[index - 1]
    current = projections[index]

    assert (
        current.beginning_total
        == previous.ending_total
    )


# --------------------------------------------------
# Test 3: Account-specific withdrawal
# --------------------------------------------------

withdrawal_amount = Decimal("60000")

withdrawal_result = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0.05"),
    withdrawals={
        "Chris 401(k)": withdrawal_amount
    },
    roth_conversions={},
)

print()
print("ACCOUNT WITHDRAWAL TEST")
print("-----------------------")

print(
    f"Withdrawal: "
    f"${withdrawal_result.withdrawal_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${withdrawal_result.ending_total:,.2f}"
)

assert (
    withdrawal_result.withdrawal_total
    == withdrawal_amount
)

chris_account = next(
    account
    for account in withdrawal_result.accounts
    if account.account_name
    == "Chris 401(k)"
)

assert (
    chris_account.withdrawal
    == withdrawal_amount
)


# --------------------------------------------------
# Test 4: Roth conversion
# --------------------------------------------------

conversion_amount = Decimal("80000")

conversion_result = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0"),
    withdrawals={},
    roth_conversions={
        "Chris 401(k)": conversion_amount
    },
)

print()
print("ROTH CONVERSION TEST")
print("--------------------")

print(
    f"Roth conversion: "
    f"${conversion_result.roth_conversion_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${conversion_result.ending_total:,.2f}"
)

assert (
    conversion_result.roth_conversion_total
    == conversion_amount
)

chris_conversion_account = next(
    account
    for account in conversion_result.accounts
    if account.account_name
    == "Chris 401(k)"
)

assert (
    chris_conversion_account.roth_conversion
    == conversion_amount
)


# --------------------------------------------------
# A Roth conversion is not a spending withdrawal.
# --------------------------------------------------

assert (
    conversion_result.withdrawal_total
    == Decimal("0")
)


# --------------------------------------------------
# Final result
# --------------------------------------------------

print()
print(
    "PASS: Portfolio projection correctly handles "
    "investment returns, year-to-year balances, "
    "account-specific withdrawals, and Roth conversions."
)