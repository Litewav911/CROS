from decimal import Decimal, ROUND_HALF_UP

from real_retirement_scenario import (
    CASH_RESERVE,
    run_real_retirement_scenario,
)


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
        == Decimal("178851.88")
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
    ) == Decimal("136354.62")

    assert money(
        final_balances["HSA"]
    ) == Decimal("42497.25")

    assert money(
        final_balances["Cash Reserve"]
    ) == Decimal("0.00")