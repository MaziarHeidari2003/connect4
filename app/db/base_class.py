from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import mapped_column


def get_datetime_now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created = mapped_column(
        DateTime(timezone=True), default=get_datetime_now_utc, index=True
    )
    modified = mapped_column(
        DateTime(timezone=True),
        default=get_datetime_now_utc,
        index=True,
        onupdate=get_datetime_now_utc,
    )
    is_deleted = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    def __str__(self):
        return f"{self.__tablename__}:{self.id}"

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}({self.__tablename__}:{self.id})"
        except:
            return f"Faulty-{self.__class__.__name__}"
