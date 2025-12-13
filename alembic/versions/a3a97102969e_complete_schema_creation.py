"""complete_schema_creation

Revision ID: a3a97102969e
Revises: eebdf320e015
Create Date: 2025-12-13 18:17:57.349077

This migration creates all database tables for the evangelism backend application.
It includes:
- Users, Accounts, Roles, AccountUser (multi-tenant structure)
- Missions, MissionUser (mission management)
- OutreachData, OutreachNumbers (outreach tracking)
- Expenses (financial tracking)

All tables use UUID primary keys and include created_at/updated_at timestamps.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a3a97102969e'
down_revision: Union[str, Sequence[str], None] = 'eebdf320e015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create all tables."""
    
    # Ensure PostgreSQL extensions exist
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    
    # Get connection to check if tables exist
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # ============================================
    # 1. USERS TABLE
    # ============================================
    if 'users' not in existing_tables:
        op.create_table(
            'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.UniqueConstraint('email', name='users_email_key')
        )
        op.create_index('ix_users_id', 'users', ['id'], unique=False)
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # ============================================
    # 2. ACCOUNTS TABLE
    # ============================================
    if 'accounts' not in existing_tables:
        op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='accounts_created_by_fkey')
        )
        op.create_index('ix_accounts_id', 'accounts', ['id'], unique=False)
    
    # ============================================
    # 3. ROLES TABLE
    # ============================================
    if 'roles' not in existing_tables:
        op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.UniqueConstraint('name', name='roles_name_key'),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='roles_account_id_fkey')
        )
        op.create_index('ix_roles_id', 'roles', ['id'], unique=False)
    
    # ============================================
    # 4. ACCOUNT_USERS TABLE (Join Table)
    # ============================================
    if 'account_users' not in existing_tables:
        op.create_table(
        'account_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='account_users_account_id_fkey'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='account_users_user_id_fkey'),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='account_users_role_id_fkey')
        )
        op.create_index('ix_account_users_id', 'account_users', ['id'], unique=False)
        # Consider adding unique constraint: (account_id, user_id) where deleted_at IS NULL
    
    # ============================================
    # 5. MISSIONS TABLE
    # ============================================
    if 'missions' not in existing_tables:
        op.create_table(
        'missions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='missions_account_id_fkey'),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='missions_created_by_fkey')
        )
        op.create_index('ix_missions_id', 'missions', ['id'], unique=False)
        # Consider adding check constraint: end_date >= start_date
    
    # ============================================
    # 6. MISSION_USERS TABLE (Join Table)
    # ============================================
    # Create enum type for mission roles
    mission_role_enum = postgresql.ENUM('leader', 'member', 'guest', name='missionrole')
    mission_role_enum.create(op.get_bind(), checkfirst=True)
    
    if 'mission_users' not in existing_tables:
        op.create_table(
        'mission_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('mission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', mission_role_enum, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name='mission_users_mission_id_fkey'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='mission_users_user_id_fkey')
        )
        op.create_index('ix_mission_users_id', 'mission_users', ['id'], unique=False)
        # Consider adding unique constraint: (mission_id, user_id) where deleted_at IS NULL
    
    # ============================================
    # 7. OUTREACH_DATA TABLE
    # ============================================
    if 'outreach_data' not in existing_tables:
        op.create_table(
        'outreach_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='outreach_data_account_id_fkey'),
            sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name='outreach_data_mission_id_fkey'),
            sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name='outreach_data_created_by_user_id_fkey')
        )
        op.create_index('ix_outreach_data_id', 'outreach_data', ['id'], unique=False)
        op.create_index('ix_outreach_data_account_id', 'outreach_data', ['account_id'], unique=False)
        op.create_index('ix_outreach_data_mission_id', 'outreach_data', ['mission_id'], unique=False)
        # Consider adding index on status and created_by_user_id
    
    # ============================================
    # 8. OUTREACH_NUMBERS TABLE
    # ============================================
    if 'outreach_numbers' not in existing_tables:
        op.create_table(
        'outreach_numbers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interested', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('healed', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('saved', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='outreach_numbers_account_id_fkey'),
            sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name='outreach_numbers_mission_id_fkey'),
            sa.UniqueConstraint('mission_id', name='outreach_numbers_mission_id_key')
        )
        op.create_index('ix_outreach_numbers_id', 'outreach_numbers', ['id'], unique=False)
        op.create_index('ix_outreach_numbers_account_id', 'outreach_numbers', ['account_id'], unique=False)
        op.create_index('ix_outreach_numbers_mission_id', 'outreach_numbers', ['mission_id'], unique=True)
    
    # ============================================
    # 9. EXPENSES TABLE
    # ============================================
    if 'expenses' not in existing_tables:
        op.create_table(
        'expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mission_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='expenses_account_id_fkey'),
            sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name='expenses_mission_id_fkey'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='expenses_user_id_fkey')
        )
        op.create_index('ix_expenses_id', 'expenses', ['id'], unique=False)
        op.create_index('ix_expenses_mission_id', 'expenses', ['mission_id'], unique=False)
        # Consider adding index on category
        # Consider adding check constraint: amount > 0


def downgrade() -> None:
    """Downgrade schema - Drop all tables in reverse order."""
    
    # Drop tables in reverse dependency order
    op.drop_table('expenses')
    op.drop_table('outreach_numbers')
    op.drop_table('outreach_data')
    op.drop_table('mission_users')
    op.drop_table('missions')
    op.drop_table('account_users')
    op.drop_table('roles')
    op.drop_table('accounts')
    op.drop_table('users')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS missionrole')
    
    # Note: Extensions are not dropped as they may be used by other databases
