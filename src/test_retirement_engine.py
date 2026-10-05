from decimal import Decimal

from portfolio_projection import (
    apply_roth_conversion_destination,
    create_initial_account_balances,
)

from retirement_engine import (
    RetirementEngineConfig,
    _withdrawal_tax,
    run_retirement_engine,
)
from tax_engine import calculate_federal_tax_with_social_security_mfj_2026


def test_engine_carries_balances_forward():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2028,
        annual_return=Decimal("0.05"),
        monthly_spending_target=Decimal("0"),
    )

    results = run_retirement_engine(
        config
    )

    assert len(results) == 2

    assert (
        results[1].beginning_total
        == results[0].ending_total
    )


def test_engine_uses_chris_401k_under_normal_conditions():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("1000"),
        rental_income_by_year={
            2027: Decimal("0"),
        },
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

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

    initial_balances = {
        "Chris 401(k)": Decimal("100000"),
        "Stephanie 401(k)": Decimal("100000"),
        "Brokerage": Decimal("100000"),
        "Roth IRA": Decimal("100000"),
        "HSA": Decimal("0"),
        "Cash Reserve": Decimal("100000"),
    }

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("1000"),
        initial_balances=initial_balances,
        rental_income_by_year={
            2027: Decimal("0"),
        },
        market_declines_by_year={
            2027: True,
        },
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

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


def test_outside_income_reduces_portfolio_need():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("10000"),
        transaction_income_by_year={
            2027: Decimal("20000"),
        },
        rental_income_by_year={
            2027: Decimal("10000"),
        },
        social_security_by_year={
            2027: Decimal("10000"),
        },
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

    assert (
        result.outside_income
        == Decimal("40000")
    )

    assert (
        result.net_spending_need
        == Decimal("52383.56164383561643835616438")
    )

    assert (
        result.cash_need_before_withdrawal
        == Decimal("52383.56164383561643835616438")
    )

    assert (
        result.net_cash_from_withdrawal
        == result.cash_need_before_withdrawal
    )


def test_outside_income_can_fully_cover_spending():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("1000"),
        rental_income_by_year={
            2027: Decimal("20000"),
        },
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

    assert (
        result.planned_spending
        == Decimal("9238.356164383561643835616438")
    )

    assert (
        result.outside_income
        == Decimal("20000")
    )

    assert (
        result.net_spending_need
        == Decimal("0")
    )

    assert (
        result.cash_need_before_withdrawal
        == Decimal("0")
    )

    assert (
        result.gross_withdrawal
        == Decimal("0")
    )

    assert (
        result.withdrawal_allocations
        == {}
    )


def test_social_security_reduces_portfolio_need():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("10000"),
        rental_income_by_year={
            2027: Decimal("0"),
        },
        social_security_by_year={
            2027: Decimal("30000"),
        },
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

    assert (
        result.outside_income
        == Decimal("30000")
    )

    assert (
        result.net_spending_need
        == Decimal("62383.56164383561643835616438")
    )

    assert (
        result.cash_need_before_withdrawal
        == result.net_spending_need
    )


def test_roth_conversion_tax_is_added_after_outside_income():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("10000"),
        rental_income_by_year={
            2027: Decimal("30000"),
        },
        base_taxable_income_by_year={
            2027: Decimal("0"),
        },
        roth_conversions_by_year={
            2027: {
                "Chris 401(k)": Decimal("80000"),
            }
        },
        conversion_tax_funded_from_withdrawal=True,
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

    assert (
        result.net_spending_need
        == Decimal("62383.56164383561643835616438")
    )

    assert (
        result.conversion_amount
        == Decimal("80000")
    )

    assert (
        result.conversion_tax
        == Decimal("12296.0000")
    )

    assert (
        result.cash_need_before_withdrawal
        == (
            result.net_spending_need
            + result.conversion_tax
        )
    )


def test_social_security_taxable_benefit_affects_conversion_tax():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("0"),
        transaction_income_by_year={
            2027: Decimal("25000"),
        },
        rental_income_by_year={
            2027: Decimal("0"),
        },
        social_security_by_year={
            2027: Decimal("50000"),
        },
        base_taxable_income_by_year={
            2027: Decimal("25000"),
        },
        roth_conversions_by_year={
            2027: {
                "Chris 401(k)": Decimal("10000"),
            }
        },
        conversion_tax_funded_from_withdrawal=False,
    )

    result = run_retirement_engine(config)[0]

    # Gross Social Security remains spendable outside income.
    assert result.outside_income == Decimal("75000")

    # With $25,000 other income and $50,000 benefits, taxable
    # Social Security is $11,100 before and $19,600 after the
    # $10,000 conversion. Federal incremental tax is $2,220;
    # North Carolina conversion tax is $399.
    assert result.conversion_tax == Decimal("2619.0000")


def test_conversion_uses_separate_social_security_other_income():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("0"),
        social_security_by_year={
            2027: Decimal("50000"),
        },
        base_taxable_income_by_year={
            2027: Decimal("100000"),
        },
        social_security_other_income_by_year={
            2027: Decimal("25000"),
        },
        roth_conversions_by_year={
            2027: {
                "Chris 401(k)": Decimal("10000"),
            }
        },
        conversion_tax_funded_from_withdrawal=False,
    )

    result = run_retirement_engine(config)[0]

    expected_federal_tax = (
        calculate_federal_tax_with_social_security_mfj_2026(
            Decimal("110000"),
            Decimal("50000"),
            Decimal("35000"),
        )
        - calculate_federal_tax_with_social_security_mfj_2026(
            Decimal("100000"),
            Decimal("50000"),
            Decimal("25000"),
        )
    )

    assert result.conversion_tax == (
        expected_federal_tax
        + Decimal("399.0000")
    )


def test_social_security_taxable_benefit_affects_withdrawal_tax():

    withdrawal_tax = _withdrawal_tax(
        base_taxable_income=Decimal("25000"),
        conversion_amount=Decimal("10000"),
        withdrawal_amount=Decimal("10000"),
        social_security_benefits=Decimal("50000"),
    )

    assert withdrawal_tax == Decimal("2619.0000")


def test_withdrawal_uses_separate_social_security_other_income():

    withdrawal_tax = _withdrawal_tax(
        base_taxable_income=Decimal("100000"),
        conversion_amount=Decimal("10000"),
        withdrawal_amount=Decimal("10000"),
        social_security_benefits=Decimal("50000"),
        provisional_other_income=Decimal("25000"),
    )

    expected_federal_tax = (
        calculate_federal_tax_with_social_security_mfj_2026(
            Decimal("120000"),
            Decimal("50000"),
            Decimal("45000"),
        )
        - calculate_federal_tax_with_social_security_mfj_2026(
            Decimal("110000"),
            Decimal("50000"),
            Decimal("35000"),
        )
    )

    assert withdrawal_tax == (
        expected_federal_tax
        + Decimal("399.0000")
    )


def test_engine_applies_roth_conversion():

    initial_balances = {
        "Chris 401(k)": Decimal("100000"),
        "Stephanie 401(k)": Decimal("100000"),
        "Brokerage": Decimal("0"),
        "Roth IRA": Decimal("10000"),
        "HSA": Decimal("0"),
        "Cash Reserve": Decimal("0"),
    }

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2027,
        annual_return=Decimal("0"),
        monthly_spending_target=Decimal("0"),
        initial_balances=initial_balances,
        base_taxable_income_by_year={
            2027: Decimal("0"),
        },
        roth_conversions_by_year={
            2027: {
                "Chris 401(k)": Decimal("80000"),
            }
        },
        conversion_tax_funded_from_withdrawal=False,
    )

    results = run_retirement_engine(
        config
    )

    result = results[0]

    assert (
        result.conversion_amount
        == Decimal("80000")
    )

    assert (
        result.ending_balances[
            "Chris 401(k)"
        ]
        == Decimal("20000")
    )

    assert (
        result.ending_balances[
            "Roth IRA"
        ]
        == Decimal("90000")
    )

    # A Roth conversion is an internal transfer.
    # It must not increase total portfolio value.
    assert (
        result.ending_total
        == result.beginning_total
    )


def test_roth_conversion_compatibility_helper_does_not_double_count():

    initial_balances = (
        create_initial_account_balances()
    )

    initial_total = sum(
        initial_balances.values(),
        Decimal("0"),
    )

    # Simulate the state AFTER project_portfolio_year()
    # has already applied the conversion.
    converted_balances = dict(
        initial_balances
    )

    conversion_amount = Decimal("80000")

    converted_balances[
        "Chris 401(k)"
    ] -= conversion_amount

    converted_balances[
        "Roth IRA"
    ] += conversion_amount

    total_after_conversion = sum(
        converted_balances.values(),
        Decimal("0"),
    )

    assert (
        total_after_conversion
        == initial_total
    )

    # Defensive compatibility check:
    #
    # Older callers may still invoke the helper after the
    # portfolio projection has already applied the transfer.
    #
    # The helper must NOT subtract another $80,000 or add
    # another $80,000.
    result = (
        apply_roth_conversion_destination(
            account_balances=converted_balances,
            source_account="Chris 401(k)",
            destination_account="Roth IRA",
            conversion_amount=conversion_amount,
        )
    )

    assert result is converted_balances

    assert (
        result["Chris 401(k)"]
        == initial_balances["Chris 401(k)"]
        - conversion_amount
    )

    assert (
        result["Roth IRA"]
        == initial_balances["Roth IRA"]
        + conversion_amount
    )

    assert (
        sum(
            result.values(),
            Decimal("0"),
        )
        == initial_total
    )


def test_engine_produces_fourteen_years():

    config = RetirementEngineConfig(
        start_year=2027,
        end_year=2040,
        annual_return=Decimal("0.05"),
    )

    results = run_retirement_engine(
        config
    )

    assert len(results) == 14
