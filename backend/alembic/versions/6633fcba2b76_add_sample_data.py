"""Add sample data

Create Date: 2024-10-17 14:26:27.697293

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6633fcba2b76"
down_revision: Union[str, None] = "e17f35d9bd2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "performance_samples", sa.Column("interval_secs", sa.Integer(), nullable=False)
    )
    op.add_column(
        "performance_samples", sa.Column("is_hashing", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "performance_samples", sa.Column("is_stable", sa.Boolean(), nullable=False)
    )
    op.add_column("performance_samples", sa.Column("power", sa.Integer(), nullable=False))
    op.add_column(
        "performance_samples", sa.Column("power_per_th", sa.Integer(), nullable=False)
    )
    op.add_column("performance_samples", sa.Column("temp", sa.Integer(), nullable=False))
    op.add_column(
        "performance_samples", sa.Column("env_temp", sa.Integer(), nullable=False)
    )
    op.add_column(
        "performance_samples",
        sa.Column("price_per_kwh", sa.Numeric(precision=6, scale=3), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("performance_samples", "price_per_kwh")
    op.drop_column("performance_samples", "env_temp")
    op.drop_column("performance_samples", "temp")
    op.drop_column("performance_samples", "power_per_th")
    op.drop_column("performance_samples", "power")
    op.drop_column("performance_samples", "is_stable")
    op.drop_column("performance_samples", "is_hashing")
    op.drop_column("performance_samples", "interval_secs")
