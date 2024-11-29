"""add asic override interval

Create Date: 2024-11-28 23:22:58.097079

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "dea9b849e378"
down_revision: Union[str, None] = "41557439d5ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("asics", sa.Column("override_interval_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "asics", "hashing_intervals", ["override_interval_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(None, "asics", type_="foreignkey")
    op.drop_column("asics", "override_interval_id")
