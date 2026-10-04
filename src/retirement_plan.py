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

    annual_roth_conversion_target: Decimal

    annual_base_taxable_income: Decimal

    annual_return_assumption: Decimal


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

    # Real CROS scenario target.
    #
    # This is the planned annual Roth conversion from
    # Chris's 401(k).
    #
    # The retirement engine may reduce the actual conversion
    # when the Chris 401(k) balance cannot support the full
    # requested amount.
    annual_roth_conversion_target=Decimal(
        "80000"
    ),

    # Real-scenario taxable-income assumption.
    #
    # This is intentionally an explicit planning input so that
    # the tax engine can later replace it with actual projected
    # taxable income.
    annual_base_taxable_income=Decimal(
        "100000"
    ),

    # Real-scenario investment-return assumption.
    annual_return_assumption=Decimal(
        "0.05"
    ),
)


def build_roth_conversion_schedule(
    start_year: int | None = None,
    end_year: int | None = None,
) -> dict[int, dict[str, Decimal]]:
    """
    Build the Roth-conversion schedule for the real retirement
    scenario.

    The requested conversion is $80,000 per year from 2027
    through the end of the retirement-plan horizon.

    The retirement engine is responsible for capping the actual
    conversion when the source account cannot support the full
    requested amount.

    Therefore the schedule represents TARGETS, not guaranteed
    transaction amounts.
    """

    if not PLAN.roth_conversions_enabled:
        return {}

    if start_year is None:
        start_year = PLAN.retirement_start.year

    if end_year is None:
        end_year = PLAN.retirement_end_year

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    return {
        year: {
            "Chris 401(k)": (
                PLAN.annual_roth_conversion_target
            )
        }
        for year in range(
            start_year,
            end_year + 1,
        )
    }


def build_base_taxable_income_schedule(
    start_year: int | None = None,
    end_year: int | None = None,
) -> dict[int, Decimal]:
    """
    Build the base taxable-income schedule used by the real
    retirement scenario.

    This remains a planning assumption until the production tax
    engine replaces it with dynamically calculated taxable income.
    """

    if start_year is None:
        start_year = PLAN.retirement_start.year

    if end_year is None:
        end_year = PLAN.retirement_end_year

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    return {
        year: PLAN.annual_base_taxable_income
        for year in range(
            start_year,
            end_year + 1,
        )
    }


def print_plan():
    """
    Print the current CROS retirement-plan assumptions.
    """

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
        f"Annual Roth conversion target: "
        f"${PLAN.annual_roth_conversion_target:,.2f}"
    )

    print(
        f"Base taxable income assumption: "
        f"${PLAN.annual_base_taxable_income:,.2f}"
    )

    print(
        f"Annual return assumption: "
        f"{PLAN.annual_return_assumption:.2%}"
    )

    print(
        f"Social Security: "
        f"{'Enabled' if PLAN.social_security_enabled else 'Disabled'}"
    )


if __name__ == "__main__":
    print_plan()