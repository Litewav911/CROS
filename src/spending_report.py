import sqlite3
from collections import defaultdict
from decimal import Decimal


DATABASE = "data/db/cros.db"


def get_monthly_spending(year: int, month: int):
    """
    Return monthly spending using effective categories.

    Manual category overrides take precedence over
    automatic categories.
    """

    connection = sqlite3.connect(DATABASE)

    rows = connection.execute(
        """
        SELECT
            transaction_date,
            amount,
            category,
            category_override
        FROM transactions
        WHERE
            strftime('%Y', transaction_date) = ?
            AND strftime('%m', transaction_date) = ?
            AND amount < 0
        ORDER BY transaction_date
        """,
        (
            str(year),
            f"{month:02d}",
        ),
    ).fetchall()

    connection.close()

    spending = defaultdict(Decimal)

    for (
        transaction_date,
        amount,
        category,
        category_override,
    ) in rows:

        effective_category = (
            category_override
            or category
            or "Uncategorized"
        )

        spending[effective_category] += Decimal(
            str(abs(amount))
        )

    return dict(spending)


def get_monthly_income(year: int, month: int):
    """
    Return total positive cash inflows for the month.
    """

    connection = sqlite3.connect(DATABASE)

    result = connection.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE
            strftime('%Y', transaction_date) = ?
            AND strftime('%m', transaction_date) = ?
            AND amount > 0
        """,
        (
            str(year),
            f"{month:02d}",
        ),
    ).fetchone()

    connection.close()

    return Decimal(str(result[0]))


def print_monthly_report(year: int, month: int):

    spending = get_monthly_spending(
        year,
        month,
    )

    income = get_monthly_income(
        year,
        month,
    )

    total_spending = sum(
        spending.values(),
        Decimal("0"),
    )

    print()
    print(
        f"{year}-{month:02d} MONTHLY SPENDING"
    )
    print(
        "-------------------------"
    )

    for category, amount in sorted(
        spending.items()
    ):
        print(
            f"{category:25} "
            f"${amount:,.2f}"
        )

    print(
        "-------------------------"
    )

    print(
        f"{'Total Spending':25} "
        f"${total_spending:,.2f}"
    )

    print(
        f"{'Total Income':25} "
        f"${income:,.2f}"
    )

    print()


if __name__ == "__main__":

    print_monthly_report(
        2027,
        1,
    )