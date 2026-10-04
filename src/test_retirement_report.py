from decimal import Decimal

from retirement_engine import (
    RetirementEngineConfig,
    run_retirement_engine,
)

from retirement_report import (
    build_retirement_report,
)


def test_retirement_report_preserves_engine_years():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2028,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("500000"),
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

    rows = build_retirement_report(
        results
    )

    assert len(rows) == 2

    assert rows[0].year == 2027
    assert rows[1].year == 2028


def test_retirement_report_preserves_portfolio_values():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("500000"),
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

    results = run_retirement_engine(
        config
    )

    rows = build_retirement_report(
        results
    )

    assert (
        rows[0].beginning_portfolio
        == results[0].beginning_total
    )

    assert (
        rows[0].ending_portfolio
        == results[0].ending_total
    )

    assert (
        rows[0].investment_gain
        == results[0].investment_gain_total
    )


def test_retirement_report_calculates_net_withdrawal():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("500000"),
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

    results = run_retirement_engine(
        config
    )

    rows = build_retirement_report(
        results
    )

    assert (
        rows[0].net_withdrawal
        == (
            results[0].gross_withdrawal
            - results[0].withdrawal_tax
        )
    )


def test_retirement_report_preserves_withdrawal_sources():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        initial_balances={
            "Chris 401(k)": Decimal("500000"),
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

    results = run_retirement_engine(
        config
    )

    rows = build_retirement_report(
        results
    )

    assert (
        rows[0].withdrawal_sources
        == results[0].withdrawal_allocations
    )