from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255)
    )

    file_type: Mapped[str] = mapped_column(
        String(50)
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime
    )

    source_transactions = relationship(
        "SourceTransaction",
        back_populates="source_document",
    )


class SourceTransaction(Base):
    __tablename__ = "source_transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id")
    )

    source_row_number: Mapped[int | None] = mapped_column(
        Integer
    )

    transaction_date: Mapped[date | None] = mapped_column(
        Date
    )

    original_description: Mapped[str | None] = mapped_column(
        Text
    )

    original_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2)
    )

    raw_row_text: Mapped[str] = mapped_column(
        Text
    )

    original_data: Mapped[str] = mapped_column(
        Text
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime
    )

    source_document = relationship(
        "SourceDocument",
        back_populates="source_transactions",
    )


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    account_type: Mapped[str] = mapped_column(
        String(50)
    )

    institution: Mapped[str | None] = mapped_column(
        String(255)
    )

    last_four: Mapped[str | None] = mapped_column(
        String(4)
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    transactions = relationship(
        "Transaction",
        back_populates="account",
    )


class CategoryRule(Base):
    __tablename__ = "category_rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    keyword: Mapped[str] = mapped_column(
        String(255)
    )

    category: Mapped[str] = mapped_column(
        String(100)
    )

    merchant: Mapped[str | None] = mapped_column(
        String(255)
    )

    transaction_type: Mapped[str] = mapped_column(
        String(50)
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    source_transaction_id: Mapped[int] = mapped_column(
        ForeignKey("source_transactions.id"),
        unique=True,
    )

    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id")
    )

    transaction_date: Mapped[date | None] = mapped_column(
        Date
    )

    description: Mapped[str | None] = mapped_column(
        Text
    )

    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2)
    )

    category: Mapped[str | None] = mapped_column(
        String(100)
    )

    category_override: Mapped[str | None] = mapped_column(
        String(100)
    )

    merchant_override: Mapped[str | None] = mapped_column(
        String(255)
    )

    merchant: Mapped[str | None] = mapped_column(
        String(255)
    )

    notes: Mapped[str | None] = mapped_column(
        Text
    )

    account = relationship(
        "Account",
        back_populates="transactions",
    )