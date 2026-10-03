import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from database import engine
from models import (
    Account,
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

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        lines = file.readlines()

    if not lines:
        return

    header = lines[0]

    reader = csv.DictReader(
        lines
    )

    physical_line_number = 1

    for row in reader:

        # csv.reader/DictReader may consume more than one
        # physical line when a CSV field contains a newline.
        # For our initial importer, locate the next complete
        # physical record using the parser's line number.
        end_line_number = reader.line_num

        raw_lines = lines[
            physical_line_number:end_line_number
        ]

        raw_row_text = "".join(raw_lines)

        yield (
            row,
            physical_line_number + 1,
            raw_row_text,
        )

        physical_line_number = end_line_number


def import_csv(
    file_path: str,
    account_name: str = "Test Checking",
) -> int:
    """Import a CSV statement while preserving source data."""

    file_path = Path(file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    file_hash = calculate_file_hash(file_path)

    with engine.begin() as connection:

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
                "filename": file_path.name,
                "file_type": file_path.suffix.lower(),
                "file_hash": file_hash,
                "imported_at": datetime.now(),
            },
        )

        source_document_id = connection.execute(
            select(SourceDocument.id).where(
                SourceDocument.file_hash == file_hash
            )
        ).scalar_one()

        # Find or create the account.
        account = connection.execute(
            select(
                Account.id,
                Account.name,
            ).where(
                Account.name == account_name
            )
        ).first()

        if account is None:

            connection.execute(
                Account.__table__.insert(),
                {
                    "name": account_name,
                    "account_type": "checking",
                    "institution": "Test Institution",
                    "is_active": True,
                },
            )

            account_id = connection.execute(
                select(Account.id).where(
                    Account.name == account_name
                )
            ).scalar_one()

        else:
            account_id = account.id

        imported_count = 0

        for (
            row,
            row_number,
            raw_row_text,
        ) in read_csv_rows_with_raw_text(file_path):

            original_data = json.dumps(
                row,
                ensure_ascii=False,
                separators=(",", ":"),
            )

            transaction_date = datetime.strptime(
                row["Date"],
                "%Y-%m-%d",
            ).date()

            amount = Decimal(row["Amount"])

            # Preserve the original source transaction.
            connection.execute(
                SourceTransaction.__table__.insert(),
                {
                    "source_document_id": source_document_id,
                    "source_row_number": row_number,
                    "transaction_date": transaction_date,
                    "original_description": row["Description"],
                    "original_amount": amount,
                    "raw_row_text": raw_row_text,
                    "original_data": original_data,
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
                    "account_id": account_id,
                    "transaction_date":
                        transaction_date,
                    "description":
                        row["Description"],
                    "amount":
                        amount,
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

        count = import_csv(test_file)

        print(
            f"Successfully imported "
            f"{count} transactions."
        )

    except ValueError as error:

        print(
            f"Import rejected: {error}"
        )