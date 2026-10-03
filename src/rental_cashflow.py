from decimal import Decimal

from rental_properties import (
    RENTAL_PROPERTIES,
    total_monthly_rent,
    total_annual_property_expenses,
)


def monthly_rental_cashflow():
    """
    Calculate planned gross rental cash flow.

    This currently includes rent and known
    annual taxes/insurance. It does not yet
    include vacancies, repairs, management,
    capital expenditures, or income taxes.
    """

    gross_rent = total_monthly_rent()

    monthly_property_expenses = (
        total_annual_property_expenses()
        / Decimal("12")
    )

    net_rental_cashflow = (
        gross_rent
        - monthly_property_expenses
    )

    return {
        "gross_rent": gross_rent,
        "property_expenses": monthly_property_expenses,
        "net_rental_cashflow": net_rental_cashflow,
    }


def print_rental_cashflow():

    result = monthly_rental_cashflow()

    print()
    print("MONTHLY RENTAL CASH FLOW")
    print("=" * 45)

    print(
        f"{'Gross rent':25}"
        f"${result['gross_rent']:,.2f}"
    )

    print(
        f"{'Taxes + insurance':25}"
        f"${result['property_expenses']:,.2f}"
    )

    print("-" * 45)

    print(
        f"{'Net rental cash flow':25}"
        f"${result['net_rental_cashflow']:,.2f}"
    )


if __name__ == "__main__":
    print_rental_cashflow()