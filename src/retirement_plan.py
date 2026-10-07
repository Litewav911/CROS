from dataclasses import dataclass
from decimal import Decimal
from datetime import date

from rental_cashflow import monthly_rental_cashflow
from tax_engine import (
    FEDERAL_STANDARD_DEDUCTION_MFJ_2026,
    NC_MFJ_STANDARD_DEDUCTION,
    calculate_employee_payroll_taxes_mfj_2026,
)


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

    # Real-scenario investment-return assumption.
    annual_return_assumption=Decimal(
        "0.05"
    ),
)


def apply_rental_passive_loss_limits(
    taxable_income_by_year: dict[int, Decimal],
) -> tuple[dict[int, Decimal], dict[int, Decimal]]:
    """Carry rental losses forward and apply them against later rental income.

    This conservative model does not apply the active-participation special
    allowance or losses from other passive activities.
    """

    allowed_income = {}
    loss_carryforward = {}
    suspended_loss = Decimal("0")
    for year, taxable_income in sorted(taxable_income_by_year.items()):
        taxable_income = Decimal(str(taxable_income))
        if taxable_income < 0:
            suspended_loss += -taxable_income
            allowed_income[year] = Decimal("0")
        else:
            offset = min(suspended_loss, taxable_income)
            suspended_loss -= offset
            allowed_income[year] = taxable_income - offset
        loss_carryforward[year] = suspended_loss
    return allowed_income, loss_carryforward


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


def build_modeled_income_schedules(
    start_year: int | None = None,
    end_year: int | None = None,
    income_assumptions: dict[str, object] | None = None,
) -> dict[str, dict[int, Decimal]]:
    """
    Build income and taxable-income schedules from modeled sources.

    Income source amounts are recurring assumptions rather than
    year-by-year taxable-income inputs. Transaction inflows are excluded.
    """

    if start_year is None:
        start_year = PLAN.retirement_start.year

    if end_year is None:
        end_year = PLAN.retirement_end_year

    if start_year > end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    assumptions = income_assumptions or {}
    rental_assumptions = assumptions.get("rental", {})
    investment_assumptions = assumptions.get("taxable_investments", {})
    employment_assumptions = assumptions.get("employment", {})

    extra_rental_expenses = Decimal(
        str(rental_assumptions.get("annual_other_expenses", 0))
    )
    annual_depreciation = Decimal(
        str(rental_assumptions.get("annual_depreciation", 0))
    )
    annual_interest = Decimal(
        str(investment_assumptions.get("annual_interest", 0))
    )
    annual_dividends = Decimal(
        str(investment_assumptions.get("annual_ordinary_dividends", 0))
    )
    annual_qualified_dividends = Decimal(
        str(investment_assumptions.get("annual_qualified_dividends", 0))
    )
    annual_net_long_term_capital_gains = Decimal(
        str(investment_assumptions.get("annual_net_long_term_capital_gains", 0))
    )
    investment_growth = Decimal(
        str(investment_assumptions.get("annual_growth", 0))
    )
    for name, amount in (
        ("Rental expenses", extra_rental_expenses),
        ("Rental depreciation", annual_depreciation),
        ("Taxable interest", annual_interest),
        ("Ordinary dividends", annual_dividends),
        ("Qualified dividends", annual_qualified_dividends),
        ("Net long-term capital gains", annual_net_long_term_capital_gains),
    ):
        if amount < 0:
            raise ValueError(f"{name} cannot be negative.")
    if investment_growth < Decimal("-1"):
        raise ValueError("Investment income growth cannot be less than -100%.")
    if annual_qualified_dividends > annual_dividends:
        raise ValueError(
            "Qualified dividends cannot exceed total ordinary dividends."
        )

    rental_cashflow = (
        monthly_rental_cashflow()["net_rental_cashflow"]
        * Decimal("12")
        - extra_rental_expenses
    )
    rental_taxable_income_before_limits = (
        rental_cashflow - annual_depreciation
    )

    employment_by_year = {
        year: Decimal("0") for year in range(start_year, end_year + 1)
    }
    employment_by_person_by_year = {
        name: {
            year: Decimal("0")
            for year in range(start_year, end_year + 1)
        }
        for name in employment_assumptions
    }
    for name, source in employment_assumptions.items():
        annual_salary = Decimal(str(source.get("annual_salary", 0)))
        last_work_date = source.get("last_work_date")
        if annual_salary < 0:
            raise ValueError("Annual employment income cannot be negative.")
        if annual_salary and last_work_date is None:
            raise ValueError(
                "Enter a last work date when annual employment income is provided."
            )
        if isinstance(last_work_date, str):
            last_work_date = date.fromisoformat(last_work_date)
        if not annual_salary or last_work_date is None:
            continue
        for year in range(start_year, end_year + 1):
            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)
            if last_work_date < year_start:
                continue
            paid_through = min(last_work_date, year_end)
            paid_days = (paid_through - year_start).days + 1
            year_days = (year_end - year_start).days + 1
            wages = annual_salary * Decimal(paid_days) / Decimal(year_days)
            employment_by_year[year] += wages
            employment_by_person_by_year[name][year] += wages

    investment_by_year = {}
    ordinary_income_by_year = {}
    federal_taxable_by_year = {}
    nc_taxable_by_year = {}
    provisional_income_by_year = {}
    preferential_income_by_year = {}
    qualified_dividends_by_year = {}
    capital_gains_by_year = {}
    total_income_by_year = {}
    payroll_tax_by_year = {}
    social_security_payroll_tax_by_year = {}
    medicare_payroll_tax_by_year = {}
    additional_medicare_tax_by_year = {}
    rental_by_year = {}
    rental_taxable_income_before_limits_by_year = {
        year: rental_taxable_income_before_limits
        for year in range(start_year, end_year + 1)
    }
    rental_taxable_income_by_year, rental_loss_carryforward_by_year = (
        apply_rental_passive_loss_limits(
            rental_taxable_income_before_limits_by_year
        )
    )
    for year in range(start_year, end_year + 1):
        payroll_tax = calculate_employee_payroll_taxes_mfj_2026(
            {
                name: wages_by_year[year]
                for name, wages_by_year in employment_by_person_by_year.items()
            }
        )
        payroll_tax_by_year[year] = payroll_tax.total_tax
        social_security_payroll_tax_by_year[year] = (
            payroll_tax.social_security_tax
        )
        medicare_payroll_tax_by_year[year] = payroll_tax.medicare_tax
        additional_medicare_tax_by_year[year] = (
            payroll_tax.additional_medicare_tax
        )
        years_after_start = year - start_year
        growth_factor = (
            (Decimal("1") + investment_growth) ** years_after_start
        )
        taxable_investment_income = (
            (annual_interest + annual_dividends)
            * growth_factor
        )
        qualified_dividends = annual_qualified_dividends * growth_factor
        net_long_term_capital_gains = (
            annual_net_long_term_capital_gains * growth_factor
        )
        preferential_income = qualified_dividends + net_long_term_capital_gains
        ordinary_income = (
            employment_by_year[year]
            + rental_taxable_income_by_year[year]
            + taxable_investment_income
        )
        total_income_for_tax = (
            ordinary_income
            + net_long_term_capital_gains
        )
        investment_by_year[year] = taxable_investment_income
        qualified_dividends_by_year[year] = qualified_dividends
        capital_gains_by_year[year] = net_long_term_capital_gains
        preferential_income_by_year[year] = preferential_income
        ordinary_income_by_year[year] = ordinary_income
        total_income_by_year[year] = total_income_for_tax
        federal_taxable_by_year[year] = max(
            Decimal("0"), total_income_for_tax
            - FEDERAL_STANDARD_DEDUCTION_MFJ_2026
        )
        nc_taxable_by_year[year] = max(
            Decimal("0"), total_income_for_tax - NC_MFJ_STANDARD_DEDUCTION
        )
        provisional_income_by_year[year] = total_income_for_tax
        rental_by_year[year] = rental_cashflow

    return {
        "employment_income": employment_by_year,
        "employment_income_by_person": employment_by_person_by_year,
        "payroll_tax": payroll_tax_by_year,
        "social_security_payroll_tax": social_security_payroll_tax_by_year,
        "medicare_payroll_tax": medicare_payroll_tax_by_year,
        "additional_medicare_tax": additional_medicare_tax_by_year,
        "rental_income": rental_by_year,
        "rental_taxable_income": rental_taxable_income_by_year,
        "rental_taxable_income_before_limits": (
            rental_taxable_income_before_limits_by_year
        ),
        "rental_loss_carryforward": rental_loss_carryforward_by_year,
        "taxable_investment_income": investment_by_year,
        "qualified_dividends": qualified_dividends_by_year,
        "net_long_term_capital_gains": capital_gains_by_year,
        "preferential_income": preferential_income_by_year,
        "ordinary_income": ordinary_income_by_year,
        "total_income": total_income_by_year,
        "federal_taxable_income": federal_taxable_by_year,
        "nc_taxable_income": nc_taxable_by_year,
        "provisional_other_income": provisional_income_by_year,
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
        f"Annual return assumption: "
        f"{PLAN.annual_return_assumption:.2%}"
    )

    print(
        f"Social Security: "
        f"{'Enabled' if PLAN.social_security_enabled else 'Disabled'}"
    )


if __name__ == "__main__":
    print_plan()
