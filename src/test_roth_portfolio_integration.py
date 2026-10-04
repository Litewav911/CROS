from decimal import Decimal

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
    apply_roth_conversion_destination,
)


print("ROTH / PORTFOLIO INTEGRATION TEST")
print("=================================")


balances = create_initial_account_balances()

starting_total = sum(
    balances.values()
)


print()
print(
    f"Beginning portfolio: "
    f"${starting_total:,.2f}"
)


conversion = Decimal("80000")


projection = project_portfolio_year(
    year=2027,
    account_balances=balances,
    annual_return=Decimal("0"),
    withdrawals={},
    roth_conversions={
        "Chris 401(k)": conversion
    },
)


ending_balances = {
    account.account_name:
        account.ending_balance
    for account in projection.accounts
}


apply_roth_conversion_destination(
    account_balances=ending_balances,
    source_account="Chris 401(k)",
    destination_account="Roth IRA",
    conversion_amount=conversion,
)


ending_total = sum(
    ending_balances.values()
)


print(
    f"Roth conversion: "
    f"${conversion:,.2f}"
)

print(
    f"Chris 401(k) ending: "
    f"${ending_balances['Chris 401(k)']:,.2f}"
)

print(
    f"Roth IRA ending: "
    f"${ending_balances['Roth IRA']:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${ending_total:,.2f}"
)


# --------------------------------------------------
# Verify source account decreased
# --------------------------------------------------

expected_chris = (
    Decimal("752073")
    - conversion
)

assert (
    ending_balances["Chris 401(k)"]
    == expected_chris
)


# --------------------------------------------------
# Verify Roth increased
# --------------------------------------------------

expected_roth = (
    Decimal("31387")
    + conversion
)

assert (
    ending_balances["Roth IRA"]
    == expected_roth
)


# --------------------------------------------------
# Verify total portfolio is unchanged
# --------------------------------------------------

assert (
    ending_total
    == starting_total
)


# --------------------------------------------------
# Verify conversion recorded
# --------------------------------------------------

assert (
    projection.roth_conversion_total
    == conversion
)


print()
print(
    "PASS: Chris 401(k) decreases by the "
    "conversion amount."
)

print(
    "PASS: Roth IRA increases by the "
    "conversion amount."
)

print(
    "PASS: Total portfolio value is unchanged "
    "by the conversion."
)

print(
    "PASS: Roth conversion is integrated into "
    "the portfolio projection."
)