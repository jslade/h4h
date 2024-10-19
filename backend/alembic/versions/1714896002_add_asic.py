"""add asic

Create Date: 2024-05-05 08:00:02.919423

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1714896002"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ("default",)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "asics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("address", sa.String(length=40), nullable=False),
        sa.Column("password", sa.String(length=40)),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asics_address"), "asics", ["address"], unique=False)
    op.create_index(op.f("ix_asics_name"), "asics", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_asics_name"), table_name="asics")
    op.drop_index(op.f("ix_asics_address"), table_name="asics")
    op.drop_table("asics")
