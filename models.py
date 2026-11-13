from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class ProductDB(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(10,2), nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    product_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True
    )