from decimal import Decimal

from portfolio_projection import (
    project_portfolio_year,
)


print("PORTFOLIO PROJECTION TEST")
print("==========================")


projection = project_portfolio_year(
    2027
)


print()

for account in projection.accounts:

    print(
        f"{account.account_name:25}"
        f"${account.beginning_balance:>14,.2f}"
    )


print()
print(
    f"Beginning portfolio: "
    f"${projection.beginning_total:,.2f}"
)

print(
    f"Ending portfolio: "
    f"${projection.ending_total:,.2f}"
)


expected_total = Decimal(
    "1219138.61"
)


assert (
    projection.beginning_total
    == expected_total
)


assert (
    projection.ending_total
    == expected_total
)


assert (
    len(projection.accounts)
    == 6
)


assert (
    projection.investment_gain_total
    == Decimal("0")
)


assert (
    projection.withdrawal_total
    == Decimal("0")
)


assert (
    projection.roth_conversion_total
    == Decimal("0")
)


print()
print(
    "PASS: Consolidated portfolio projection "
    "correctly includes all modeled accounts."
)