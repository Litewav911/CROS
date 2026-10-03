import sqlite3

DATABASE = "data/db/cros.db"


def correct_transaction(
    transaction_id: int,
    category: str | None = None,
    merchant: str | None = None,
):
    connection = sqlite3.connect(DATABASE)

    transaction = connection.execute(
        """
        SELECT
            id,
            category,
            merchant,
            category_override,
            merchant_override
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()

    if transaction is None:
        connection.close()
        raise ValueError(
            f"Transaction {transaction_id} was not found."
        )

    current_category = transaction[1]
    current_merchant = transaction[2]

    new_category = (
        category
        if category is not None
        else transaction[3]
    )

    new_merchant = (
        merchant
        if merchant is not None
        else transaction[4]
    )

    connection.execute(
        """
        UPDATE transactions
        SET
            category_override = ?,
            merchant_override = ?
        WHERE id = ?
        """,
        (
            new_category,
            new_merchant,
            transaction_id,
        ),
    )

    connection.commit()

    updated = connection.execute(
        """
        SELECT
            id,
            description,
            category,
            category_override,
            merchant,
            merchant_override
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()

    connection.close()

    return updated


if __name__ == "__main__":

    result = correct_transaction(
        transaction_id=1,
        category="Groceries",
        merchant="Acme Grocery Store",
    )

    print("Transaction correction saved:")
    print(result)