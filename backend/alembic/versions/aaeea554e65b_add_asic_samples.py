"""add asic samples

Create Date: 2024-10-20 07:07:30.087996

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "aaeea554e65b"
down_revision: Union[str, None] = "b9b085c1b74e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "performance_samples", sa.Column("hash_rate", sa.Integer(), nullable=False)
    )
    op.add_column(
        "performance_samples", sa.Column("power_limit", sa.Integer(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("performance_samples", "power_limit")
    op.drop_column("performance_samples", "hash_rate")
