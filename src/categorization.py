import sqlite3
from dataclasses import dataclass
from typing import Optional


DATABASE = "data/db/cros.db"


@dataclass
class CategoryResult:
    category: str
    merchant: Optional[str] = None
    transaction_type: str = "expense"


def categorize(
    description: str,
    amount: float,
) -> CategoryResult:

    normalized = description.upper()

    connection = sqlite3.connect(DATABASE)

    rules = connection.execute(
        """
        SELECT
            keyword,
            category,
            merchant,
            transaction_type
        FROM category_rules
        WHERE active = 1
        ORDER BY priority ASC, id ASC
        """
    ).fetchall()

    connection.close()

    for (
        keyword,
        category,
        merchant,
        transaction_type,
    ) in rules:

        if keyword.upper() in normalized:

            return CategoryResult(
                category=category,
                merchant=merchant or description.title(),
                transaction_type=transaction_type,
            )

    if amount > 0:

        return CategoryResult(
            category="Other Income",
            merchant=description.title(),
            transaction_type="income",
        )

    return CategoryResult(
        category="Uncategorized",
        merchant=description.title(),
        transaction_type="expense",
    )