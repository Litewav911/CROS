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
    calculate_incremental_tax,
    FEDERAL_MFJ_2026_BRACKETS,
    NC_TAX_RATE,
)


ZERO = Decimal("0")


@dataclass
class RetirementEngineConfig:
    """
    Configuration for the stateful 2027-2040 retirement engine.

    The engine deliberately does not invent account balances,
    Social Security claiming dates, Roth conversion schedules,
    brokerage balances, or cash-reserve balances.

    Those items are supplied as explicit inputs.
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

    social_security_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    rental_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

    base_taxable_income_by_year: dict[int, Decimal] = field(
        default_factory=dict
    )

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
    """

    year: int

    beginning_balances: dict[str, Decimal]

    planned_spending: Decimal

    transaction_income: Decimal

    rental_income: Decimal

    social_security: Decimal

    conversion_amount: Decimal

    conversion_tax: Decimal

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
    Calculate the retirement spending target for a year.

    The first retirement year may be prorated from the actual
    retirement start date through December 31.

    All later years receive the full annual target.
    """

    monthly_target = _to_decimal(
        config.monthly_spending_target
    )

    annual_target = monthly_target * Decimal("12")

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
    Rental income is modeled independently of the retirement
    start date because the rental properties operate throughout
    the year.
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
) -> tuple[Decimal, Decimal, Decimal]:

    transaction_income = _to_decimal(
        config.transaction_income_by_year.get(
            year,
            ZERO,
        )
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


def _conversion_tax(
    year: int,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
) -> Decimal:
    """
    Calculate the incremental federal + NC tax generated
    by the Roth conversion.

    The existing CROS Roth conversion integration remains
    authoritative for this calculation.
    """

    if conversion_amount <= ZERO:
        return ZERO

    result = calculate_roth_conversion(
        year=year,
        source_account="Chris 401(k)",
        destination_account="Roth IRA",
        base_taxable_income=base_taxable_income,
        conversion_amount=conversion_amount,
    )

    return _to_decimal(
        result.total_tax
    )


def _withdrawal_tax(
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    withdrawal_amount: Decimal,
) -> Decimal:
    """
    Calculate the incremental tax caused by a traditional
    tax-deferred withdrawal.

    Conversion income is included first so the progressive
    tax brackets are respected.
    """

    if withdrawal_amount <= ZERO:
        return ZERO

    taxable_before_withdrawal = (
        base_taxable_income
        + conversion_amount
    )

    federal_tax = calculate_incremental_tax(
        taxable_before_withdrawal,
        withdrawal_amount,
        FEDERAL_MFJ_2026_BRACKETS,
    )

    nc_tax = (
        withdrawal_amount
        * NC_TAX_RATE
    )

    return (
        federal_tax
        + nc_tax
    )


def _gross_up_tax_deferred_withdrawal(
    net_needed: Decimal,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    maximum_available: Decimal,
) -> tuple[Decimal, Decimal]:

    """
    Find the gross traditional-account withdrawal needed
    to produce the requested net cash after incremental tax.

    Binary search is used because the federal tax is progressive.

    If the account cannot satisfy the entire net need, the
    maximum available amount is returned.
    """

    net_needed = _to_decimal(net_needed)

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
    Determine the account priority.

    Normal conditions:
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
        * (Decimal("1") + annual_return)
    )


def _allocate_withdrawal(
    net_needed: Decimal,
    beginning_balances: Mapping[str, Decimal],
    annual_return: Decimal,
    base_taxable_income: Decimal,
    conversion_amount: Decimal,
    market_decline: bool,
    reserved_for_conversions: Mapping[str, Decimal] | None = None,
) -> tuple[
    dict[str, Decimal],
    Decimal,
    Decimal,
    Decimal,
]:
    """
    Allocate a required net cash amount across the withdrawal
    priority.

    Traditional withdrawals are grossed up for their incremental
    federal and NC income tax.

    Conversion amounts are reserved before withdrawals so that
    a requested Roth conversion does not accidentally get consumed
    by the spending withdrawal.

    If the portfolio cannot satisfy the full cash requirement,
    the function returns the maximum available withdrawal instead
    of raising an exception.
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

        available -= reserved

        available = max(
            ZERO,
            available,
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
                    base_taxable_income,
                    conversion_amount,
                    available,
                )
            )

            net = gross - tax

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
    Cap each Roth conversion only against the source account's
    available balance after investment growth.

    Withdrawals are deliberately NOT subtracted here.

    The withdrawal allocator separately reserves the conversion
    amount so the two transactions can coexist.
    """

    result: dict[str, Decimal] = {}

    for account_name, requested_amount in requested.items():

        requested_amount = _to_decimal(
            requested_amount
        )

        if requested_amount < ZERO:
            raise ValueError(
                f"Roth conversion cannot be negative "
                f"for {account_name}."
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


def run_retirement_engine(
    config: RetirementEngineConfig,
) -> list[RetirementYearResult]:

    """
    Run the stateful CROS retirement engine.

    Each year's ending account balances become the next year's
    beginning balances.

    The engine currently models:

        - retirement spending
        - transaction income
        - rental income
        - Social Security
        - investment growth
        - Rule-of-55 withdrawal priority
        - market-decline cash-reserve priority
        - traditional-account withdrawal taxes
        - Roth conversions
        - Roth-conversion taxes
        - account-to-account balance carry-forward

    Important behavior:

        A requested Roth conversion reserves its source-account
        balance before spending withdrawals are allocated.

        If the portfolio cannot fund the complete annual spending
        target, the engine records the available withdrawal and
        continues the projection with depleted accounts.

        This allows the engine to produce the complete requested
        projection period even when a deliberately undersized
        test portfolio reaches zero.
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
            rental_income,
            social_security,
        ) = _get_year_income(
            config,
            year,
        )

        base_taxable_income = (
            _base_taxable_income(
                config,
                year,
            )
        )

        market_decline = (
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

        # --------------------------------------------------
        # Determine actual Roth conversion amounts.
        #
        # A conversion is capped only by the source account's
        # post-growth balance. Withdrawals are handled separately
        # and must respect these reserved conversion amounts.
        # --------------------------------------------------

        roth_conversions = _cap_roth_conversions(
            requested_conversions,
            beginning_balances,
            annual_return,
        )

        actual_conversion_amount = sum(
            roth_conversions.values(),
            ZERO,
        )

        conversion_tax = _conversion_tax(
            year,
            base_taxable_income,
            actual_conversion_amount,
        )

        # --------------------------------------------------
        # Determine cash required from the portfolio.
        #
        # Conversion tax is treated as a cash requirement when
        # configured to be funded from portfolio withdrawals.
        # --------------------------------------------------

        total_non_portfolio_income = (
            transaction_income
            + rental_income
            + social_security
        )

        cash_need = max(
            ZERO,
            planned_spending
            + (
                conversion_tax
                if config.conversion_tax_funded_from_withdrawal
                else ZERO
            )
            - total_non_portfolio_income,
        )

        # --------------------------------------------------
        # Allocate spending withdrawals.
        #
        # Roth conversions reserve their source-account dollars
        # before this allocation occurs.
        # --------------------------------------------------

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
        )

        # --------------------------------------------------
        # The portfolio is allowed to be underfunded.
        #
        # A shortfall is represented by:
        #
        #     net_cash_from_withdrawal < cash_need
        #
        # The engine continues into the next year with the
        # resulting account balances.
        #
        # This is intentional for long-horizon projection and
        # depletion testing.
        # --------------------------------------------------

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
                rental_income=rental_income,
                social_security=social_security,
                conversion_amount=actual_conversion_amount,
                conversion_tax=conversion_tax,
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

        # --------------------------------------------------
        # Carry state into the next year.
        # --------------------------------------------------

        account_balances = ending_balances

    return results


def print_retirement_engine(
    results: list[RetirementYearResult],
):
    """
    Print the annual 2027-2040 retirement-engine ledger.
    """

    print()
    print(
        "CROS RETIREMENT ENGINE"
    )
    print("=" * 145)

    print(
        f"{'Year':<8}"
        f"{'Spending':>15}"
        f"{'Income':>15}"
        f"{'Withdrawal':>15}"
        f"{'Withdrawal Tax':>16}"
        f"{'Roth Conv.':>15}"
        f"{'Conv. Tax':>15}"
        f"{'Ending Portfolio':>20}"
    )

    print("-" * 145)

    for result in results:

        total_income = (
            result.transaction_income
            + result.rental_income
            + result.social_security
        )

        print(
            f"{result.year:<8}"
            f"${result.planned_spending:>13,.2f}"
            f"${total_income:>13,.2f}"
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