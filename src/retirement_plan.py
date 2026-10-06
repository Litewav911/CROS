from dataclasses import dataclass, field
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

    non_social_security_taxable_income_by_year: dict[
        int, Decimal
    ] = field(default_factory=dict)

    tax_exempt_interest_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )


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
    annual_roth_conversion_target: Decimal | None = None,
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

    conversion_target = (
        PLAN.annual_roth_conversion_target
        if annual_roth_conversion_target is None
        else Decimal(str(annual_roth_conversion_target))
    )

    return {
        year: {
            "Chris 401(k)": (
                conversion_target
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


def build_social_security_other_income_schedule(
    start_year: int | None = None,
    end_year: int | None = None,
) -> dict[int, Decimal]:
    """Build the non-Social-Security income used for provisional income.

    Use the annual non-Social-Security income input when provided.
    Otherwise retain the existing base taxable-income assumption
    as a proxy. Add tax-exempt interest for each year.
    """

    base_income = build_base_taxable_income_schedule(
        start_year=start_year,
        end_year=end_year,
    )

    return {
        year: PLAN.non_social_security_taxable_income_by_year.get(
            year,
            base_income[year],
        )
        + PLAN.tax_exempt_interest_by_year.get(
            year,
            Decimal("0"),
        )
        for year in base_income
    }


def build_social_security_benefit_schedule(
    start_year: int | None = None,
    end_year: int | None = None,
    claimant_inputs: dict[str, dict[str, Decimal | int]] | None = None,
) -> dict[int, Decimal]:
    """Build annual benefits from claimant estimates and claiming inputs.

    Each claimant provides a birth year, claiming age, monthly benefit
    estimated by SSA for that claiming age, and assumed annual COLA.
    The first modeled benefit year is the birth year plus claiming age.
    """

    if start_year is None:
        start_year = PLAN.retirement_start.year

    if end_year is None:
        end_year = PLAN.retirement_end_year

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    if not PLAN.social_security_enabled:
        return {
            year: Decimal("0")
            for year in range(start_year, end_year + 1)
        }

    annual_benefits = {
        year: Decimal("0") for year in range(start_year, end_year + 1)
    }
    for claimant in (claimant_inputs or {}).values():
        birth_year = int(claimant["birth_year"])
        claiming_age = int(claimant["claiming_age"])
        monthly_benefit = Decimal(str(claimant["monthly_benefit"]))
        annual_cola = Decimal(str(claimant["annual_cola"]))
        if not 62 <= claiming_age <= 70:
            raise ValueError("Claiming age must be between 62 and 70.")
        if monthly_benefit < 0:
            raise ValueError("Monthly Social Security benefit cannot be negative.")
        if annual_cola < Decimal("-1"):
            raise ValueError("Annual COLA cannot be less than -100%.")

        first_benefit_year = birth_year + claiming_age
        modeled_start_year = max(start_year, first_benefit_year)
        monthly_amount = monthly_benefit * (
            Decimal("1") + annual_cola
        ) ** max(0, modeled_start_year - first_benefit_year)
        for year in range(modeled_start_year, end_year + 1):
            annual_benefits[year] += monthly_amount * Decimal("12")
            monthly_amount *= Decimal("1") + annual_cola

    return annual_benefits


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
