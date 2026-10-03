import sqlite3

DATABASE = "data/db/cros.db"

connection = sqlite3.connect(DATABASE)

# Show the source record BEFORE modification.
print()
print("SOURCE BEFORE")
print("--------------")

source_before = connection.execute(
    """
    SELECT
        id,
        original_description,
        original_amount,
        raw_row_text,
        original_data
    FROM source_transactions
    WHERE id = 1
    """
).fetchone()

print(source_before)


# Modify ONLY the CROS interpretation.
connection.execute(
    """
    UPDATE transactions
    SET
        category = ?,
        merchant = ?
    WHERE id = ?
    """,
    (
        "Groceries",
        "ACME Grocery Store",
        1,
    ),
)

connection.commit()


# Show the CROS record AFTER modification.
print()
print("CROS AFTER")
print("----------")

cros_after = connection.execute(
    """
    SELECT
        id,
        source_transaction_id,
        description,
        amount,
        category,
        merchant
    FROM transactions
    WHERE id = 1
    """
).fetchone()

print(cros_after)


# Show the ORIGINAL source record again.
print()
print("SOURCE AFTER")
print("-------------")

source_after = connection.execute(
    """
    SELECT
        id,
        original_description,
        original_amount,
        raw_row_text,
        original_data
    FROM source_transactions
    WHERE id = 1
    """
).fetchone()

print(source_after)


# Verify that the source was not changed.
if source_before == source_after:
    print()
    print("PASS: Original source transaction was not changed.")
else:
    print()
    print("FAIL: Original source transaction was changed.")


connection.close()