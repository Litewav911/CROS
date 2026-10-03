from dataclasses import dataclass
from decimal import Decimal

from retirement_accounts import get_account


@dataclass
class AnnualAccountProjection:
    """
    Represents one retirement account's balance
    during one projection year.
    """

    year: int
    account_name: str
    beginning_balance: Decimal
    investment_gain: Decimal
    withdrawal: Decimal
    roth_conversion: Decimal
    ending_balance: Decimal


def project_account_year(
    year: int,
    account_name: str,
    beginning_balance: Decimal,
    investment_gain: Decimal = Decimal("0"),
    withdrawal: Decimal = Decimal("0"),
    roth_conversion: Decimal = Decimal("0"),
) -> AnnualAccountProjection:
    """
    Calculate the ending balance for one account
    during one year.

    Taxes and investment-return assumptions are
    intentionally handled elsewhere.
    """

    beginning_balance = Decimal(
        str(beginning_balance)
    )

    investment_gain = Decimal(
        str(investment_gain)
    )

    withdrawal = Decimal(
        str(withdrawal)
    )

    roth_conversion = Decimal(
        str(roth_conversion)
    )

    if investment_gain < 0:
        raise ValueError(
            "Investment gain cannot be negative. "
            "Use investment_loss for negative returns."
        )

    if withdrawal < 0:
        raise ValueError(
            "Withdrawal cannot be negative."
        )

    if roth_conversion < 0:
        raise ValueError(
            "Roth conversion cannot be negative."
        )

    ending_balance = (
        beginning_balance
        + investment_gain
        - withdrawal
        - roth_conversion
    )

    return AnnualAccountProjection(
        year=year,
        account_name=account_name,
        beginning_balance=beginning_balance,
        investment_gain=investment_gain,
        withdrawal=withdrawal,
        roth_conversion=roth_conversion,
        ending_balance=ending_balance,
    )


def get_starting_balance(
    account_name: str,
) -> Decimal:
    """
    Retrieve the modeled starting balance from
    the retirement account model.
    """

    account = get_account(
        account_name
    )

    return Decimal(
        str(account.balance)
    )


def print_account_projection(
    projection: AnnualAccountProjection,
):

    print()
    print(
        f"ACCOUNT PROJECTION: "
        f"{projection.account_name}"
    )

    print("=" * 65)

    print(
        f"{'Year':25}"
        f"{projection.year}"
    )

    print(
        f"{'Beginning balance':25}"
        f"${projection.beginning_balance:,.2f}"
    )

    print(
        f"{'Investment gain':25}"
        f"${projection.investment_gain:,.2f}"
    )

    print(
        f"{'Withdrawal':25}"
        f"${projection.withdrawal:,.2f}"
    )

    print(
        f"{'Roth conversion':25}"
        f"${projection.roth_conversion:,.2f}"
    )

    print(
        f"{'Ending balance':25}"
        f"${projection.ending_balance:,.2f}"
    )


if __name__ == "__main__":

    starting_balance = get_starting_balance(
        "Chris 401(k)"
    )

    projection = project_account_year(
        year=2027,
        account_name="Chris 401(k)",
        beginning_balance=starting_balance,
        investment_gain=Decimal("50000"),
        withdrawal=Decimal("60000"),
        roth_conversion=Decimal("80000"),
    )

    print_account_projection(
        projection
    )