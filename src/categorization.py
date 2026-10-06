import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DATABASE = Path(__file__).resolve().parent.parent / "data" / "db" / "cros.db"


@dataclass
class CategoryResult:
    category: str
    merchant: Optional[str] = None
    transaction_type: str = "expense"


def categorize(
    description: str,
    amount: float,
    database_path: Path = DATABASE,
) -> CategoryResult:

    return categorize_with_rules(
        description,
        amount,
        load_category_rules(database_path),
    )


def load_category_rules(
    database_path: Path = DATABASE,
) -> list[tuple[str, str, Optional[str], str]]:
    if not database_path.exists():
        return []

    database_uri = f"file:{database_path.as_posix()}?mode=ro"
    try:
        with closing(sqlite3.connect(database_uri, uri=True)) as connection:
            return connection.execute(
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
    except sqlite3.OperationalError:
        return []


def categorize_with_rules(
    description: str,
    amount: float,
    rules: list[tuple[str, str, Optional[str], str]],
) -> CategoryResult:
    normalized = description.upper()

    for (
        keyword,
        category,
        merchant,
        transaction_type,
    ) in rules:

        if keyword and keyword.upper() in normalized:

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
