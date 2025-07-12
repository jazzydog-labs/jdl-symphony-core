"""Initial schema with UserProfile, Workspace, Repo, and Vault

Revision ID: 001
Revises: 
Create Date: 2025-07-12 13:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profiles_email'), 'user_profiles', ['email'], unique=True)
    op.create_index(op.f('ix_user_profiles_username'), 'user_profiles', ['username'], unique=True)

    # Create workspace_type enum
    workspace_type_enum = postgresql.ENUM('general', 'client', 'personal', 'research', name='workspace_type_enum')
    workspace_type_enum.create(op.get_bind())

    # Create workspaces table
    op.create_table('workspaces',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_profile_id', postgresql.UUID(), nullable=False),
        sa.Column('workspace_type', sa.Enum('general', 'client', 'personal', 'research', name='workspace_type_enum'), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=False),
        sa.Column('shared_resources', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_profile_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_name'), 'workspaces', ['name'], unique=False)
    op.create_index(op.f('ix_workspaces_user_profile_id'), 'workspaces', ['user_profile_id'], unique=False)

    # Create repos table
    op.create_table('repos',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('path', sa.Text(), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(), nullable=False),
        sa.Column('remote_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repos_name'), 'repos', ['name'], unique=False)
    op.create_index(op.f('ix_repos_workspace_id'), 'repos', ['workspace_id'], unique=False)

    # Create vaults table
    op.create_table('vaults',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('path', sa.Text(), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vaults_name'), 'vaults', ['name'], unique=False)
    op.create_index(op.f('ix_vaults_workspace_id'), 'vaults', ['workspace_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_vaults_workspace_id'), table_name='vaults')
    op.drop_index(op.f('ix_vaults_name'), table_name='vaults')
    op.drop_table('vaults')
    
    op.drop_index(op.f('ix_repos_workspace_id'), table_name='repos')
    op.drop_index(op.f('ix_repos_name'), table_name='repos')
    op.drop_table('repos')
    
    op.drop_index(op.f('ix_workspaces_user_profile_id'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_name'), table_name='workspaces')
    op.drop_table('workspaces')
    
    # Drop enum type
    workspace_type_enum = postgresql.ENUM('general', 'client', 'personal', 'research', name='workspace_type_enum')
    workspace_type_enum.drop(op.get_bind())
    
    op.drop_index(op.f('ix_user_profiles_username'), table_name='user_profiles')
    op.drop_index(op.f('ix_user_profiles_email'), table_name='user_profiles')
    op.drop_table('user_profiles')