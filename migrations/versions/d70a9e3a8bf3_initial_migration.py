"""initial migration

Revision ID: d70a9e3a8bf3
Revises: fe23aa732c38
Create Date: 2025-06-05 06:57:44.153101

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = 'd70a9e3a8bf3'
down_revision: Union[str, None] = 'fe23aa732c38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SIMPLE APPROACH: Drop and recreate tables with UUIDs
    # WARNING: This will delete all existing data!
    
    # Drop tables in correct order (child table first)
    op.drop_table('urls')
    op.drop_table('users')
    
    # Drop sequence if it exists
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq")
    
    # Create users table with UUID
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    
    # Create urls table with UUID
    op.create_table('urls',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('key', sa.String(255), unique=True, nullable=False),
        sa.Column('secret_key', sa.String(255), unique=True, nullable=False),
        sa.Column('target_url', sa.String(2048), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('clicks', sa.Integer(), default=0, nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_urls_key', 'urls', ['key'], unique=True)
    op.create_index('ix_urls_secret_key', 'urls', ['secret_key'], unique=True)
    op.create_index('ix_urls_target_url', 'urls', ['target_url'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('urls')
    op.drop_table('users')
    
    # Recreate with integer IDs (original structure)
    op.execute("CREATE SEQUENCE users_id_seq")
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False, 
                 server_default=sa.text("nextval('users_id_seq'::regclass)")),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    
    op.create_table('urls',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('key', sa.String(), unique=True, nullable=True),
        sa.Column('secret_key', sa.String(), unique=True, nullable=True),
        sa.Column('target_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('clicks', sa.Integer(), default=0, nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('date_created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_urls_key', 'urls', ['key'], unique=True)
    op.create_index('ix_urls_secret_key', 'urls', ['secret_key'], unique=True)
    op.create_index('ix_urls_target_url', 'urls', ['target_url'])