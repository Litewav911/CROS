from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "data" / "db" / "cros.db"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=False,
)