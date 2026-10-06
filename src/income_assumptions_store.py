from contextlib import closing
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sqlite3

from database import DATABASE_PATH


def default_income_assumptions() -> dict[str, object]:
    return {
        "employment": {
            name: {
                "annual_salary": Decimal("0"),
                "last_work_date": None,
            }
            for name in ("Chris", "Stephanie")
        },
        "taxable_investments": {
            "annual_interest": Decimal("0"),
            "annual_ordinary_dividends": Decimal("0"),
            "annual_growth": Decimal("0"),
        },
        "rental": {
            "annual_other_expenses": Decimal("0"),
            "annual_depreciation": Decimal("0"),
        },
    }


def _encode_income_assumptions(
    income_assumptions: dict[str, object],
) -> str:
    serializable = {
        "employment": {
            name: {
                "annual_salary": str(source["annual_salary"]),
                "last_work_date": (
                    source["last_work_date"].isoformat()
                    if source["last_work_date"] is not None
                    else None
                ),
            }
            for name, source in income_assumptions["employment"].items()
        },
        "taxable_investments": {
            key: str(value)
            for key, value in income_assumptions[
                "taxable_investments"
            ].items()
        },
        "rental": {
            key: str(value)
            for key, value in income_assumptions["rental"].items()
        },
    }
    return json.dumps(serializable, sort_keys=True)


def _decode_income_assumptions(payload: str) -> dict[str, object]:
    values = json.loads(payload)
    for source in values["employment"].values():
        source["annual_salary"] = Decimal(source["annual_salary"])
        if source["last_work_date"] is not None:
            source["last_work_date"] = date.fromisoformat(
                source["last_work_date"]
            )
    for assumptions_key in ("taxable_investments", "rental"):
        values[assumptions_key] = {
            key: Decimal(value)
            for key, value in values[assumptions_key].items()
        }
    return values


def load_income_assumptions(
    database_path: Path = DATABASE_PATH,
) -> dict[str, object]:
    if not database_path.exists():
        return default_income_assumptions()

    with closing(sqlite3.connect(database_path)) as connection:
        try:
            row = connection.execute(
                "SELECT value FROM cros_settings WHERE key = ?",
                ("income_assumptions",),
            ).fetchone()
        except sqlite3.OperationalError as error:
            if "no such table" in str(error).lower():
                return default_income_assumptions()
            raise

    if row is None:
        return default_income_assumptions()
    return _decode_income_assumptions(row[0])


def save_income_assumptions(
    income_assumptions: dict[str, object],
    database_path: Path = DATABASE_PATH,
) -> None:
    payload = _encode_income_assumptions(income_assumptions)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cros_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO cros_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            ("income_assumptions", payload),
        )
        connection.commit()
