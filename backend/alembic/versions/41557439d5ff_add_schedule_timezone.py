"""add schedule timezone

Create Date: 2024-10-20 20:56:13.713066

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "41557439d5ff"
down_revision: Union[str, None] = "aaeea554e65b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hashing_schedules", sa.Column("timezone_name", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("hashing_schedules", "timezone_name")
