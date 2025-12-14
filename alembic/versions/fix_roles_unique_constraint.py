"""fix_roles_unique_constraint_per_account

Revision ID: fix_roles_unique
Revises: a05db07c37b7
Create Date: 2025-12-14 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_roles_unique'
down_revision = 'a05db07c37b7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old unique constraint on name only
    op.drop_constraint('roles_name_key', 'roles', type_='unique')
    
    # Add composite unique constraint on (name, account_id)
    op.create_unique_constraint('unique_role_per_account', 'roles', ['name', 'account_id'])


def downgrade():
    # Revert to old constraint
    op.drop_constraint('unique_role_per_account', 'roles', type_='unique')
    op.create_unique_constraint('roles_name_key', 'roles', ['name'])
