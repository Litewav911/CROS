from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryResult:
    category: str
    merchant: Optional[str] = None
    transaction_type: str = "expense"


RULES = [
    {
        "keywords": ["GROCERY", "WALMART", "FOOD LION", "KROGER"],
        "category": "Groceries",
        "transaction_type": "expense",
    },
    {
        "keywords": ["ELECTRIC", "DUKE ENERGY", "POWER"],
        "category": "Utilities",
        "transaction_type": "expense",
    },
    {
        "keywords": ["GAS STATION", "SHELL", "EXXON", "BP"],
        "category": "Fuel",
        "transaction_type": "expense",
    },
    {
        "keywords": ["RESTAURANT", "MCDONALD", "WENDY", "CHICK-FIL-A"],
        "category": "Dining",
        "transaction_type": "expense",
    },
    {
        "keywords": ["PAYROLL", "DIRECT DEPOSIT", "SALARY"],
        "category": "Income",
        "transaction_type": "income",
    },
]


def categorize(description: str, amount: float) -> CategoryResult:
    """
    Determine the category and transaction type
    from the transaction description.
    """

    normalized = description.upper()

    for rule in RULES:
        for keyword in rule["keywords"]:
            if keyword in normalized:

                return CategoryResult(
                    category=rule["category"],
                    merchant=description.title(),
                    transaction_type=rule["transaction_type"],
                )

    # Fallback based on amount.
    if amount > 0:
        return CategoryResult(
            category="Other Income",
            merchant=description.title(),
            transaction_type="income",
        )

    return CategoryResult(
        category="Uncategorized",
        merchant=description.title(),
        transaction_type="expense",
    )