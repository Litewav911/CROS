from categorization import categorize


test_transactions = [
    ("ACME GROCERY STORE", -125.43),
    ("ELECTRIC COMPANY", -182.17),
    ("GAS STATION", -52.14),
    ("RESTAURANT ABC", -78.50),
    ("PAYROLL DEPOSIT", 4250.00),
    ("UNKNOWN PURCHASE", -25.00),
]


for description, amount in test_transactions:

    result = categorize(
        description,
        amount,
    )

    print(
        f"{description:25} "
        f"${amount:8.2f}  "
        f"{result.category:20} "
        f"{result.transaction_type}"
    )