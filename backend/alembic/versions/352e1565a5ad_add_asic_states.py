"""add asic states

Create Date: 2024-10-19 22:58:49.028202

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "352e1565a5ad"
down_revision: Union[str, None] = "559e85839709"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "asics",
        sa.Column("is_online", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "asics",
        sa.Column("is_hashing", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "asics",
        sa.Column("is_stable", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("asics", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_asics_is_hashing"), "asics", ["is_hashing"], unique=False)
    op.create_index(op.f("ix_asics_is_online"), "asics", ["is_online"], unique=False)
    op.create_index(op.f("ix_asics_is_stable"), "asics", ["is_stable"], unique=False)
    op.add_column(
        "performance_samples", sa.Column("is_online", sa.Boolean(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("performance_samples", "is_online")
    op.drop_index(op.f("ix_asics_is_stable"), table_name="asics")
    op.drop_index(op.f("ix_asics_is_online"), table_name="asics")
    op.drop_index(op.f("ix_asics_is_hashing"), table_name="asics")
    op.drop_column("asics", "updated_at")
    op.drop_column("asics", "is_stable")
    op.drop_column("asics", "is_hashing")
    op.drop_column("asics", "is_online")
