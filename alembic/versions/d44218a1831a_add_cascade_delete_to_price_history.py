"""add cascade delete to price history

Revision ID: d44218a1831a
Revises: 4d74ffd21d31
Create Date: 2026-11-17 17:54:14.151977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd44218a1831a'
down_revision: Union[str, Sequence[str], None] = '4d74ffd21d31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the existing foreign key
    op.drop_constraint(
        "price_history_product_id_fkey",
        "price_history",
        type_="foreignkey"
    )

    # Create the foreign key with cascading deletes
    op.create_foreign_key(
        "price_history_product_id_fkey",
        "price_history",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE"
    )

def downgrade() -> None:
    # Remove the cascading foreign key
    op.drop_constraint(
        "price_history)product_id_fkey",
        "price_history",
        type_="foreignkey"
    )

    # Restore the original foreign key
    op.create_foreign_key(
        "price_history_product_id_fkey",
        "price_history",
        "products",
        ["product_id"],
        ["id"]
    )
