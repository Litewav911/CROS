from pathlib import Path
import tempfile

import pytest
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from database import Base
from import_csv import import_csv, parse_csv_content
from models import Account, CategoryRule, SourceDocument, SourceTransaction, Transaction
from transaction_service import update_category_override


@pytest.fixture
def isolated_engine():
    database_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(database_engine)
    yield database_engine
    database_engine.dispose()


def _temporary_csv(content: bytes) -> Path:
    database_directory = Path(__file__).resolve().parent.parent / "data" / "db"
    with tempfile.NamedTemporaryFile(
        prefix="import-test-",
        suffix=".csv",
        dir=database_directory,
        delete=False,
    ) as temporary_file:
        temporary_file.write(content)
        return Path(temporary_file.name)


def test_parse_csv_content_validates_and_preserves_original_rows():
    rows = parse_csv_content(
        b"Date,Description,Amount,Reference\r\n"
        b"2027-01-02,ACME Grocery,-32.50,abc\r\n"
    )

    assert len(rows) == 1
    assert rows[0]["source_row_number"] == 2
    assert rows[0]["transaction_date"].isoformat() == "2027-01-02"
    assert str(rows[0]["amount"]) == "-32.50"
    assert rows[0]["raw_row_text"] == "2027-01-02,ACME Grocery,-32.50,abc\r\n"
    assert '"Reference":"abc"' in rows[0]["original_data"]


def test_parse_csv_content_normalizes_required_header_whitespace_and_case():
    rows = parse_csv_content(
        b" date , description , AMOUNT \n"
        b"2027-01-02,ACME Grocery,-32.50\n"
    )

    assert len(rows) == 1
    assert rows[0]["transaction_date"].isoformat() == "2027-01-02"
    assert rows[0]["description"] == "ACME Grocery"
    assert str(rows[0]["amount"]) == "-32.50"
    assert '" date "' in rows[0]["original_data"]


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"Posted,Payee,Value\n2027-01-01,Store,-4\n", "must include the columns"),
        (b"Date,Description,Amount\n2027/01/01,Store,-4\n", "Date must use YYYY-MM-DD"),
        (b"Date,Description,Amount\n2027-01-01,Store,nope\n", "Amount must be a valid number"),
        (b"Date,Description,Amount\n2027-01-01,,4\n", "Description cannot be empty"),
    ],
)
def test_parse_csv_content_rejects_invalid_statements(content, message):
    with pytest.raises(ValueError, match=message):
        parse_csv_content(content)


def test_import_csv_uses_explicit_account_metadata_and_reviewed_categories(
    isolated_engine,
):
    content = (
        b"Date,Description,Amount\n"
        b"2027-01-02,ACME Grocery,-32.50\n"
        b"2027-01-03,Unknown deposit,100.00\n"
    )
    csv_path = _temporary_csv(content)
    try:
        with isolated_engine.begin() as connection:
            connection.execute(
                insert(CategoryRule).values(
                    keyword="ACME",
                    category="Groceries",
                    merchant="Acme Market",
                    transaction_type="expense",
                    priority=10,
                    active=True,
                )
            )

        imported_count = import_csv(
            csv_path,
            account_name="Joint Checking",
            account_type="checking",
            institution="Community Credit Union",
            last_four="4821",
            source_filename="january.csv",
            category_overrides={3: "Other income reviewed"},
            database_engine=isolated_engine,
        )

        assert imported_count == 2
        with Session(isolated_engine) as session:
            account = session.scalar(select(Account))
            document = session.scalar(select(SourceDocument))
            source_rows = session.scalars(
                select(SourceTransaction).order_by(SourceTransaction.id)
            ).all()
            transactions = session.scalars(
                select(Transaction).order_by(Transaction.id)
            ).all()

        assert account.name == "Joint Checking"
        assert account.account_type == "checking"
        assert account.institution == "Community Credit Union"
        assert account.last_four == "4821"
        assert document.filename == "january.csv"
        assert source_rows[0].original_description == "ACME Grocery"
        assert str(source_rows[0].original_amount) == "-32.50"
        assert transactions[0].category == "Groceries"
        assert transactions[0].merchant == "Acme Market"
        assert transactions[1].category == "Other Income"
        assert transactions[1].category_override == "Other income reviewed"
        assert all(row.account_id == account.id for row in transactions)

        update_category_override(
            transactions[0].id,
            "Household supplies",
            database_engine=isolated_engine,
        )
        with Session(isolated_engine) as session:
            corrected = session.scalar(
                select(Transaction).where(Transaction.id == transactions[0].id)
            )
        assert corrected.category == "Groceries"
        assert corrected.category_override == "Household supplies"

        with pytest.raises(ValueError, match="already been imported"):
            import_csv(
                csv_path,
                account_name="Joint Checking",
                account_type="checking",
                institution="Community Credit Union",
                last_four="4821",
                database_engine=isolated_engine,
            )
    finally:
        csv_path.unlink(missing_ok=True)


def test_import_csv_requires_explicit_new_account_metadata(isolated_engine):
    csv_path = _temporary_csv(
        b"Date,Description,Amount\n2027-01-02,Purchase,-1.00\n"
    )
    try:
        with pytest.raises(ValueError, match="Account name is required"):
            import_csv(csv_path, database_engine=isolated_engine)

        with Session(isolated_engine) as session:
            assert session.scalars(select(Account)).all() == []
            assert session.scalars(select(SourceDocument)).all() == []
    finally:
        csv_path.unlink(missing_ok=True)
