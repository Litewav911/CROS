from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RentalProperty:
    name: str
    monthly_rent: Decimal
    property_value: Decimal
    mortgage_balance: Decimal
    annual_taxes: Decimal
    annual_insurance: Decimal


RENTAL_PROPERTIES = [
    RentalProperty(
        name="1017 N Salisbury",
        monthly_rent=Decimal("1200"),
        property_value=Decimal("283000"),
        mortgage_balance=Decimal("0"),
        annual_taxes=Decimal("700.92"),
        annual_insurance=Decimal("1481.13"),
    ),

    RentalProperty(
        name="8 E 15th Ave",
        monthly_rent=Decimal("560"),
        property_value=Decimal("35000"),
        mortgage_balance=Decimal("0"),
        annual_taxes=Decimal("806.04"),
        annual_insurance=Decimal("359.84"),
    ),

    RentalProperty(
        name="805 Peach Orchard",
        monthly_rent=Decimal("1500"),
        property_value=Decimal("183000"),
        mortgage_balance=Decimal("0"),
        annual_taxes=Decimal("461.75"),
        annual_insurance=Decimal("674.23"),
    ),
]


def total_monthly_rent():
    return sum(
        property.monthly_rent
        for property in RENTAL_PROPERTIES
    )


def total_annual_rent():
    return (
        total_monthly_rent()
        * Decimal("12")
    )


def total_annual_taxes():
    return sum(
        property.annual_taxes
        for property in RENTAL_PROPERTIES
    )


def total_annual_insurance():
    return sum(
        property.annual_insurance
        for property in RENTAL_PROPERTIES
    )


def total_annual_property_expenses():
    return (
        total_annual_taxes()
        + total_annual_insurance()
    )


def print_rental_properties():

    print()
    print("CROS RENTAL PROPERTIES")
    print("=" * 75)

    total_value = Decimal("0")

    for property in RENTAL_PROPERTIES:

        print(
            f"{property.name:25}"
            f" Rent: ${property.monthly_rent:,.2f}"
            f"  Value: ${property.property_value:,.2f}"
        )

        total_value += property.property_value

    print("-" * 75)

    print(
        f"{'Total monthly rent':25}"
        f"${total_monthly_rent():,.2f}"
    )

    print(
        f"{'Total annual rent':25}"
        f"${total_annual_rent():,.2f}"
    )

    print(
        f"{'Annual taxes':25}"
        f"${total_annual_taxes():,.2f}"
    )

    print(
        f"{'Annual insurance':25}"
        f"${total_annual_insurance():,.2f}"
    )

    print(
        f"{'Annual property expenses':25}"
        f"${total_annual_property_expenses():,.2f}"
    )

    print(
        f"{'Total property value':25}"
        f"${total_value:,.2f}"
    )


if __name__ == "__main__":
    print_rental_properties()