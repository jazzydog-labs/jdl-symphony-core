#!/usr/bin/env python3
"""Demo script showcasing database models and domain model mapping."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from symphony.domain.models import Repo, UserProfile, Vault, Workspace
from symphony.infrastructure.database.base import Base
from symphony.infrastructure.database.models import RepoDB, UserProfileDB, VaultDB, WorkspaceDB


def domain_to_db_user_profile(user: UserProfile) -> UserProfileDB:
    """Convert domain UserProfile to database model."""
    return UserProfileDB(
        id=user.id,
        username=user.username,
        email=user.email,
        preferences=user.preferences,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def db_to_domain_user_profile(db_user: UserProfileDB) -> UserProfile:
    """Convert database UserProfile to domain model."""
    return UserProfile(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        preferences=db_user.preferences,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
    )


def domain_to_db_workspace(workspace: Workspace) -> WorkspaceDB:
    """Convert domain Workspace to database model."""
    return WorkspaceDB(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        user_profile_id=workspace.user_profile_id,
        workspace_type=workspace.workspace_type,
        settings=workspace.settings,
        shared_resources=workspace.shared_resources,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


def db_to_domain_workspace(db_workspace: WorkspaceDB) -> Workspace:
    """Convert database Workspace to domain model."""
    return Workspace(
        id=db_workspace.id,
        name=db_workspace.name,
        description=db_workspace.description,
        user_profile_id=db_workspace.user_profile_id,
        workspace_type=db_workspace.workspace_type,
        settings=db_workspace.settings,
        shared_resources=db_workspace.shared_resources,
        created_at=db_workspace.created_at,
        updated_at=db_workspace.updated_at,
    )


def domain_to_db_repo(repo: Repo) -> RepoDB:
    """Convert domain Repo to database model."""
    return RepoDB(
        id=repo.id,
        name=repo.name,
        path=repo.path,
        workspace_id=repo.workspace_id,
        remote_url=repo.remote_url,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
    )


def db_to_domain_repo(db_repo: RepoDB) -> Repo:
    """Convert database Repo to domain model."""
    return Repo(
        id=db_repo.id,
        name=db_repo.name,
        path=db_repo.path,
        workspace_id=db_repo.workspace_id,
        remote_url=db_repo.remote_url,
        created_at=db_repo.created_at,
        updated_at=db_repo.updated_at,
    )


def domain_to_db_vault(vault: Vault) -> VaultDB:
    """Convert domain Vault to database model."""
    return VaultDB(
        id=vault.id,
        name=vault.name,
        path=vault.path,
        workspace_id=vault.workspace_id,
        created_at=vault.created_at,
        updated_at=vault.updated_at,
    )


def db_to_domain_vault(db_vault: VaultDB) -> Vault:
    """Convert database Vault to domain model."""
    return Vault(
        id=db_vault.id,
        name=db_vault.name,
        path=db_vault.path,
        workspace_id=db_vault.workspace_id,
        created_at=db_vault.created_at,
        updated_at=db_vault.updated_at,
    )


async def demo_database_models():
    """Demonstrate database model functionality."""
    print("🎵 Symphony Database Models Demo")
    print("=" * 60)

    # Create in-memory SQLite database for demo
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # 1. Create domain models
        print("\n1. Creating domain models with validation...")
        user = UserProfile(
            id=uuid4(),
            username="john_doe",
            email="john@example.com",
            preferences={"theme": "dark", "language": "en"},
        )
        print(f"✅ Created UserProfile: {user.username}")

        workspace = Workspace(
            id=uuid4(),
            name="ML Research Project",
            description="Machine learning experiments and papers",
            user_profile_id=user.id,
            workspace_type="research",
            settings={"auto_save": True, "notifications": False},
        )
        print(f"✅ Created Workspace: {workspace.name}")

        repo = Repo(
            id=uuid4(),
            name="ml-experiments",
            path="/home/john/projects/ml-experiments",
            workspace_id=workspace.id,
            remote_url="git@github.com:johndoe/ml-experiments.git",
        )
        print(f"✅ Created Repo: {repo.name}")

        vault = Vault(
            id=uuid4(),
            name="research-notes",
            path="/home/john/vaults/research-notes",
            workspace_id=workspace.id,
        )
        print(f"✅ Created Vault: {vault.name}")

        # 2. Convert to database models and save
        print("\n2. Converting to database models and persisting...")
        db_user = domain_to_db_user_profile(user)
        db_workspace = domain_to_db_workspace(workspace)
        db_repo = domain_to_db_repo(repo)
        db_vault = domain_to_db_vault(vault)

        session.add_all([db_user, db_workspace, db_repo, db_vault])
        await session.commit()
        print("✅ All models saved to database")

        # 3. Query and demonstrate relationships
        print("\n3. Querying database with relationships...")
        stmt = select(UserProfileDB).where(UserProfileDB.username == "john_doe")
        result = await session.execute(stmt)
        loaded_user = result.scalar_one()

        print(f"✅ Loaded user: {loaded_user.username}")
        print(f"   Email: {loaded_user.email}")
        print(f"   Preferences: {loaded_user.preferences}")

        # Load workspaces for user
        stmt = select(WorkspaceDB).where(WorkspaceDB.user_profile_id == loaded_user.id)
        result = await session.execute(stmt)
        workspaces = result.scalars().all()

        print(f"\n   User has {len(workspaces)} workspace(s):")
        for ws in workspaces:
            print(f"   - {ws.name} ({ws.workspace_type})")

            # Load repos for workspace
            stmt = select(RepoDB).where(RepoDB.workspace_id == ws.id)
            result = await session.execute(stmt)
            repos = result.scalars().all()
            print(f"     Repos: {[r.name for r in repos]}")

            # Load vaults for workspace
            stmt = select(VaultDB).where(VaultDB.workspace_id == ws.id)
            result = await session.execute(stmt)
            vaults = result.scalars().all()
            print(f"     Vaults: {[v.name for v in vaults]}")

        # 4. Convert back to domain models
        print("\n4. Converting back to domain models...")
        domain_user = db_to_domain_user_profile(loaded_user)
        print(f"✅ Converted to domain UserProfile: {domain_user.username}")

        # 5. Demonstrate domain model validation
        print("\n5. Testing domain model validation...")
        try:
            invalid_user = UserProfile(username="a", email="invalid-email")
        except ValueError as e:
            print(f"✅ Validation caught invalid username: {e}")

        try:
            invalid_workspace = Workspace(
                name="", user_profile_id=uuid4(), workspace_type="invalid"
            )
        except ValueError as e:
            print(f"✅ Validation caught invalid workspace: {e}")

        # 6. Update operations
        print("\n6. Testing update operations...")
        domain_user.update_email("john.doe@newdomain.com")
        workspace.rename("Advanced ML Research")
        workspace.add_shared_resource(uuid4(), "template")

        # Update in database
        loaded_user.email = domain_user.email
        loaded_user.updated_at = datetime.now(UTC)
        await session.commit()
        print("✅ Updates persisted to database")

    # Clean up
    await engine.dispose()
    print("\n✨ Database models demo completed!")


if __name__ == "__main__":
    # Note: This demo uses SQLite for simplicity. In production, the app uses PostgreSQL.
    # To run with PostgreSQL, ensure Docker is running and use `just db-up` first.
    try:
        import aiosqlite  # noqa: F401
    except ImportError:
        print("Please install aiosqlite to run this demo: pip install aiosqlite")
        exit(1)

    asyncio.run(demo_database_models())