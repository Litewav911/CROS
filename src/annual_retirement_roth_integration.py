from decimal import Decimal

from annual_withdrawal import (
    calculate_annual_withdrawal,
)

from monthly_spending import (
    get_month_summary,
)

from rental_cashflow import (
    monthly_rental_cashflow,
)

from portfolio_projection import (
    create_initial_account_balances,
    project_portfolio_year,
)

from roth_conversion_integration import (
    calculate_roth_conversion,
)


def calculate_annual_retirement_roth(
    year: int,
    annual_return: Decimal = Decimal("0"),
    base_taxable_income: Decimal = Decimal("0"),
    roth_conversion_amount: Decimal = Decimal("0"),
    market_decline: bool = False,
):
    """
    Integrate the annual retirement cash-flow engine,
    Roth conversion tax engine, and portfolio projection.

    This function coordinates:

        1. Annual spending
        2. Transaction income
        3. Rental cash flow
        4. Portfolio withdrawal requirement
        5. Withdrawal source
        6. Roth conversion
        7. Federal conversion tax
        8. NC conversion tax
        9. Portfolio projection
       10. Ending account balances

    Roth conversion taxes are tracked separately from
    the portfolio transfer.

    The gross Roth conversion moves from the traditional
    account to the Roth account and therefore does not
    reduce total portfolio value.
    """

    year = int(year)
    annual_return = Decimal(
        str(annual_return)
    )
    base_taxable_income = Decimal(
        str(base_taxable_income)
    )
    roth_conversion_amount = Decimal(
        str(roth_conversion_amount)
    )

    if annual_return < 0:
        raise ValueError(
            "Annual return cannot be negative."
        )

    if base_taxable_income < 0:
        raise ValueError(
            "Base taxable income cannot be negative."
        )

    if roth_conversion_amount < 0:
        raise ValueError(
            "Roth conversion amount cannot be negative."
        )

    # --------------------------------------------------
    # Annual withdrawal engine
    # --------------------------------------------------

    annual_withdrawal = (
        calculate_annual_withdrawal(
            year=year,
            market_decline=market_decline,
        )
    )

    portfolio_requirement = Decimal(
        str(
            annual_withdrawal[
                "annual_portfolio_requirement"
            ]
        )
    )

    withdrawal_source = (
        annual_withdrawal[
            "recommended_source"
        ]
    )

    # --------------------------------------------------
    # Annual cash-flow totals
    #
    # These are calculated from the authoritative
    # monthly spending and rental engines.
    # --------------------------------------------------

    annual_spending = Decimal("0")
    transaction_income = Decimal("0")
    rental_income = Decimal("0")

    for month in range(1, 13):

        summary = get_month_summary(
            year,
            month,
        )

        rental = monthly_rental_cashflow()

        annual_spending += Decimal(
            str(
                summary["total_spending"]
            )
        )

        transaction_income += Decimal(
            str(
                summary["total_income"]
            )
        )

        rental_income += Decimal(
            str(
                rental["net_rental_cashflow"]
            )
        )

    # --------------------------------------------------
    # Determine portfolio withdrawal
    # --------------------------------------------------

    if (
        withdrawal_source == "None"
        or portfolio_requirement <= 0
    ):

        withdrawals = {}

    else:

        withdrawals = {
            withdrawal_source:
                portfolio_requirement
        }

    # --------------------------------------------------
    # Roth conversion tax calculation
    # --------------------------------------------------

    conversion = calculate_roth_conversion(
        year=year,
        source_account="Chris 401(k)",
        destination_account="Roth IRA",
        base_taxable_income=base_taxable_income,
        conversion_amount=roth_conversion_amount,
    )

    # --------------------------------------------------
    # Portfolio projection
    # --------------------------------------------------

    starting_balances = (
        create_initial_account_balances()
    )

    projection = project_portfolio_year(
        year=year,
        account_balances=starting_balances,
        annual_return=annual_return,
        withdrawals=withdrawals,
        roth_conversions={
            "Chris 401(k)":
                roth_conversion_amount,
        },
    )

    ending_balances = {
        account.account_name:
            account.ending_balance
        for account in projection.accounts
    }

    # --------------------------------------------------
    # Return the complete integrated result
    # --------------------------------------------------

    return {
        "year": year,

        "annual_spending":
            annual_spending,

        "transaction_income":
            transaction_income,

        "rental_income":
            rental_income,

        "portfolio_requirement":
            portfolio_requirement,

        "withdrawal_source":
            withdrawal_source,

        "withdrawals":
            withdrawals,

        "roth_conversion":
            conversion,

        "projection":
            projection,

        "ending_balances":
            ending_balances,
    }


def print_annual_retirement_roth(
    result,
):
    """
    Print a readable annual retirement/Roth
    integration result.
    """

    year = result["year"]
    conversion = result["roth_conversion"]
    projection = result["projection"]
    ending_balances = result["ending_balances"]

    print()
    print(
        f"ANNUAL RETIREMENT / ROTH: {year}"
    )
    print("=" * 70)

    print()
    print("RETIREMENT CASH FLOW")
    print("--------------------")

    print(
        f"{'Annual spending':35}"
        f"${result['annual_spending']:,.2f}"
    )

    print(
        f"{'Transaction income':35}"
        f"${result['transaction_income']:,.2f}"
    )

    print(
        f"{'Rental income':35}"
        f"${result['rental_income']:,.2f}"
    )

    print(
        f"{'Portfolio requirement':35}"
        f"${result['portfolio_requirement']:,.2f}"
    )

    print(
        f"{'Withdrawal source':35}"
        f"{result['withdrawal_source']}"
    )

    print()
    print("ROTH CONVERSION")
    print("----------------")

    print(
        f"{'Conversion amount':35}"
        f"${conversion.conversion_amount:,.2f}"
    )

    print(
        f"{'Federal tax':35}"
        f"${conversion.federal_tax:,.2f}"
    )

    print(
        f"{'NC tax':35}"
        f"${conversion.nc_tax:,.2f}"
    )

    print(
        f"{'Total conversion tax':35}"
        f"${conversion.total_tax:,.2f}"
    )

    print(
        f"{'Net Roth amount':35}"
        f"${conversion.net_roth_amount:,.2f}"
    )

    print()
    print("PORTFOLIO")
    print("---------")

    print(
        f"{'Beginning portfolio':35}"
        f"${projection.beginning_total:,.2f}"
    )

    print(
        f"{'Investment gain':35}"
        f"${projection.investment_gain_total:,.2f}"
    )

    print(
        f"{'Portfolio withdrawal':35}"
        f"${projection.withdrawal_total:,.2f}"
    )

    print(
        f"{'Roth conversion':35}"
        f"${projection.roth_conversion_total:,.2f}"
    )

    print(
        f"{'Ending portfolio':35}"
        f"${projection.ending_total:,.2f}"
    )

    print()
    print("ACCOUNT BALANCES")
    print("----------------")

    for account_name in (
        "Chris 401(k)",
        "Stephanie 401(k)",
        "Roth IRA",
        "HSA",
        "Cash Reserve",
        "Brokerage",
    ):

        if account_name in ending_balances:

            print(
                f"{account_name:25}"
                f"${ending_balances[account_name]:,.2f}"
            )