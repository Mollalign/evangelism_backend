"""fix_healed_to_heared_column_name

Revision ID: a05db07c37b7
Revises: a3a97102969e
Create Date: 2025-12-14 03:31:29.576759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a05db07c37b7'
down_revision: Union[str, Sequence[str], None] = 'a3a97102969e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Rename healed to heared."""
    # Rename column from healed to heared
    op.alter_column('outreach_numbers', 'healed',
                    new_column_name='heared',
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    existing_server_default=sa.text('0'))


def downgrade() -> None:
    """Downgrade schema - Rename heared back to healed."""
    # Rename column back from heared to healed
    op.alter_column('outreach_numbers', 'heared',
                    new_column_name='healed',
                    existing_type=sa.Integer(),
                    existing_nullable=False,
                    existing_server_default=sa.text('0'))
