from datetime import date
from decimal import Decimal

from retirement_engine import RetirementEngineConfig, run_retirement_engine
from retirement_plan import (
    apply_rental_passive_loss_limits,
    build_modeled_income_schedules,
)


def test_rental_passive_losses_carry_forward_against_future_rental_income():
    taxable_income, carryforward = apply_rental_passive_loss_limits(
        {
            2027: Decimal("-10000"),
            2028: Decimal("3000"),
            2029: Decimal("10000"),
        }
    )

    assert taxable_income == {
        2027: Decimal("0"),
        2028: Decimal("0"),
        2029: Decimal("3000"),
    }
    assert carryforward == {
        2027: Decimal("10000"),
        2028: Decimal("7000"),
        2029: Decimal("0"),
    }


def test_rental_loss_schedule_does_not_reduce_other_taxable_income():
    schedules = build_modeled_income_schedules(
        start_year=2027,
        end_year=2028,
        income_assumptions={
            "employment": {
                "Chris": {
                    "annual_salary": Decimal("50000"),
                    "last_work_date": date(2028, 12, 31),
                }
            },
            "rental": {"annual_depreciation": Decimal("50000")},
        },
    )

    assert schedules["rental_taxable_income"] == {
        2027: Decimal("0"),
        2028: Decimal("0"),
    }
    assert schedules["rental_loss_carryforward"] == {
        2027: Decimal("15363.91"),
        2028: Decimal("30727.82"),
    }
    assert schedules["ordinary_income"] == schedules["employment_income"]


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
                "annual_qualified_dividends": Decimal("800"),
                "annual_net_long_term_capital_gains": Decimal("5000"),
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
    assert schedules["qualified_dividends"] == {
        2027: Decimal("800"), 2028: Decimal("840.00")
    }
    assert schedules["net_long_term_capital_gains"] == {
        2027: Decimal("5000"), 2028: Decimal("5250.00")
    }
    assert schedules["preferential_income"] == {
        2027: Decimal("5800"), 2028: Decimal("6090.00")
    }
    assert schedules["federal_taxable_income"][2028] == Decimal("4836.09")
    assert schedules["nc_taxable_income"][2028] == Decimal("11536.09")
    assert schedules["provisional_other_income"][2028] == Decimal("37036.09")


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


def test_qualified_dividends_cannot_exceed_total_ordinary_dividends():
    try:
        build_modeled_income_schedules(
            start_year=2027,
            end_year=2027,
            income_assumptions={
                "taxable_investments": {
                    "annual_ordinary_dividends": Decimal("100"),
                    "annual_qualified_dividends": Decimal("101"),
                }
            },
        )
    except ValueError as error:
        assert str(error) == (
            "Qualified dividends cannot exceed total ordinary dividends."
        )
    else:
        raise AssertionError("Qualified dividends must be a subset of dividends.")


def test_payroll_tax_schedule_uses_wages_for_each_person():
    schedules = build_modeled_income_schedules(
        start_year=2027,
        end_year=2027,
        income_assumptions={
            "employment": {
                "Chris": {
                    "annual_salary": Decimal("200000"),
                    "last_work_date": date(2027, 12, 31),
                },
                "Stephanie": {
                    "annual_salary": Decimal("200000"),
                    "last_work_date": date(2027, 12, 31),
                },
            }
        },
    )

    assert schedules["payroll_tax"] == {2027: Decimal("30028.00")}
    assert schedules["social_security_payroll_tax"] == {
        2027: Decimal("22878.00")
    }
    assert schedules["medicare_payroll_tax"] == {
        2027: Decimal("5800.00")
    }
    assert schedules["additional_medicare_tax"] == {
        2027: Decimal("1350.00")
    }


def test_payroll_taxes_reduce_employment_cash_flow_in_retirement_engine():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        monthly_spending_target=Decimal("0"),
        employment_income_by_year={2027: Decimal("80000")},
        payroll_tax_by_year={2027: Decimal("6120")},
        rental_income_by_year={2027: Decimal("0")},
        initial_balances={},
    )

    result = run_retirement_engine(config)[0]

    assert result.employment_income == Decimal("80000")
    assert result.payroll_tax == Decimal("6120")
    assert result.outside_income == Decimal("73880")


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
