import sqlite3

from transaction_service import get_effective_transaction


DATABASE = "data/db/cros.db"


connection = sqlite3.connect(DATABASE)


print()
print("BEFORE OVERRIDE")
print("----------------")

row = connection.execute(
    """
    SELECT
        id,
        description,
        category,
        category_override,
        merchant,
        merchant_override
    FROM transactions
    WHERE id = 1
    """
).fetchone()

print(row)


print()
print("SETTING MANUAL CORRECTION")
print("--------------------------")

connection.execute(
    """
    UPDATE transactions
    SET
        category_override = ?,
        merchant_override = ?
    WHERE id = ?
    """,
    (
        "Groceries - Test Override",
        "Acme Grocery - Test Override",
        1,
    ),
)

connection.commit()
connection.close()


print()
print("EFFECTIVE TRANSACTION")
print("----------------------")

effective = get_effective_transaction(1)

print(effective)


print()
print("RESULT")

if (
    effective["category"]
    == "Groceries - Test Override"
    and
    effective["merchant"]
    == "Acme Grocery - Test Override"
):
    print("PASS: Manual overrides are being used.")

else:
    print("FAIL: Manual overrides are not being used.")


print()
print("SOURCE DATA CHECK")
print("------------------")

connection = sqlite3.connect(DATABASE)

source = connection.execute(
    """
    SELECT
        original_description,
        original_amount,
        raw_row_text
    FROM source_transactions
    WHERE id = 1
    """
).fetchone()

connection.close()

print(source)

if (
    source[0] == "ACME GROCERY STORE"
    and
    float(source[1]) == -125.43
):
    print(
        "PASS: Original source data remains unchanged."
    )
else:
    print(
        "FAIL: Original source data was changed."
    )