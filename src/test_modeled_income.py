from datetime import date
from decimal import Decimal

from retirement_engine import RetirementEngineConfig, run_retirement_engine
from retirement_plan import build_modeled_income_schedules


def test_income_schedules_derive_from_recurring_sources_and_work_dates():
    schedules = build_modeled_income_schedules(
        start_year=2027,
        end_year=2028,
        income_assumptions={
            "employment": {
                "Chris": {
                    "annual_salary": Decimal("120000"),
                    "last_work_date": date(2027, 3, 26),
                }
            },
            "taxable_investments": {
                "annual_interest": Decimal("1000"),
                "annual_ordinary_dividends": Decimal("2000"),
                "annual_growth": Decimal("0.05"),
            },
            "rental": {
                "annual_other_expenses": Decimal("1000"),
                "annual_depreciation": Decimal("5000"),
            },
        },
    )

    salary_2027 = Decimal("120000") * Decimal("85") / Decimal("365")
    assert schedules["employment_income"] == {
        2027: salary_2027,
        2028: Decimal("0"),
    }
    assert schedules["rental_income"] == {
        2027: Decimal("33636.09"),
        2028: Decimal("33636.09"),
    }
    assert schedules["taxable_investment_income"] == {
        2027: Decimal("3000"),
        2028: Decimal("3150.00"),
    }
    assert schedules["ordinary_income"] == {
        2027: salary_2027 + Decimal("28636.09") + Decimal("3000"),
        2028: Decimal("28636.09") + Decimal("3150.00"),
    }
    assert schedules["federal_taxable_income"][2028] == Decimal("0")
    assert schedules["nc_taxable_income"][2028] == Decimal("6286.09")
    assert schedules["provisional_other_income"] == schedules["ordinary_income"]


def test_employment_income_requires_a_last_work_date():
    try:
        build_modeled_income_schedules(
            start_year=2027,
            end_year=2027,
            income_assumptions={
                "employment": {
                    "Chris": {"annual_salary": Decimal("50000")}
                }
            },
        )
    except ValueError as error:
        assert str(error) == (
            "Enter a last work date when annual employment income is provided."
        )
    else:
        raise AssertionError("A last work date should be required.")


def test_modeled_income_tax_is_included_in_portfolio_cash_need():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("0"),
        employment_income_by_year={2027: Decimal("80000")},
        rental_income_by_year={2027: Decimal("0")},
        base_taxable_income_by_year={2027: Decimal("47800")},
        nc_taxable_income_by_year={2027: Decimal("54500")},
        social_security_other_income_by_year={2027: Decimal("80000")},
    )

    result = run_retirement_engine(config)[0]

    assert result.outside_income == Decimal("80000")
    assert result.base_income_tax == Decimal("7414.5500")
    assert result.cash_need_before_withdrawal == result.base_income_tax
    assert result.net_cash_from_withdrawal.quantize(Decimal("0.01")) == (
        result.base_income_tax.quantize(Decimal("0.01"))
    )
    assert result.withdrawal_tax > Decimal("0")
