import sqlite3


DATABASE = "data/db/cros.db"


RULES = [
    ("GROCERY", "Groceries", None, "expense", 100),
    ("WALMART", "Groceries", "Walmart", "expense", 100),
    ("FOOD LION", "Groceries", "Food Lion", "expense", 100),

    ("ELECTRIC", "Utilities", None, "expense", 100),
    ("DUKE ENERGY", "Utilities", "Duke Energy", "expense", 90),
    ("POWER", "Utilities", None, "expense", 100),

    ("GAS STATION", "Fuel", None, "expense", 100),
    ("SHELL", "Fuel", "Shell", "expense", 100),
    ("EXXON", "Fuel", "Exxon", "expense", 100),
    ("BP", "Fuel", "BP", "expense", 100),

    ("RESTAURANT", "Dining", None, "expense", 100),
    ("MCDONALD", "Dining", "McDonald's", "expense", 100),
    ("WENDY", "Dining", "Wendy's", "expense", 100),

    ("PAYROLL", "Income", None, "income", 50),
    ("DIRECT DEPOSIT", "Income", None, "income", 50),
    ("SALARY", "Income", None, "income", 50),
]


connection = sqlite3.connect(DATABASE)

connection.executemany(
    """
    INSERT INTO category_rules
    (
        keyword,
        category,
        merchant,
        transaction_type,
        priority,
        active
    )
    VALUES (?, ?, ?, ?, ?, 1)
    """,
    RULES,
)

connection.commit()

count = connection.execute(
    "SELECT COUNT(*) FROM category_rules"
).fetchone()[0]

connection.close()

print(
    f"Category rules created successfully: {count}"
)