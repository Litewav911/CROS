from decimal import Decimal

from retirement_engine import (
    RetirementEngineConfig,
    RetirementYearResult,
    run_retirement_engine,
)

from retirement_plan import (
    PLAN,
    build_base_taxable_income_schedule,
    build_roth_conversion_schedule,
    build_social_security_benefit_schedule,
    build_social_security_other_income_schedule,
)


START_YEAR = PLAN.retirement_start.year
END_YEAR = PLAN.retirement_end_year

ANNUAL_RETURN = PLAN.annual_return_assumption
MONTHLY_SPENDING_TARGET = PLAN.monthly_spending_target

CASH_RESERVE = Decimal("116819")

STARTING_BALANCES = {
    "Chris 401(k)": Decimal("752073"),
    "Stephanie 401(k)": Decimal("414214.61"),
    "Brokerage": Decimal("0"),
    "Roth IRA": Decimal("31387"),
    "HSA": Decimal("21464"),
    "Cash Reserve": CASH_RESERVE,
}


def build_real_retirement_config(
    monthly_spending_target: Decimal | None = None,
    annual_return_assumption: Decimal | None = None,
    annual_roth_conversion_target: Decimal | None = None,
) -> RetirementEngineConfig:
    """
    Build the current real-plan configuration.

    Plan assumptions come from retirement_plan.py.

    Starting account balances and the current cash reserve are
    explicit scenario inputs.

    This configuration intentionally keeps outside income
    separate from the portfolio-funded spending target because
    that is the behavior currently established by the tested
    retirement engine.
    """

    return RetirementEngineConfig(
        start_year=START_YEAR,
        end_year=END_YEAR,
        annual_return=(
            ANNUAL_RETURN
            if annual_return_assumption is None
            else Decimal(str(annual_return_assumption))
        ),
        monthly_spending_target=(
            MONTHLY_SPENDING_TARGET
            if monthly_spending_target is None
            else Decimal(str(monthly_spending_target))
        ),
        retirement_start=PLAN.retirement_start,
        prorate_first_retirement_year=True,
        initial_balances=STARTING_BALANCES.copy(),
        social_security_by_year=(
            build_social_security_benefit_schedule(
                start_year=START_YEAR,
                end_year=END_YEAR,
            )
        ),
        base_taxable_income_by_year=(
            build_base_taxable_income_schedule(
                start_year=START_YEAR,
                end_year=END_YEAR,
            )
        ),
        social_security_other_income_by_year=(
            build_social_security_other_income_schedule(
                start_year=START_YEAR,
                end_year=END_YEAR,
            )
        ),
        roth_conversions_by_year=(
            build_roth_conversion_schedule(
                start_year=START_YEAR,
                end_year=END_YEAR,
                annual_roth_conversion_target=(
                    annual_roth_conversion_target
                ),
            )
        ),
        conversion_tax_funded_from_withdrawal=True,
    )


def run_real_retirement_scenario(
    monthly_spending_target: Decimal | None = None,
    annual_return_assumption: Decimal | None = None,
    annual_roth_conversion_target: Decimal | None = None,
) -> list[RetirementYearResult]:
    """
    Run the current real 2027-2040 retirement scenario.
    """

    config = build_real_retirement_config(
        monthly_spending_target=monthly_spending_target,
        annual_return_assumption=annual_return_assumption,
        annual_roth_conversion_target=annual_roth_conversion_target,
    )

    return run_retirement_engine(
        config
    )


def _money(value: Decimal) -> str:
    """
    Format a Decimal as currency.
    """

    return f"${value:,.2f}"


def _outside_income(
    result: RetirementYearResult,
) -> Decimal:
    """
    Calculate total income received outside the portfolio.

    This is displayed separately for planning visibility.

    The retirement engine intentionally keeps the retirement
    spending target independent of outside income.
    """

    return (
        result.transaction_income
        + result.rental_income
        + result.social_security
    )


def _cash_shortfall(
    result: RetirementYearResult,
) -> Decimal:
    """
    Calculate any unmet portfolio cash requirement.
    """

    return max(
        Decimal("0"),
        result.cash_need_before_withdrawal
        - result.net_cash_from_withdrawal,
    )


def _print_year(
    result: RetirementYearResult,
) -> None:
    """
    Print one annual scenario row and its supporting detail.
    """

    outside_income = _outside_income(
        result
    )

    shortfall = _cash_shortfall(
        result
    )

    print(
        f"{result.year:<8}"
        f"{_money(result.planned_spending):>15}"
        f"{_money(outside_income):>18}"
        f"{_money(result.cash_need_before_withdrawal):>15}"
        f"{_money(result.gross_withdrawal):>15}"
        f"{_money(result.withdrawal_tax):>16}"
        f"{_money(result.conversion_amount):>15}"
        f"{_money(result.conversion_tax):>15}"
        f"{_money(result.ending_total):>20}"
    )

    if result.withdrawal_allocations:

        sources = ", ".join(
            f"{name}: {_money(amount)}"
            for name, amount
            in result.withdrawal_allocations.items()
        )

        print(
            f"         Withdrawal sources: "
            f"{sources}"
        )

    print(
        f"         Net cash from withdrawal: "
        f"{_money(result.net_cash_from_withdrawal)}"
    )

    if shortfall > Decimal("0"):

        print(
            f"         CASH SHORTFALL: "
            f"{_money(shortfall)}"
        )

    if result.market_decline:

        print(
            "         MARKET DECLINE: "
            "cash-reserve priority active"
        )


def _print_ending_balances(
    results: list[RetirementYearResult],
) -> None:
    """
    Print final account balances.
    """

    print()
    print("ENDING ACCOUNT BALANCES")
    print("-----------------------")

    if not results:
        return

    final_balances = results[-1].ending_balances

    for account_name, balance in final_balances.items():

        print(
            f"{account_name}: "
            f"{_money(balance)}"
        )


def _print_totals(
    results: list[RetirementYearResult],
) -> None:
    """
    Print cumulative scenario totals.
    """

    print()
    print("SCENARIO TOTALS")
    print("---------------")

    total_spending = sum(
        (
            result.planned_spending
            for result in results
        ),
        Decimal("0"),
    )

    total_outside_income = sum(
        (
            _outside_income(result)
            for result in results
        ),
        Decimal("0"),
    )

    total_withdrawals = sum(
        (
            result.gross_withdrawal
            for result in results
        ),
        Decimal("0"),
    )

    total_withdrawal_tax = sum(
        (
            result.withdrawal_tax
            for result in results
        ),
        Decimal("0"),
    )

    total_conversions = sum(
        (
            result.conversion_amount
            for result in results
        ),
        Decimal("0"),
    )

    total_conversion_tax = sum(
        (
            result.conversion_tax
            for result in results
        ),
        Decimal("0"),
    )

    total_shortfall = sum(
        (
            _cash_shortfall(result)
            for result in results
        ),
        Decimal("0"),
    )

    print(
        f"Total planned spending: "
        f"{_money(total_spending)}"
    )

    print(
        f"Total outside income: "
        f"{_money(total_outside_income)}"
    )

    print(
        f"Total gross withdrawals: "
        f"{_money(total_withdrawals)}"
    )

    print(
        f"Total withdrawal tax: "
        f"{_money(total_withdrawal_tax)}"
    )

    print(
        f"Total Roth conversions: "
        f"{_money(total_conversions)}"
    )

    print(
        f"Total Roth-conversion tax: "
        f"{_money(total_conversion_tax)}"
    )

    print(
        f"Total cash shortfall: "
        f"{_money(total_shortfall)}"
    )


def print_real_retirement_scenario(
    results: list[RetirementYearResult],
) -> None:
    """
    Print the real retirement scenario ledger.
    """

    print()
    print("CROS REAL RETIREMENT SCENARIO")
    print("=" * 175)

    print(
        f"Retirement start: "
        f"{PLAN.retirement_start}"
    )

    print(
        f"Spending target: "
        f"{_money(MONTHLY_SPENDING_TARGET)}/month"
    )

    print(
        f"Annual return assumption: "
        f"{ANNUAL_RETURN:.2%}"
    )

    print(
        f"Annual Roth conversion target: "
        f"{_money(PLAN.annual_roth_conversion_target)}"
    )

    print(
        f"Base taxable income assumption: "
        f"{_money(PLAN.annual_base_taxable_income)}"
    )

    print(
        f"Starting cash reserve: "
        f"{_money(CASH_RESERVE)}"
    )

    print()

    print(
        f"{'Year':<8}"
        f"{'Spending':>15}"
        f"{'Outside Income':>18}"
        f"{'Cash Need':>15}"
        f"{'Withdrawal':>15}"
        f"{'Withdrawal Tax':>16}"
        f"{'Roth Conv.':>15}"
        f"{'Conv. Tax':>15}"
        f"{'Ending Portfolio':>20}"
    )

    print("-" * 175)

    for result in results:

        _print_year(
            result
        )

    _print_ending_balances(
        results
    )

    _print_totals(
        results
    )


if __name__ == "__main__":

    results = run_real_retirement_scenario()

    print_real_retirement_scenario(
        results
    )
