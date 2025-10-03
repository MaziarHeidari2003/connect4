from app.db.base_class import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import INTEGER, String


class Player(Base):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    nick_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
