import sqlite3
from sqlalchemy import update
from sqlalchemy.engine import Engine
from typing import Optional

from database import engine
from models import Transaction

DATABASE = "data/db/cros.db"


def get_effective_transaction(
    transaction_id: int,
) -> Optional[dict]:
    """
    Return a transaction using manual overrides when present.
    """

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    row = connection.execute(
        """
        SELECT
            id,
            source_transaction_id,
            account_id,
            transaction_date,
            description,
            amount,
            category,
            category_override,
            merchant,
            merchant_override,
            notes
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "source_transaction_id":
            row["source_transaction_id"],
        "account_id":
            row["account_id"],
        "transaction_date":
            row["transaction_date"],
        "description":
            row["description"],
        "amount":
            row["amount"],

        "category":
            row["category_override"]
            or row["category"],

        "merchant":
            row["merchant_override"]
            or row["merchant"],

        "notes":
            row["notes"],
    }


def update_category_override(
    transaction_id: int,
    category_override: str | None,
    database_engine: Engine = engine,
) -> None:
    """Set or clear a transaction's manual category override."""
    if category_override is not None and not category_override.strip():
        raise ValueError("Category cannot be empty.")

    with database_engine.begin() as connection:
        result = connection.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(category_override=category_override)
        )
        if result.rowcount != 1:
            raise LookupError(f"Transaction not found: {transaction_id}")
