"""Add interval to sample

Create Date: 2025-11-02 05:32:53.644800

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "dde465bb185a"
down_revision: Union[str, None] = "d91e9a15a4c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "performance_samples",
        sa.Column("hashing_interval_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_performance_samples_hashing_interval_id"),
        "performance_samples",
        ["hashing_interval_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_performance_samples_hashing_intervals",
        "performance_samples",
        "hashing_intervals",
        ["hashing_interval_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_performance_samples_hashing_intervals",
        "performance_samples",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_performance_samples_hashing_interval_id"),
        table_name="performance_samples",
    )
    op.drop_column("performance_samples", "hashing_interval_id")
