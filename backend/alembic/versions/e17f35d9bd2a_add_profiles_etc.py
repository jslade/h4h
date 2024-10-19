"""Add profiles etc

Create Date: 2024-10-17 13:20:14.007684

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e17f35d9bd2a"
down_revision: Union[str, None] = "1714896002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hashing_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "performance_limits",
        sa.Column("power_limit", sa.Integer(), nullable=True),
        sa.Column("daily_power_budget", sa.Integer(), nullable=True),
        sa.Column("weekly_power_budget", sa.Integer(), nullable=True),
        sa.Column("monthly_power_budget", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "asic_profiles",
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["hashing_schedules.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asic_profiles_name"), "asic_profiles", ["name"], unique=True)
    op.create_table(
        "hashing_intervals",
        sa.Column("daytime_start_hhmm", sa.String(), nullable=False),
        sa.Column("daytime_end_hhmm", sa.String(), nullable=False),
        sa.Column("date_start_mmdd", sa.String(), nullable=False),
        sa.Column("date_end_mmdd", sa.String(), nullable=False),
        sa.Column("weekdays_active", sa.String(), nullable=False),
        sa.Column("hashing_enabled", sa.Boolean(), nullable=False),
        sa.Column("price_per_kwh", sa.Numeric(precision=6, scale=3), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=True),
        sa.Column("performance_limit_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.ForeignKeyConstraint(
            ["performance_limit_id"],
            ["performance_limits.id"],
        ),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["hashing_schedules.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "performance_samples",
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("asic_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["asic_id"],
            ["asics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_performance_samples_asic_id"),
        "performance_samples",
        ["asic_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_samples_timestamp"),
        "performance_samples",
        ["timestamp"],
        unique=False,
    )
    op.add_column("asics", sa.Column("profile_id", sa.Integer(), nullable=True))
    op.alter_column(
        "asics", "password", existing_type=sa.VARCHAR(length=40), nullable=False
    )
    op.alter_column(
        "asics",
        "name",
        existing_type=sa.VARCHAR(length=40),
        type_=sa.String(length=60),
        existing_nullable=False,
    )
    op.drop_index("ix_asics_name", table_name="asics")
    op.create_index(op.f("ix_asics_name"), "asics", ["name"], unique=True)
    op.create_foreign_key(None, "asics", "asic_profiles", ["profile_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("asics_profile_id_fkey", "asics", type_="foreignkey")
    op.drop_index(op.f("ix_asics_name"), table_name="asics")
    op.create_index("ix_asics_name", "asics", ["name"], unique=False)
    op.alter_column(
        "asics",
        "name",
        existing_type=sa.String(length=60),
        type_=sa.VARCHAR(length=40),
        existing_nullable=False,
    )
    op.alter_column(
        "asics", "password", existing_type=sa.VARCHAR(length=40), nullable=True
    )
    op.drop_column("asics", "profile_id")
    op.drop_index(
        op.f("ix_performance_samples_timestamp"), table_name="performance_samples"
    )
    op.drop_index(
        op.f("ix_performance_samples_asic_id"), table_name="performance_samples"
    )
    op.drop_table("performance_samples")
    op.drop_table("hashing_intervals")
    op.drop_index(op.f("ix_asic_profiles_name"), table_name="asic_profiles")
    op.drop_table("asic_profiles")
    op.drop_table("performance_limits")
    op.drop_table("hashing_schedules")
