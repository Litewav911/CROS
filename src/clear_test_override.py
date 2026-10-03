import sqlite3

DATABASE = "data/db/cros.db"

connection = sqlite3.connect(DATABASE)

connection.execute(
    """
    UPDATE transactions
    SET
        category_override = NULL,
        merchant_override = NULL
    WHERE id = ?
    """,
    (1,),
)

connection.commit()

connection.close()

print("Test override removed.")