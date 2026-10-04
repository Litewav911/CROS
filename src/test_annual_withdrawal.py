from decimal import Decimal

from annual_withdrawal import (
    calculate_annual_withdrawal,
)

from rental_cashflow import (
    monthly_rental_cashflow,
)


def test_annual_withdrawal_processes_twelve_months():
    result = calculate_annual_withdrawal(
        2027,
        market_decline=False,
    )

    assert (
        len(result["monthly_results"])
        == 12
    )


def test_annual_withdrawal_uses_authoritative_rental_cashflow():
    result = calculate_annual_withdrawal(
        2027,
        market_decline=False,
    )

    monthly_rental = Decimal(
        str(
            monthly_rental_cashflow()[
                "net_rental_cashflow"
            ]
        )
    )

    expected_rental_income = (
        monthly_rental * Decimal("12")
    )

    actual = result[
        "total_rental_income"
    ].quantize(
        Decimal("0.01")
    )

    expected = expected_rental_income.quantize(
        Decimal("0.01")
    )

    assert actual == expected


def test_annual_withdrawal_aggregates_positive_requirements():
    result = calculate_annual_withdrawal(
        2027,
        market_decline=False,
    )

    expected_requirement = Decimal("0")

    for monthly_result in result[
        "monthly_results"
    ]:

        monthly_requirement = Decimal(
            str(
                monthly_result[
                    "preliminary_portfolio_requirement"
                ]
            )
        )

        if monthly_requirement > 0:

            expected_requirement += (
                monthly_requirement
            )

    actual = result[
        "annual_portfolio_requirement"
    ].quantize(
        Decimal("0.01")
    )

    expected = expected_requirement.quantize(
        Decimal("0.01")
    )

    assert actual == expected


def test_annual_withdrawal_selects_chris_401k():
    result = calculate_annual_withdrawal(
        2027,
        market_decline=False,
    )

    assert (
        result["recommended_source"]
        == "Chris 401(k)"
    )


def test_annual_withdrawal_has_positive_requirement():
    result = calculate_annual_withdrawal(
        2027,
        market_decline=False,
    )

    assert (
        result["annual_portfolio_requirement"]
        > Decimal("0")
    )