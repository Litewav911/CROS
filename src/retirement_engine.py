from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Mapping

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)
from rental_cashflow import monthly_rental_cashflow
from retirement_plan import PLAN
from retirement_accounts import get_account
from roth_conversion_integration import (
    calculate_roth_conversion,
)
from tax_engine import (
    NC_TAX_RATE,
    calculate_federal_tax_with_preferential_income_mfj_2026,
    calculate_flat_tax,
    calculate_social_security_taxable_benefit_mfj,
    calculate_withdrawal_tax_mfj_2026,
)


ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass
class RetirementEngineConfig:
    """
    Configuration for the stateful CROS retirement engine.
    """

    start_year: int = 2027
    end_year: int = 2040

    annual_return: Decimal = Decimal("0")

    monthly_spending_target: Decimal = (
        PLAN.monthly_spending_target
    )

    retirement_start: date = PLAN.retirement_start

    prorate_first_retirement_year: bool = True

    transaction_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    employment_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    payroll_tax_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    social_security_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    rental_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    base_taxable_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    preferential_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    nc_taxable_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    social_security_other_income_by_year: dict[
        int, Decimal
    ] = field(default_factory=dict)

    roth_conversions_by_year: dict[
        int,
        dict[str, Decimal],
    ] = field(default_factory=dict)

    market_declines_by_year: dict[int, bool] = field(
        default_factory=dict
    )

    initial_balances: dict[str, Decimal] | None = None

    conversion_tax_funded_from_withdrawal: bool = True


@dataclass
class RetirementYearResult:
    """
    Complete state transition for one retirement year.

    Outside income reduces the amount of retirement spending
    that must be funded by the investment portfolio.

    Roth conversions remain portfolio-neutral transfers.
    Conversion tax is treated separately as a cash requirement
    when conversion_tax_funded_from_withdrawal is enabled.
    """

    year: int

    beginning_balances: dict[str, Decimal]

    planned_spending: Decimal

    transaction_income: Decimal

    employment_income: Decimal

    payroll_tax: Decimal

    rental_income: Decimal

    social_security: Decimal

    outside_income: Decimal

    net_spending_need: Decimal

    conversion_amount: Decimal

    conversion_tax: Decimal

    base_income_tax: Decimal

    cash_need_before_withdrawal: Decimal

    gross_withdrawal: Decimal

    withdrawal_tax: Decimal

    net_cash_from_withdrawal: Decimal

    withdrawal_allocations: dict[str, Decimal]

    market_decline: bool

    ending_balances: dict[str, Decimal]

    beginning_total: Decimal

    investment_gain_total: Decimal

    ending_total: Decimal


def _to_decimal(value) -> Decimal:
    return Decimal(str(value))


def _days_in_year(year: int) -> int:
    start = date(year, 1, 1)
    end = date(year + 1, 1, 1)

    return (end - start).days


def _planned_spending_for_year(
    config: RetirementEngineConfig,
    year: int,
) -> Decimal:
    """
    Calculate annual planned spending.

    The first retirement year is prorated from the actual
    retirement date through December 31 when enabled.
    """

    monthly_target = _to_decimal(
        config.monthly_spending_target
    )

    annual_target = (
        monthly_target * Decimal("12")
    )

    if (
        not config.prorate_first_retirement_year
        or year != config.retirement_start.year
    ):
        return annual_target

    year_end = date(year, 12, 31)

    if config.retirement_start > year_end:
        return ZERO

    active_days = (
        year_end
        - config.retirement_start
    ).days + 1

    year_days = _days_in_year(year)

    return (
        annual_target
        * Decimal(active_days)
        / Decimal(year_days)
    )


def _default_rental_income(
    year: int,
) -> Decimal:
    """
    Rental properties operate throughout the year,
    independent of the retirement start date.

    The year argument is retained for interface consistency.
    """

    monthly = monthly_rental_cashflow()

    return (
        _to_decimal(
            monthly["net_rental_cashflow"]
        )
        * Decimal("12")
    )


def _get_year_income(
    config: RetirementEngineConfig,
    year: int,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:

    transaction_income = _to_decimal(
        config.transaction_income_by_year.get(
            year,
            ZERO,
        )
    )

    employment_income = _to_decimal(
        config.employment_income_by_year.get(year, ZERO)
    )

    if year in config.rental_income_by_year:

        rental_income = _to_decimal(
            config.rental_income_by_year[year]
        )

    else:

        rental_income = _default_rental_income(
            year
        )

    social_security = _to_decimal(
        config.social_security_by_year.get(
            year,
            ZERO,
        )
    )

    return (
        transaction_income,
        employment_income,
        rental_income,
        social_security,
    )


def _base_taxable_income(
    config: RetirementEngineConfig,
    year: int,
) -> Decimal:

    return _to_decimal(
        config.base_taxable_income_by_year.get(
            year,
            ZERO,
        )
    )


def _social_security_other_income(
    config: RetirementEngineConfig,
    year: int,
    base_taxable_income: Decimal,
) -> Decimal:
    """Return income used to calculate Social Security taxability."""
    return _to_decimal(
        config.social_security_other_income_by_year.get(
            year,
            base_taxable_income,
        )
    )


def _base_income_tax(
    federal_taxable_income: Decimal,
    nc_taxable_income: Decimal,
    social_security_benefits: Decimal,
    provisional_other_income: Decimal,
    preferential_income: Decimal = ZERO,
) -> Decimal:
    federal_tax = calculate_federal_tax_with_preferential_income_mfj_2026(
        federal_taxable_income,
        preferential_income,
        social_security_benefits,
        provisional_other_income,
    )
    nc_tax = calculate_flat_tax(nc_taxable_income, NC_TAX_RATE)
    return federal_tax + nc_tax


def _conversion_tax_for_account(
    year: int,
    source_account: str,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    social_security_benefits: Decimal = ZERO,
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = ZERO,
) -> Decimal:
    """
    Calculate incremental federal + NC tax for one
    Roth conversion.
    """

    conversion_amount = _to_decimal(
        conversion_amount
    )

    if conversion_amount <= ZERO:
        return ZERO

    account = get_account(
        source_account
    )

    if not account.roth_conversion_allowed:
        raise ValueError(
            f"Roth conversion is not allowed "
            f"from {source_account}."
        )

    result = calculate_roth_conversion(
        year=year,
        source_account=source_account,
        destination_account="Roth IRA",
        base_taxable_income=base_taxable_income,
        conversion_amount=conversion_amount,
        social_security_benefits=social_security_benefits,
        provisional_other_income=provisional_other_income,
        preferential_income=preferential_income,
    )

    return _to_decimal(
        result.total_tax
    )


def _total_conversion_tax(
    year: int,
    base_taxable_income: Decimal,
    roth_conversions: Mapping[str, Decimal],
    social_security_benefits: Decimal = ZERO,
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = ZERO,
) -> Decimal:
    """
    Calculate total tax for all requested Roth conversions.
    """

    total_tax = ZERO
    taxable_income_so_far = base_taxable_income
    provisional_income_so_far = (
        base_taxable_income
        if provisional_other_income is None
        else provisional_other_income
    )

    for source_account, conversion_amount in (
        roth_conversions.items()
    ):

        total_tax += _conversion_tax_for_account(
            year=year,
            source_account=source_account,
            base_taxable_income=taxable_income_so_far,
            conversion_amount=conversion_amount,
            social_security_benefits=social_security_benefits,
            provisional_other_income=provisional_income_so_far,
            preferential_income=preferential_income,
        )

        taxable_income_so_far += conversion_amount
        provisional_income_so_far += conversion_amount

    return total_tax


def _withdrawal_tax(
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    withdrawal_amount: Decimal,
    social_security_benefits: Decimal = ZERO,
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = ZERO,
) -> Decimal:
    """
    Calculate incremental tax caused by a traditional
    tax-deferred withdrawal.

    All federal and North Carolina tax calculations are
    delegated to the tax engine.
    """

    withdrawal_amount = _to_decimal(
        withdrawal_amount
    )

    if withdrawal_amount <= ZERO:
        return ZERO

    return calculate_withdrawal_tax_mfj_2026(
        base_taxable_income=base_taxable_income,
        conversion_amount=conversion_amount,
        withdrawal_amount=withdrawal_amount,
        social_security_benefits=social_security_benefits,
        provisional_other_income=provisional_other_income,
        preferential_income=preferential_income,
    )


def _gross_up_tax_deferred_withdrawal(
    net_needed: Decimal,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    maximum_available: Decimal,
    social_security_benefits: Decimal = ZERO,
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = ZERO,
) -> tuple[Decimal, Decimal]:
    """
    Find the gross tax-deferred withdrawal required to
    produce the requested net cash.
    """

    net_needed = _to_decimal(
        net_needed
    )

    maximum_available = _to_decimal(
        maximum_available
    )

    if net_needed <= ZERO:
        return ZERO, ZERO

    if maximum_available <= ZERO:
        return ZERO, ZERO

    def net_after_tax(
        gross: Decimal,
    ) -> tuple[Decimal, Decimal]:

        tax = _withdrawal_tax(
            base_taxable_income,
            conversion_amount,
            gross,
            social_security_benefits,
            provisional_other_income,
            preferential_income,
        )

        return (
            gross - tax,
            tax,
        )

    maximum_net, maximum_tax = net_after_tax(
        maximum_available
    )

    if maximum_net <= net_needed:
        return (
            maximum_available,
            maximum_tax,
        )

    low = ZERO
    high = maximum_available

    for _ in range(100):

        midpoint = (
            low + high
        ) / Decimal("2")

        net, _ = net_after_tax(
            midpoint
        )

        if net < net_needed:
            low = midpoint
        else:
            high = midpoint

    gross = high

    _, tax = net_after_tax(
        gross
    )

    return gross, tax


def _withdrawal_priority(
    market_decline: bool,
) -> list[str]:
    """
    Determine withdrawal priority.

    Normal:
        Chris 401(k)
        Brokerage
        Cash Reserve
        Stephanie 401(k)
        Roth IRA

    Market decline:
        Cash Reserve
        Chris 401(k)
        Brokerage
        Stephanie 401(k)
        Roth IRA
    """

    if market_decline:

        return [
            "Cash Reserve",
            "Chris 401(k)",
            "Brokerage",
            "Stephanie 401(k)",
            "Roth IRA",
        ]

    return [
        "Chris 401(k)",
        "Brokerage",
        "Cash Reserve",
        "Stephanie 401(k)",
        "Roth IRA",
    ]


def _account_available_after_growth(
    account_name: str,
    beginning_balances: Mapping[str, Decimal],
    annual_return: Decimal,
) -> Decimal:

    beginning = _to_decimal(
        beginning_balances.get(
            account_name,
            ZERO,
        )
    )

    return (
        beginning
        * (ONE + annual_return)
    )


def _allocate_withdrawal(
    net_needed: Decimal,
    beginning_balances: Mapping[str, Decimal],
    annual_return: Decimal,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    market_decline: bool,
    reserved_for_conversions: Mapping[str, Decimal] | None = None,
    social_security_benefits: Decimal = ZERO,
    provisional_other_income: Decimal | None = None,
    preferential_income: Decimal = ZERO,
) -> tuple[
    dict[str, Decimal],
    Decimal,
    Decimal,
    Decimal,
]:
    """
    Allocate required net cash across withdrawal priority.

    Tax-deferred withdrawals are grossed up for tax.

    Roth conversion amounts are reserved before withdrawal
    allocation.
    """

    if reserved_for_conversions is None:
        reserved_for_conversions = {}

    remaining_net = _to_decimal(
        net_needed
    )

    allocations: dict[str, Decimal] = {}

    total_gross = ZERO
    total_tax = ZERO
    total_net = ZERO
    taxable_withdrawals_so_far = ZERO

    for account_name in _withdrawal_priority(
        market_decline
    ):

        if remaining_net <= ZERO:
            break

        available = (
            _account_available_after_growth(
                account_name,
                beginning_balances,
                annual_return,
            )
        )

        reserved = _to_decimal(
            reserved_for_conversions.get(
                account_name,
                ZERO,
            )
        )

        available = max(
            ZERO,
            available - reserved,
        )

        if available <= ZERO:
            continue

        account = get_account(
            account_name
        )

        if not account.withdrawal_allowed:
            continue

        if account.tax_treatment == "tax_deferred":

            gross, tax = (
                _gross_up_tax_deferred_withdrawal(
                    remaining_net,
                    base_taxable_income
                    + taxable_withdrawals_so_far,
                    conversion_amount,
                    available,
                    social_security_benefits,
                    (
                        None
                        if provisional_other_income is None
                        else provisional_other_income
                        + taxable_withdrawals_so_far
                    ),
                    preferential_income,
                )
            )

            net = gross - tax
            taxable_withdrawals_so_far += gross

        else:

            gross = min(
                remaining_net,
                available,
            )

            tax = ZERO
            net = gross

        if gross <= ZERO:
            continue

        allocations[account_name] = (
            allocations.get(
                account_name,
                ZERO,
            )
            + gross
        )

        total_gross += gross
        total_tax += tax
        total_net += net

        remaining_net = max(
            ZERO,
            remaining_net - net,
        )

    return (
        allocations,
        total_gross,
        total_tax,
        total_net,
    )


def _cap_roth_conversions(
    requested: dict[str, Decimal],
    beginning_balances: Mapping[str, Decimal],
    annual_return: Decimal,
) -> dict[str, Decimal]:
    """
    Cap each requested Roth conversion at the source
    account's post-growth balance.
    """

    result: dict[str, Decimal] = {}

    for account_name, requested_amount in (
        requested.items()
    ):

        requested_amount = _to_decimal(
            requested_amount
        )

        if requested_amount < ZERO:
            raise ValueError(
                f"Roth conversion cannot be negative "
                f"for {account_name}."
            )

        account = get_account(
            account_name
        )

        if not account.roth_conversion_allowed:

            raise ValueError(
                f"Roth conversion is not allowed "
                f"from {account_name}."
            )

        available = (
            _account_available_after_growth(
                account_name,
                beginning_balances,
                annual_return,
            )
        )

        available = max(
            ZERO,
            available,
        )

        result[account_name] = min(
            requested_amount,
            available,
        )

    return result


def _validate_account_balances(
    balances: Mapping[str, Decimal],
) -> None:
    """
    Reject negative starting balances.
    """

    for account_name, balance in balances.items():

        balance = _to_decimal(
            balance
        )

        if balance < ZERO:
            raise ValueError(
                f"Account balance cannot be negative "
                f"for {account_name}."
            )


def _portfolio_cash_requirement(
    planned_spending: Decimal,
    outside_income: Decimal,
    conversion_tax: Decimal,
    conversion_tax_funded_from_withdrawal: bool,
    base_income_tax: Decimal = ZERO,
) -> Decimal:
    """
    Determine the portfolio withdrawal requirement.

    Formula:

        portfolio cash need =
            planned spending
            - outside income
            + tax on modeled income
            + conversion tax

    The result cannot be less than zero.
    """

    planned_spending = _to_decimal(
        planned_spending
    )

    outside_income = _to_decimal(
        outside_income
    )

    conversion_tax = _to_decimal(
        conversion_tax
    )

    base_income_tax = _to_decimal(base_income_tax)

    spending_need = max(
        ZERO,
        planned_spending
        - outside_income,
    )

    tax_need = (
        conversion_tax
        if conversion_tax_funded_from_withdrawal
        else ZERO
    )

    return max(
        ZERO,
        spending_need
        + base_income_tax
        + tax_need,
    )


def run_retirement_engine(
    config: RetirementEngineConfig,
) -> list[RetirementYearResult]:
    """
    Run the stateful CROS retirement engine.

    Each year's ending balances become the following year's
    beginning balances.

    Outside income reduces the portfolio-funded spending
    requirement.

    Tax on modeled ordinary income is included in the portfolio cash
    need. Roth conversion tax is added only when
    conversion_tax_funded_from_withdrawal is enabled.
    """

    if config.start_year > config.end_year:
        raise ValueError(
            "start_year cannot be greater than end_year."
        )

    annual_return = _to_decimal(
        config.annual_return
    )

    if annual_return < ZERO:
        raise ValueError(
            "annual_return cannot be negative."
        )

    if config.initial_balances is None:

        account_balances = (
            create_initial_account_balances()
        )

    else:

        account_balances = {
            name: _to_decimal(balance)
            for name, balance
            in config.initial_balances.items()
        }

    _validate_account_balances(
        account_balances
    )

    results: list[RetirementYearResult] = []

    for year in range(
        config.start_year,
        config.end_year + 1,
    ):

        beginning_balances = {
            name: _to_decimal(balance)
            for name, balance
            in account_balances.items()
        }

        planned_spending = (
            _planned_spending_for_year(
                config,
                year,
            )
        )

        (
            transaction_income,
            employment_income,
            rental_income,
            social_security,
        ) = _get_year_income(
            config,
            year,
        )

        payroll_tax = _to_decimal(
            config.payroll_tax_by_year.get(year, ZERO)
        )
        if payroll_tax < ZERO:
            raise ValueError("Payroll taxes cannot be negative.")

        outside_income = (
            transaction_income
            + employment_income
            + rental_income
            + social_security
            - payroll_tax
        )

        net_spending_need = max(
            ZERO,
            planned_spending
            - outside_income,
        )

        base_taxable_income = (
            _base_taxable_income(
                config,
                year,
            )
        )

        provisional_other_income = (
            _social_security_other_income(
                config,
                year,
                base_taxable_income,
            )
        )
        preferential_income = _to_decimal(
            config.preferential_income_by_year.get(year, ZERO)
        )

        nc_taxable_income = _to_decimal(
            config.nc_taxable_income_by_year.get(
                year,
                base_taxable_income,
            )
        )
        base_income_tax = _base_income_tax(
            federal_taxable_income=base_taxable_income,
            nc_taxable_income=nc_taxable_income,
            social_security_benefits=social_security,
            provisional_other_income=provisional_other_income,
            preferential_income=preferential_income,
        )

        market_decline = bool(
            config.market_declines_by_year.get(
                year,
                False,
            )
        )

        requested_conversions = {
            account: _to_decimal(amount)
            for account, amount
            in config.roth_conversions_by_year.get(
                year,
                {},
            ).items()
        }

        roth_conversions = _cap_roth_conversions(
            requested_conversions,
            beginning_balances,
            annual_return,
        )

        actual_conversion_amount = sum(
            roth_conversions.values(),
            ZERO,
        )

        conversion_tax = _total_conversion_tax(
            year=year,
            base_taxable_income=base_taxable_income,
            roth_conversions=roth_conversions,
            social_security_benefits=social_security,
            provisional_other_income=provisional_other_income,
            preferential_income=preferential_income,
        )

        cash_need = _portfolio_cash_requirement(
            planned_spending=planned_spending,
            outside_income=outside_income,
            conversion_tax=conversion_tax,
            conversion_tax_funded_from_withdrawal=(
                config.conversion_tax_funded_from_withdrawal
            ),
            base_income_tax=base_income_tax,
        )

        (
            withdrawals,
            gross_withdrawal,
            withdrawal_tax,
            net_cash_from_withdrawal,
        ) = _allocate_withdrawal(
            net_needed=cash_need,
            beginning_balances=beginning_balances,
            annual_return=annual_return,
            base_taxable_income=base_taxable_income,
            conversion_amount=actual_conversion_amount,
            market_decline=market_decline,
            reserved_for_conversions=roth_conversions,
            social_security_benefits=social_security,
            provisional_other_income=provisional_other_income,
            preferential_income=preferential_income,
        )

        projection = project_portfolio_year(
            year=year,
            account_balances=beginning_balances,
            annual_return=annual_return,
            withdrawals=withdrawals,
            roth_conversions=roth_conversions,
        )

        ending_balances = {
            account.account_name:
                account.ending_balance
            for account in projection.accounts
        }

        results.append(
            RetirementYearResult(
                year=year,
                beginning_balances=beginning_balances,
                planned_spending=planned_spending,
                transaction_income=transaction_income,
                employment_income=employment_income,
                payroll_tax=payroll_tax,
                rental_income=rental_income,
                social_security=social_security,
                outside_income=outside_income,
                net_spending_need=net_spending_need,
                conversion_amount=actual_conversion_amount,
                conversion_tax=conversion_tax,
                base_income_tax=base_income_tax,
                cash_need_before_withdrawal=cash_need,
                gross_withdrawal=gross_withdrawal,
                withdrawal_tax=withdrawal_tax,
                net_cash_from_withdrawal=net_cash_from_withdrawal,
                withdrawal_allocations=withdrawals,
                market_decline=market_decline,
                ending_balances=ending_balances,
                beginning_total=projection.beginning_total,
                investment_gain_total=projection.investment_gain_total,
                ending_total=projection.ending_total,
            )
        )

        account_balances = ending_balances

    return results


def print_retirement_engine(
    results: list[RetirementYearResult],
):
    """
    Print the annual CROS retirement-engine ledger.
    """

    print()
    print(
        "CROS RETIREMENT ENGINE"
    )
    print("=" * 160)

    print(
        f"{'Year':<8}"
        f"{'Spending':>15}"
        f"{'Outside Income':>17}"
        f"{'Income Tax':>15}"
        f"{'Cash Need':>15}"
        f"{'Withdrawal':>15}"
        f"{'Withdrawal Tax':>16}"
        f"{'Roth Conv.':>15}"
        f"{'Conv. Tax':>15}"
        f"{'Ending Portfolio':>20}"
    )

    print("-" * 160)

    for result in results:

        print(
            f"{result.year:<8}"
            f"${result.planned_spending:>13,.2f}"
            f"${result.outside_income:>15,.2f}"
            f"${result.base_income_tax:>13,.2f}"
            f"${result.cash_need_before_withdrawal:>13,.2f}"
            f"${result.gross_withdrawal:>13,.2f}"
            f"${result.withdrawal_tax:>14,.2f}"
            f"${result.conversion_amount:>13,.2f}"
            f"${result.conversion_tax:>13,.2f}"
            f"${result.ending_total:>18,.2f}"
        )

        if result.withdrawal_allocations:

            sources = ", ".join(
                f"{name}: ${amount:,.2f}"
                for name, amount
                in result.withdrawal_allocations.items()
            )

            print(
                f"         Withdrawal sources: "
                f"{sources}"
            )

        print(
            f"         Net cash from withdrawal: "
            f"${result.net_cash_from_withdrawal:,.2f}"
        )

        shortfall = (
            result.cash_need_before_withdrawal
            - result.net_cash_from_withdrawal
        )

        if shortfall > ZERO:

            print(
                f"         CASH SHORTFALL: "
                f"${shortfall:,.2f}"
            )

        if result.market_decline:

            print(
                "         MARKET DECLINE: "
                "cash-reserve priority active"
            )
