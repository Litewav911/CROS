from dataclasses import dataclass
from decimal import Decimal
from datetime import date


@dataclass
class RetirementPlan:
    """
    Core retirement-plan assumptions.

    These are planning inputs, not transaction data.
    """

    retirement_start: date

    monthly_spending_target: Decimal

    annual_spending_target: Decimal

    retirement_end_year: int

    rule_of_55_enabled: bool

    roth_conversions_enabled: bool

    social_security_enabled: bool


PLAN = RetirementPlan(
    retirement_start=date(2027, 3, 26),

    monthly_spending_target=Decimal(
        "11000"
    ),

    annual_spending_target=Decimal(
        "132000"
    ),

    retirement_end_year=2040,

    rule_of_55_enabled=True,

    roth_conversions_enabled=True,

    social_security_enabled=True,
)


def print_plan():

    print()
    print("CROS RETIREMENT PLAN")
    print("=" * 40)

    print(
        f"Retirement start: "
        f"{PLAN.retirement_start}"
    )

    print(
        f"Monthly spending target: "
        f"${PLAN.monthly_spending_target:,.2f}"
    )

    print(
        f"Annual spending target: "
        f"${PLAN.annual_spending_target:,.2f}"
    )

    print(
        f"Planning horizon ends: "
        f"{PLAN.retirement_end_year}"
    )

    print(
        f"Rule of 55: "
        f"{'Enabled' if PLAN.rule_of_55_enabled else 'Disabled'}"
    )

    print(
        f"Roth conversions: "
        f"{'Enabled' if PLAN.roth_conversions_enabled else 'Disabled'}"
    )

    print(
        f"Social Security: "
        f"{'Enabled' if PLAN.social_security_enabled else 'Disabled'}"
    )


if __name__ == "__main__":
    print_plan()