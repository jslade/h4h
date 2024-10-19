"""add asic is_active

Create Date: 2024-10-19 15:22:55.287874

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "559e85839709"
down_revision: Union[str, None] = "6633fcba2b76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "asics",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.create_index(op.f("ix_asics_is_active"), "asics", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_asics_is_active"), table_name="asics")
    op.drop_column("asics", "is_active")
