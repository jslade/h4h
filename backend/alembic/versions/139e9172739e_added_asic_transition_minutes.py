"""Added asic transition_minutes

Create Date: 2026-03-11 23:34:43.474052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '139e9172739e'
down_revision: Union[str, None] = 'dde465bb185a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('asics', sa.Column('transition_minutes', sa.Integer(), server_default='5', nullable=False))


def downgrade() -> None:
    op.drop_column('asics', 'transition_minutes')
