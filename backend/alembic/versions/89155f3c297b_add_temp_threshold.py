"""Add temp threshold

Create Date: 2025-04-03 01:59:16.912081

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "89155f3c297b"
down_revision: Union[str, None] = "ab110a383df2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hashing_intervals",
        sa.Column("temp_min", sa.Integer(), server_default="0", nullable=True),
    )
    op.add_column(
        "hashing_intervals",
        sa.Column("temp_max", sa.Integer(), server_default="0", nullable=True),
    )


def downgrade() -> None:
    op.drop_column("hashing_intervals", "temp_max")
    op.drop_column("hashing_intervals", "temp_min")
