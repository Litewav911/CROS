import sqlite3
from decimal import Decimal


DATABASE = "data/db/cros.db"


def get_month_summary(year: int, month: int):
    """
    Calculate the actual spending and income for a month.

    Category overrides take precedence over automatic categories.
    """

    connection = sqlite3.connect(DATABASE)

    rows = connection.execute(
        """
        SELECT
            amount,
            category,
            category_override
        FROM transactions
        WHERE
            strftime('%Y', transaction_date) = ?
            AND strftime('%m', transaction_date) = ?
        """,
        (
            str(year),
            f"{month:02d}",
        ),
    ).fetchall()

    connection.close()

    total_spending = Decimal("0")
    total_income = Decimal("0")

    categories = {}

    for amount, category, category_override in rows:

        amount = Decimal(str(amount))

        effective_category = (
            category_override
            or category
            or "Uncategorized"
        )

        if amount < 0:

            spending_amount = abs(amount)

            total_spending += spending_amount

            categories[effective_category] = (
                categories.get(
                    effective_category,
                    Decimal("0"),
                )
                + spending_amount
            )

        elif amount > 0:

            total_income += amount

    return {
        "year": year,
        "month": month,
        "total_spending": total_spending,
        "total_income": total_income,
        "categories": categories,
    }


def print_summary(year: int, month: int):

    summary = get_month_summary(
        year,
        month,
    )

    print()
    print(
        f"MONTH SUMMARY: "
        f"{year}-{month:02d}"
    )
    print("=" * 40)

    print(
        f"Total Spending: "
        f"${summary['total_spending']:,.2f}"
    )

    print(
        f"Total Income:   "
        f"${summary['total_income']:,.2f}"
    )

    print()
    print("SPENDING BY CATEGORY")
    print("---------------------")

    for category, amount in sorted(
        summary["categories"].items()
    ):
        print(
            f"{category:25}"
            f"${amount:,.2f}"
        )


if __name__ == "__main__":

    print_summary(
        2027,
        1,
    )