from decimal import Decimal

from retirement_engine import (
    RetirementEngineConfig,
    run_retirement_engine,
)


def test_engine_carries_balances_forward():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2028,
        annual_return=Decimal("0.05"),
        initial_balances={
            "Chris 401(k)": Decimal("100000"),
            "Stephanie 401(k)": Decimal("0"),
            "Brokerage": Decimal("0"),
            "Roth IRA": Decimal("0"),
            "HSA": Decimal("0"),
            "Cash Reserve": Decimal("0"),
        },
        rental_income_by_year={
            2027: Decimal("0"),
            2028: Decimal("0"),
        },
    )

    results = run_retirement_engine(
        config
    )

    assert len(results) == 2

    first = results[0]
    second = results[1]

    assert (
        second.beginning_balances[
            "Chris 401(k)"
        ]
        == first.ending_balances[
            "Chris 401(k)"
        ]
    )


def test_engine_uses_chris_401k_under_normal_conditions():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("200000"),
            "Stephanie 401(k)": Decimal("0"),
            "Brokerage": Decimal("0"),
            "Roth IRA": Decimal("0"),
            "HSA": Decimal("0"),
            "Cash Reserve": Decimal("0"),
        },
        rental_income_by_year={
            2027: Decimal("0"),
        },
    )

    result = run_retirement_engine(
        config
    )[0]

    assert (
        "Chris 401(k)"
        in result.withdrawal_allocations
    )

    assert (
        result.withdrawal_allocations[
            "Chris 401(k)"
        ]
        > Decimal("0")
    )


def test_engine_uses_cash_reserve_during_market_decline():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        market_declines_by_year={
            2027: True,
        },
        initial_balances={
            "Chris 401(k)": Decimal("200000"),
            "Stephanie 401(k)": Decimal("0"),
            "Brokerage": Decimal("0"),
            "Roth IRA": Decimal("0"),
            "HSA": Decimal("0"),
            "Cash Reserve": Decimal("50000"),
        },
        rental_income_by_year={
            2027: Decimal("0"),
        },
    )

    result = run_retirement_engine(
        config
    )[0]

    assert (
        "Cash Reserve"
        in result.withdrawal_allocations
    )

    assert (
        result.withdrawal_allocations[
            "Cash Reserve"
        ]
        > Decimal("0")
    )


def test_engine_applies_roth_conversion():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        base_taxable_income_by_year={
            2027: Decimal("100000"),
        },
        roth_conversions_by_year={
            2027: {
                "Chris 401(k)": Decimal("50000"),
            },
        },
        initial_balances={
            "Chris 401(k)": Decimal("200000"),
            "Stephanie 401(k)": Decimal("0"),
            "Brokerage": Decimal("0"),
            "Roth IRA": Decimal("10000"),
            "HSA": Decimal("0"),
            "Cash Reserve": Decimal("100000"),
        },
        rental_income_by_year={
            2027: Decimal("0"),
        },
    )

    result = run_retirement_engine(
        config
    )[0]

    assert (
        result.conversion_amount
        == Decimal("50000")
    )

    assert (
        result.conversion_tax
        > Decimal("0")
    )

    assert (
        result.ending_balances[
            "Chris 401(k)"
        ]
        < Decimal("200000")
    )

    assert (
        result.ending_balances[
            "Roth IRA"
        ]
        > Decimal("10000")
    )


def test_engine_produces_fourteen_years():
    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2040,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("1000000"),
            "Stephanie 401(k)": Decimal("0"),
            "Brokerage": Decimal("0"),
            "Roth IRA": Decimal("0"),
            "HSA": Decimal("0"),
            "Cash Reserve": Decimal("0"),
        },
        rental_income_by_year={
            year: Decimal("0")
            for year in range(2027, 2041)
        },
    )

    results = run_retirement_engine(
        config
    )

    assert len(results) == 14

    assert results[0].year == 2027
    assert results[-1].year == 2040