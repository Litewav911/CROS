import sqlite3

DATABASE = "data/db/cros.db"


connection = sqlite3.connect(DATABASE)

columns = {
    row[1]
    for row in connection.execute(
        "PRAGMA table_info(transactions)"
    ).fetchall()
}


if "category_override" not in columns:
    connection.execute(
        """
        ALTER TABLE transactions
        ADD COLUMN category_override TEXT
        """
    )

    print("Added category_override column.")
else:
    print("category_override already exists.")


if "merchant_override" not in columns:
    connection.execute(
        """
        ALTER TABLE transactions
        ADD COLUMN merchant_override TEXT
        """
    )

    print("Added merchant_override column.")
else:
    print("merchant_override already exists.")


connection.commit()


print()
print("TRANSACTIONS TABLE")
print("------------------")

for row in connection.execute(
    "PRAGMA table_info(transactions)"
):
    print(row)


connection.close()

print()
print("Migration complete.")