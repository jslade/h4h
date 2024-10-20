"""add asic changed_at

Create Date: 2024-10-20 06:17:39.874795

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "b9b085c1b74e"
down_revision: Union[str, None] = "352e1565a5ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("asics", sa.Column("changed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("asics", "changed_at")
