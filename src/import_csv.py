import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import Engine

from categorization import categorize_with_rules
from database import engine
from models import (
    Account,
    CategoryRule,
    SourceDocument,
    SourceTransaction,
    Transaction,
)


def calculate_file_hash(file_path: Path) -> str:
    """Return the SHA-256 hash of the original file."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def read_csv_rows_with_raw_text(file_path: Path):
    """
    Read CSV rows while preserving the original physical
    CSV line text.

    The original file itself is also preserved separately
    through its SHA-256 hash and source document record.
    """

    content = file_path.read_bytes()

    for row in parse_csv_content(content):
        yield (
            json.loads(row["original_data"]),
            row["source_row_number"],
            row["raw_row_text"],
        )


def parse_csv_content(content: bytes) -> list[dict[str, object]]:
    """Validate and normalize a CSV using the supported statement columns."""
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("CSV must be encoded as UTF-8.") from error

    if not text.strip():
        raise ValueError("CSV file is empty.")

    lines = text.splitlines(keepends=True)
    reader = csv.DictReader(lines)
    required_columns = {"Date", "Description", "Amount"}
    raw_fieldnames = reader.fieldnames
    canonical_headers = {
        "date": "Date",
        "description": "Description",
        "amount": "Amount",
    }
    normalized_fieldnames = [
        canonical_headers.get(fieldname.strip().casefold(), fieldname.strip())
        for fieldname in raw_fieldnames or []
    ]
    if len({name.casefold() for name in normalized_fieldnames}) != len(
        normalized_fieldnames
    ):
        raise ValueError("CSV column names must be unique.")
    if not raw_fieldnames or not required_columns.issubset(
        normalized_fieldnames
    ):
        raise ValueError(
            "CSV must include the columns Date, Description, and Amount."
        )

    parsed_rows = []
    previous_line_number = 1
    for row in reader:
        line_number = reader.line_num
        raw_row_text = "".join(lines[previous_line_number:line_number])
        previous_line_number = line_number

        if not row or all(value in (None, "") for value in row.values()):
            continue
        if None in row:
            raise ValueError(
                f"CSV row {line_number}: Row has more values than the header."
            )
        normalized_row = {
            normalized: row[original]
            for original, normalized in zip(
                raw_fieldnames, normalized_fieldnames
            )
        }

        try:
            transaction_date = datetime.strptime(
                (normalized_row.get("Date") or "").strip(),
                "%Y-%m-%d",
            ).date()
        except ValueError as error:
            raise ValueError(
                f"CSV row {line_number}: Date must use YYYY-MM-DD."
            ) from error

        description = (normalized_row.get("Description") or "").strip()
        if not description:
            raise ValueError(
                f"CSV row {line_number}: Description cannot be empty."
            )

        try:
            amount = Decimal((normalized_row.get("Amount") or "").strip())
        except InvalidOperation as error:
            raise ValueError(
                f"CSV row {line_number}: Amount must be a valid number."
            ) from error
        if not amount.is_finite():
            raise ValueError(
                f"CSV row {line_number}: Amount must be finite."
            )

        original_data = json.dumps(
            row,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        parsed_rows.append(
            {
                "source_row_number": line_number,
                "transaction_date": transaction_date,
                "description": description,
                "amount": amount,
                "raw_row_text": raw_row_text,
                "original_data": original_data,
            }
        )

    if not parsed_rows:
        raise ValueError("CSV contains no transaction rows.")

    return parsed_rows


def import_csv(
    file_path: str | Path,
    account_id: int | None = None,
    account_name: str | None = None,
    account_type: str | None = None,
    institution: str | None = None,
    last_four: str | None = None,
    source_filename: str | None = None,
    category_overrides: dict[int, str] | None = None,
    database_engine: Engine = engine,
) -> int:
    """Import a CSV statement while preserving source data."""

    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if account_id is None:
        if not account_name or not account_name.strip():
            raise ValueError("Account name is required for a new account.")
        if not account_type or not account_type.strip():
            raise ValueError("Account type is required for a new account.")
        if not institution or not institution.strip():
            raise ValueError("Institution is required for a new account.")
        if last_four and (
            len(last_four) != 4 or not last_four.isdigit()
        ):
            raise ValueError("Last four must contain exactly four digits.")

    parsed_rows = parse_csv_content(file_path.read_bytes())
    file_hash = calculate_file_hash(file_path)

    with database_engine.begin() as connection:

        # Prevent importing the exact same file twice.
        existing_document = connection.execute(
            select(
                SourceDocument.id,
                SourceDocument.filename,
            ).where(
                SourceDocument.file_hash == file_hash
            )
        ).first()

        if existing_document:
            raise ValueError(
                "This file has already been imported: "
                f"{existing_document.filename}"
            )

        # Register the original document.
        connection.execute(
            SourceDocument.__table__.insert(),
            {
                "filename": source_filename or file_path.name,
                "file_type": Path(source_filename or file_path.name).suffix.lower(),
                "file_hash": file_hash,
                "imported_at": datetime.now(),
            },
        )

        source_document_id = connection.execute(
            select(SourceDocument.id).where(
                SourceDocument.file_hash == file_hash
            )
        ).scalar_one()

        if account_id is not None:
            account = connection.execute(
                select(Account.id).where(
                    Account.id == account_id,
                    Account.is_active.is_(True),
                )
            ).first()
            if account is None:
                raise ValueError("Selected account does not exist or is inactive.")
            resolved_account_id = account.id
        else:
            duplicate_account = connection.execute(
                select(Account.id).where(Account.name == account_name.strip())
            ).first()
            if duplicate_account:
                raise ValueError(
                    "An account with that name already exists. Select it instead."
                )
            connection.execute(
                Account.__table__.insert(),
                {
                    "name": account_name.strip(),
                    "account_type": account_type.strip(),
                    "institution": institution.strip(),
                    "last_four": last_four or None,
                    "is_active": True,
                },
            )

            resolved_account_id = connection.execute(
                select(Account.id).where(Account.name == account_name.strip())
            ).scalar_one()

        category_rules = connection.execute(
            select(
                CategoryRule.keyword,
                CategoryRule.category,
                CategoryRule.merchant,
                CategoryRule.transaction_type,
            )
            .where(CategoryRule.active.is_(True))
            .order_by(CategoryRule.priority.asc(), CategoryRule.id.asc())
        ).all()
        category_overrides = category_overrides or {}
        imported_count = 0

        for row in parsed_rows:
            row_number = row["source_row_number"]
            transaction_date = row["transaction_date"]
            description = row["description"]
            amount = row["amount"]
            category_result = categorize_with_rules(
                description,
                float(amount),
                category_rules,
            )

            # Preserve the original source transaction.
            connection.execute(
                SourceTransaction.__table__.insert(),
                {
                    "source_document_id": source_document_id,
                    "source_row_number": row_number,
                    "transaction_date": transaction_date,
                    "original_description": description,
                    "original_amount": amount,
                    "raw_row_text": row["raw_row_text"],
                    "original_data": row["original_data"],
                    "imported_at": datetime.now(),
                },
            )

            source_transaction_id = connection.execute(
                select(SourceTransaction.id)
                .where(
                    SourceTransaction.source_document_id
                    == source_document_id
                )
                .where(
                    SourceTransaction.source_row_number
                    == row_number
                )
            ).scalar_one()

            # Create the CROS working transaction.
            connection.execute(
                Transaction.__table__.insert(),
                {
                    "source_transaction_id":
                        source_transaction_id,
                    "account_id": resolved_account_id,
                    "transaction_date":
                        transaction_date,
                    "description": description,
                    "amount":
                        amount,
                    "category": category_result.category,
                    "category_override": category_overrides.get(row_number),
                    "merchant": category_result.merchant,
                },
            )

            imported_count += 1

    return imported_count


if __name__ == "__main__":

    test_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "imports"
        / "test_statement.csv"
    )

    try:

        count = import_csv(
            test_file,
            account_name="Test Checking",
            account_type="checking",
            institution="Test Institution",
        )

        print(
            f"Successfully imported "
            f"{count} transactions."
        )

    except ValueError as error:

        print(
            f"Import rejected: {error}"
        )
