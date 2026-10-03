import sqlite3

connection = sqlite3.connect(
    "data/db/cros.db"
)

print()
print("SOURCE DOCUMENTS")
print("----------------")

for row in connection.execute(
    """
    SELECT
        id,
        filename,
        file_type,
        file_hash
    FROM source_documents
    """
):
    print(row)


print()
print("SOURCE TRANSACTIONS")
print("-------------------")

for row in connection.execute(
    """
    SELECT
        id,
        source_document_id,
        source_row_number,
        transaction_date,
        original_description,
        original_amount,
        raw_row_text,
        original_data
    FROM source_transactions
    ORDER BY id
    """
):
    print(row)


print()
print("CROS TRANSACTIONS")
print("-----------------")

for row in connection.execute(
    """
    SELECT
        id,
        source_transaction_id,
        transaction_date,
        description,
        amount,
        category,
        merchant
    FROM transactions
    ORDER BY id
    """
):
    print(row)


connection.close()