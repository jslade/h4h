"""Add interval ordering

Create Date: 2024-12-14 14:54:21.608537

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ab110a383df2"
down_revision: Union[str, None] = "dea9b849e378"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hashing_intervals",
        sa.Column("order", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "hashing_intervals",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.alter_column(
        "hashing_intervals",
        "price_per_kwh",
        existing_type=sa.NUMERIC(precision=6, scale=3),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "hashing_intervals",
        "price_per_kwh",
        existing_type=sa.NUMERIC(precision=6, scale=3),
        nullable=False,
    )
    op.drop_column("hashing_intervals", "is_active")
    op.drop_column("hashing_intervals", "order")
