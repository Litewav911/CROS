from decimal import Decimal, ROUND_HALF_UP

from real_retirement_scenario import (
    CASH_RESERVE,
    build_real_retirement_config,
    run_real_retirement_scenario,
)
from retirement_plan import PLAN
from retirement_plan import build_social_security_benefit_schedule
from rental_cashflow import monthly_rental_cashflow


CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    """
    Round a modeled monetary value to the nearest cent.
    """

    return value.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def test_real_retirement_scenario_produces_fourteen_years():

    results = run_real_retirement_scenario()

    assert len(results) == 14

    assert results[0].year == 2027
    assert results[-1].year == 2040


def test_real_retirement_config_supplies_provisional_income_schedule():

    config = build_real_retirement_config()
    annual_rental_cashflow = (
        monthly_rental_cashflow()["net_rental_cashflow"]
        * Decimal("12")
    )

    assert config.social_security_other_income_by_year == {
        year: annual_rental_cashflow
        for year in range(
            PLAN.retirement_start.year,
            PLAN.retirement_end_year + 1,
        )
    }
    assert config.social_security_by_year == {
        year: Decimal("0")
        for year in range(
            PLAN.retirement_start.year,
            PLAN.retirement_end_year + 1,
        )
    }


def test_real_retirement_config_accepts_plan_assumption_overrides():

    config = build_real_retirement_config(
        monthly_spending_target=Decimal("12500"),
        annual_return_assumption=Decimal("0.04"),
        annual_roth_conversion_target=Decimal("50000"),
    )

    assert config.monthly_spending_target == Decimal("12500")
    assert config.annual_return == Decimal("0.04")
    assert config.roth_conversions_by_year == {
        year: {"Chris 401(k)": Decimal("50000")}
        for year in range(2027, 2041)
    }
    assert config.base_taxable_income_by_year == {
        year: Decimal("34636.09")
        for year in range(2027, 2041)
    }
    assert config.social_security_by_year == {
        year: Decimal("0")
        for year in range(2027, 2041)
    }


def test_real_retirement_scenario_applies_plan_assumption_overrides():

    results = run_real_retirement_scenario(
        monthly_spending_target=Decimal("12500"),
        annual_return_assumption=Decimal("0.04"),
        annual_roth_conversion_target=Decimal("50000"),
    )

    assert results[0].planned_spending > Decimal("101621.92")
    assert results[0].conversion_amount == Decimal("50000")


def test_real_retirement_config_uses_calculated_social_security_schedule():
    benefits = build_social_security_benefit_schedule(
        claimant_inputs={
            "Chris": {
                "birth_year": 1960,
                "claiming_age": 67,
                "monthly_benefit": Decimal("2000"),
                "annual_cola": Decimal("0.02"),
            }
        }
    )
    config = build_real_retirement_config(social_security_by_year=benefits)

    assert config.social_security_by_year[2027] == Decimal("24000")
    assert config.social_security_by_year[2028] == Decimal("24480.00")
    assert config.social_security_by_year[2029] == Decimal("24969.6000")
    assert config.social_security_other_income_by_year == {
        year: Decimal("34636.09")
        for year in range(2027, 2041)
    }


def test_social_security_schedule_starts_at_claiming_year_and_applies_cola():
    schedule = build_social_security_benefit_schedule(
        start_year=2027,
        end_year=2030,
        claimant_inputs={
            "Chris": {
                "birth_year": 1960,
                "claiming_age": 67,
                "monthly_benefit": Decimal("2500"),
                "annual_cola": Decimal("0.03"),
            },
            "Stephanie": {
                "birth_year": 1961,
                "claiming_age": 67,
                "monthly_benefit": Decimal("1800"),
                "annual_cola": Decimal("0"),
            },
        },
    )

    assert schedule == {
        2027: Decimal("30000"),
        2028: Decimal("52500.00"),
        2029: Decimal("53427.0000"),
        2030: Decimal("54381.810000"),
    }


def test_real_retirement_scenario_uses_partial_first_year():

    results = run_real_retirement_scenario()

    result = results[0]

    assert money(
        result.planned_spending
    ) == Decimal("101621.92")


def test_real_retirement_scenario_has_expected_outside_income():

    results = run_real_retirement_scenario()

    for result in results:

        outside_income = (
            result.transaction_income
            + result.rental_income
            + result.social_security
        )

        assert money(
            outside_income
        ) == Decimal("34636.09")


def test_real_retirement_scenario_uses_starting_cash_reserve():

    results = run_real_retirement_scenario()

    first_result = results[0]

    assert (
        first_result.beginning_balances[
            "Cash Reserve"
        ]
        == CASH_RESERVE
    )


def test_real_retirement_scenario_uses_eighty_thousand_roth_conversion_target():

    results = run_real_retirement_scenario()

    for result in results:

        if result.year in {
            2027,
            2028,
            2029,
            2030,
        }:

            assert (
                result.conversion_amount
                == Decimal("80000")
            )


def test_real_retirement_scenario_has_no_cash_shortfall():

    results = run_real_retirement_scenario()

    for result in results:

        shortfall = max(
            Decimal("0"),
            result.cash_need_before_withdrawal
            - result.net_cash_from_withdrawal,
        )

        assert money(shortfall) == Decimal("0.00")


def test_real_retirement_scenario_ending_portfolio_matches_baseline():

    results = run_real_retirement_scenario()

    final_result = results[-1]

    assert (
        money(final_result.ending_total)
        == Decimal("284465.52")
    )


def test_real_retirement_scenario_ends_with_expected_account_balances():

    results = run_real_retirement_scenario()

    final_balances = results[-1].ending_balances

    assert money(
        final_balances["Chris 401(k)"]
    ) == Decimal("0.00")

    assert money(
        final_balances["Stephanie 401(k)"]
    ) == Decimal("0.00")

    assert money(
        final_balances["Brokerage"]
    ) == Decimal("0.00")

    assert money(
        final_balances["Roth IRA"]
    ) == Decimal("241968.27")

    assert money(
        final_balances["HSA"]
    ) == Decimal("42497.25")

    assert money(
        final_balances["Cash Reserve"]
    ) == Decimal("0.00")
