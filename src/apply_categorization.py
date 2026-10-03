import sqlite3

from categorization import categorize


DATABASE = "data/db/cros.db"


def apply_categorization():
    connection = sqlite3.connect(DATABASE)

    transactions = connection.execute(
        """
        SELECT
            id,
            description,
            amount
        FROM transactions
        ORDER BY id
        """
    ).fetchall()

    updated = 0

    for transaction_id, description, amount in transactions:

        result = categorize(
            description,
            float(amount),
        )

        connection.execute(
            """
            UPDATE transactions
            SET
                category = ?,
                merchant = ?
            WHERE id = ?
            """,
            (
                result.category,
                result.merchant,
                transaction_id,
            ),
        )

        updated += 1

        print(
            f"{description:25} -> "
            f"{result.category:20} "
            f"({result.transaction_type})"
        )

    connection.commit()
    connection.close()

    print()
    print(
        f"Categorization complete: "
        f"{updated} transactions updated."
    )


if __name__ == "__main__":
    apply_categorization()