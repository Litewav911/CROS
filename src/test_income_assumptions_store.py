from contextlib import contextmanager
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import tempfile

from database import DATABASE_PATH
from income_assumptions_store import (
    _decode_income_assumptions,
    default_income_assumptions,
    load_income_assumptions,
    save_income_assumptions,
)


@contextmanager
def _temporary_database_path():
    with tempfile.NamedTemporaryFile(
        prefix="income-assumptions-",
        suffix=".sqlite",
        dir=DATABASE_PATH.parent,
        delete=False,
    ) as temporary_database:
        database_path = Path(temporary_database.name)
    database_path.unlink()

    try:
        yield database_path
    finally:
        database_path.unlink(missing_ok=True)


def test_load_income_assumptions_returns_defaults_without_saved_settings():
    with _temporary_database_path() as database_path:
        assert load_income_assumptions(database_path) == (
            default_income_assumptions()
        )
        assert not database_path.exists()


def test_saved_income_assumptions_reload_with_decimal_and_date_types():
    with _temporary_database_path() as database_path:
        assumptions = {
            "employment": {
                "Chris": {
                    "annual_salary": Decimal("125000.50"),
                    "last_work_date": date(2027, 3, 26),
                },
                "Stephanie": {
                    "annual_salary": Decimal("0"),
                    "last_work_date": None,
                },
            },
            "taxable_investments": {
                "annual_interest": Decimal("1200.25"),
                "annual_ordinary_dividends": Decimal("3400"),
                "annual_qualified_dividends": Decimal("1200"),
                "annual_net_long_term_capital_gains": Decimal("2500"),
                "annual_growth": Decimal("0.025"),
            },
            "rental": {
                "annual_other_expenses": Decimal("2500"),
                "annual_depreciation": Decimal("6500"),
            },
        }

        save_income_assumptions(assumptions, database_path)

        assert load_income_assumptions(database_path) == assumptions


def test_saving_income_assumptions_replaces_previous_values():
    with _temporary_database_path() as database_path:
        first = default_income_assumptions()
        first["rental"]["annual_depreciation"] = Decimal("1000")
        second = default_income_assumptions()
        second["rental"]["annual_depreciation"] = Decimal("2000")

        save_income_assumptions(first, database_path)
        save_income_assumptions(second, database_path)

        assert load_income_assumptions(database_path) == second


def test_legacy_income_assumptions_default_new_investment_fields_to_zero():
    legacy_payload = json.dumps(
        {
            "employment": {
                name: {
                    "annual_salary": "0",
                    "last_work_date": None,
                }
                for name in ("Chris", "Stephanie")
            },
            "taxable_investments": {
                "annual_interest": "100",
                "annual_ordinary_dividends": "200",
                "annual_growth": "0.01",
            },
            "rental": {
                "annual_other_expenses": "0",
                "annual_depreciation": "0",
            },
        }
    )

    assumptions = _decode_income_assumptions(legacy_payload)

    assert assumptions["taxable_investments"][
        "annual_qualified_dividends"
    ] == Decimal("0")
    assert assumptions["taxable_investments"][
        "annual_net_long_term_capital_gains"
    ] == Decimal("0")
