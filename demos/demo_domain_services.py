#!/usr/bin/env python3
"""Demo script showcasing domain services functionality."""

import asyncio
from pathlib import Path

from symphony.config.demo import get_demo_settings
from symphony.domain.exceptions import (
    DuplicateRepoNameError,
    EmailAlreadyExistsError,
    RepoLimitExceeded,
    UsernameAlreadyExistsError,
    UserProfileNotFoundError,
    VaultLimitExceeded,
    WorkspaceLimitExceeded,
    WorkspaceNotFoundError,
)
from symphony.domain.services import (
    RepoService,
    UserProfileService,
    VaultService,
    WorkspaceService,
)
from symphony.infrastructure.database.connection import get_engine
from symphony.infrastructure.database.base import Base
from symphony.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


class DemoServices:
    """Demo showcasing domain services capabilities."""

    def __init__(self) -> None:
        """Initialize demo with database setup."""
        # Use demo database
        self.settings = get_demo_settings()
        # Use persistent file for this demo
        self.settings.demo_database_url = "sqlite+aiosqlite:///demo_services.db"
        self.engine = get_engine(self.settings)

    async def setup_database(self) -> None:
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")

    async def demo_user_profile_service(self) -> None:
        """Demonstrate UserProfileService functionality."""
        print("\n" + "=" * 60)
        print("🧑 USER PROFILE SERVICE DEMO")
        print("=" * 60)

        # Create unit of work and service
        uow = SQLAlchemyUnitOfWork(self.settings)
        service = UserProfileService(uow)

        # 1. Create user profiles
        print("\n1. Creating user profiles...")
        alice = await service.create_user_profile(
            username="alice_dev",
            email="alice@example.com",
            preferences={"theme": "dark", "notifications": True}
        )
        print(f"   ✅ Created user: {alice.username} ({alice.id})")

        bob = await service.create_user_profile(
            username="bob_designer",
            email="bob@example.com"
        )
        print(f"   ✅ Created user: {bob.username} ({bob.id})")

        # 2. Try creating duplicate username
        print("\n2. Testing duplicate username validation...")
        try:
            await service.create_user_profile(
                username="alice_dev",  # Duplicate!
                email="alice2@example.com"
            )
        except UsernameAlreadyExistsError as e:
            print(f"   ❌ Expected error: {e}")

        # 3. Try creating duplicate email
        print("\n3. Testing duplicate email validation...")
        try:
            await service.create_user_profile(
                username="alice_other",
                email="alice@example.com"  # Duplicate!
            )
        except EmailAlreadyExistsError as e:
            print(f"   ❌ Expected error: {e}")

        # 4. Update user profile
        print("\n4. Updating user profile...")
        updated_alice = await service.update_user_profile(
            user_id=alice.id,
            preferences={"theme": "light", "notifications": False, "language": "en"}
        )
        print(f"   ✅ Updated preferences: {updated_alice.preferences}")

        # 5. Get user by username
        print("\n5. Getting user by username...")
        user = await service.get_user_profile_by_username("bob_designer")
        print(f"   ✅ Found user: {user.username} ({user.email})")

        # 6. Check workspace limit
        print("\n6. Checking workspace creation permission...")
        can_create = await service.can_create_workspace(alice.id)
        print(f"   ✅ Can create workspace: {can_create}")

        return alice, bob

    async def demo_workspace_service(self, alice_id, bob_id) -> None:
        """Demonstrate WorkspaceService functionality."""
        print("\n" + "=" * 60)
        print("🏢 WORKSPACE SERVICE DEMO")
        print("=" * 60)

        # Create unit of work and service
        uow = SQLAlchemyUnitOfWork(self.settings)
        service = WorkspaceService(uow)

        # 1. Create workspaces
        print("\n1. Creating workspaces...")
        personal_ws = await service.create_workspace(
            user_id=alice_id,
            name="Personal Projects",
            workspace_type="personal",
            description="My personal coding projects"
        )
        print(f"   ✅ Created workspace: {personal_ws.name} ({personal_ws.id})")

        client_ws = await service.create_workspace(
            user_id=alice_id,
            name="Client Work",
            workspace_type="client",
            description="Projects for clients",
            settings={"billing_enabled": True}
        )
        print(f"   ✅ Created workspace: {client_ws.name} ({client_ws.id})")

        research_ws = await service.create_workspace(
            user_id=bob_id,
            name="Design Research",
            workspace_type="research"
        )
        print(f"   ✅ Created workspace: {research_ws.name} ({research_ws.id})")

        # 2. List user workspaces
        print("\n2. Listing Alice's workspaces...")
        alice_workspaces = await service.list_user_workspaces(alice_id)
        for ws in alice_workspaces:
            print(f"   - {ws.name} ({ws.workspace_type})")

        # 3. Filter by type
        print("\n3. Filtering by workspace type...")
        client_workspaces = await service.list_user_workspaces(
            alice_id, 
            workspace_type="client"
        )
        print(f"   Found {len(client_workspaces)} client workspace(s)")

        # 4. Update workspace
        print("\n4. Updating workspace...")
        updated_ws = await service.update_workspace(
            workspace_id=personal_ws.id,
            user_id=alice_id,
            description="My awesome personal projects",
            settings={"auto_backup": True}
        )
        print(f"   ✅ Updated description: {updated_ws.description}")

        # 5. Check resource limits
        print("\n5. Checking resource limits...")
        can_add_repo = await service.can_add_repo(personal_ws.id)
        can_add_vault = await service.can_add_vault(personal_ws.id)
        print(f"   Can add repo: {can_add_repo}")
        print(f"   Can add vault: {can_add_vault}")

        # 6. Get workspace stats
        print("\n6. Getting workspace statistics...")
        stats = await service.get_workspace_stats(personal_ws.id)
        print(f"   Repos: {stats.get('repos', 0)}, Vaults: {stats.get('vaults', 0)}")

        return personal_ws, client_ws

    async def demo_repo_service(self, workspace_id, user_id) -> None:
        """Demonstrate RepoService functionality."""
        print("\n" + "=" * 60)
        print("📂 REPO SERVICE DEMO")
        print("=" * 60)

        # Create unit of work and service
        uow = SQLAlchemyUnitOfWork(self.settings)
        service = RepoService(uow)

        # 1. Create repos
        print("\n1. Creating repos...")
        symphony_repo = await service.create_repo(
            workspace_id=workspace_id,
            user_id=user_id,
            name="symphony-backend",
            path="/home/alice/projects/symphony",
            remote_url="https://github.com/alice/symphony.git",
            metadata={"language": "python", "framework": "fastapi"}
        )
        print(f"   ✅ Created repo: {symphony_repo.name} ({symphony_repo.id})")

        frontend_repo = await service.create_repo(
            workspace_id=workspace_id,
            user_id=user_id,
            name="symphony-frontend",
            path="/home/alice/projects/symphony-ui",
            remote_url="https://github.com/alice/symphony-ui.git",
            metadata={"language": "typescript", "framework": "react"}
        )
        print(f"   ✅ Created repo: {frontend_repo.name} ({frontend_repo.id})")

        # 2. Try creating duplicate name
        print("\n2. Testing duplicate repo name...")
        try:
            await service.create_repo(
                workspace_id=workspace_id,
                user_id=user_id,
                name="symphony-backend",  # Duplicate!
                path="/tmp/other"
            )
        except DuplicateRepoNameError as e:
            print(f"   ❌ Expected error: {e}")

        # 3. List workspace repos
        print("\n3. Listing workspace repos...")
        repos = await service.list_workspace_repos(workspace_id, user_id)
        for repo in repos:
            print(f"   - {repo.name}: {repo.remote_url or 'no remote'}")

        # 4. Update repo
        print("\n4. Updating repo...")
        updated_repo = await service.update_repo(
            repo_id=symphony_repo.id,
            user_id=user_id,
            metadata={"language": "python", "framework": "fastapi", "version": "0.1.0"}
        )
        print(f"   ✅ Updated metadata: {updated_repo.metadata}")

        # 5. Sync with remote
        print("\n5. Syncing with remote...")
        synced_repo = await service.sync_with_remote(symphony_repo.id, user_id)
        print(f"   ✅ Last synced: {synced_repo.last_synced}")

        return symphony_repo, frontend_repo

    async def demo_vault_service(self, workspace_id, user_id) -> None:
        """Demonstrate VaultService functionality."""
        print("\n" + "=" * 60)
        print("🔐 VAULT SERVICE DEMO")
        print("=" * 60)

        # Create unit of work and service
        uow = SQLAlchemyUnitOfWork(self.settings)
        service = VaultService(uow)

        # 1. Create vaults
        print("\n1. Creating vaults...")
        env_vault = await service.create_vault(
            workspace_id=workspace_id,
            user_id=user_id,
            name="env-secrets",
            path="/home/alice/.vaults/env",
            metadata={"type": "environment", "encryption": "aes256"}
        )
        print(f"   ✅ Created vault: {env_vault.name} ({env_vault.id})")

        api_vault = await service.create_vault(
            workspace_id=workspace_id,
            user_id=user_id,
            name="api-keys",
            path="/home/alice/.vaults/api",
            metadata={"type": "api_keys", "rotation": "monthly"}
        )
        print(f"   ✅ Created vault: {api_vault.name} ({api_vault.id})")

        # 2. List workspace vaults
        print("\n2. Listing workspace vaults...")
        vaults = await service.list_workspace_vaults(workspace_id, user_id)
        for vault in vaults:
            print(f"   - {vault.name} ({'locked' if vault.is_locked else 'unlocked'})")

        # 3. Lock/unlock vault
        print("\n3. Testing vault locking...")
        locked_vault = await service.lock_vault(env_vault.id, user_id)
        print(f"   ✅ Locked vault: {locked_vault.name} (is_locked={locked_vault.is_locked})")

        unlocked_vault = await service.unlock_vault(env_vault.id, user_id)
        print(f"   ✅ Unlocked vault: {unlocked_vault.name} (is_locked={unlocked_vault.is_locked})")

        # 4. Update vault
        print("\n4. Updating vault...")
        updated_vault = await service.update_vault(
            vault_id=api_vault.id,
            user_id=user_id,
            metadata={"type": "api_keys", "rotation": "weekly", "last_rotation": "2024-01-15"}
        )
        print(f"   ✅ Updated metadata: {updated_vault.metadata}")

        return env_vault, api_vault

    async def demo_cross_service_operations(self) -> None:
        """Demonstrate operations across multiple services."""
        print("\n" + "=" * 60)
        print("🔄 CROSS-SERVICE OPERATIONS DEMO")
        print("=" * 60)

        # Create services
        uow = SQLAlchemyUnitOfWork(self.settings)
        user_service = UserProfileService(uow)
        workspace_service = WorkspaceService(uow)
        repo_service = RepoService(uow)

        # 1. Complete user setup workflow
        print("\n1. Complete user onboarding workflow...")
        
        # Create user
        user = await user_service.create_user_profile(
            username="newbie",
            email="newbie@example.com"
        )
        print(f"   ✅ Created user: {user.username}")

        # Create default workspace
        workspace = await workspace_service.create_workspace(
            user_id=user.id,
            name="Getting Started",
            workspace_type="general",
            description="Default workspace for new users"
        )
        print(f"   ✅ Created default workspace: {workspace.name}")

        # Create example repo
        repo = await repo_service.create_repo(
            workspace_id=workspace.id,
            user_id=user.id,
            name="hello-world",
            path="/tmp/hello-world",
            metadata={"template": "starter"}
        )
        print(f"   ✅ Created starter repo: {repo.name}")

        # 2. Resource limit testing
        print("\n2. Testing resource limits...")
        
        # Try to create many repos (test limit)
        created_count = 1  # Already created one
        max_attempts = 10
        
        for i in range(2, max_attempts + 1):
            try:
                await repo_service.create_repo(
                    workspace_id=workspace.id,
                    user_id=user.id,
                    name=f"test-repo-{i}",
                    path=f"/tmp/test-{i}"
                )
                created_count += 1
            except RepoLimitExceeded:
                print(f"   ❌ Hit repo limit at {created_count} repos")
                break
        
        if created_count == max_attempts:
            print(f"   ✅ Created {created_count} repos (limit not reached in test)")

        # 3. Cleanup demonstration
        print("\n3. Cascading delete demonstration...")
        
        # Delete user (should cascade to workspace, repos, vaults)
        await user_service.delete_user_profile(user.id)
        print("   ✅ Deleted user and all associated data")

        # Verify deletion
        try:
            await user_service.get_user_profile(user.id)
        except UserProfileNotFoundError:
            print("   ✅ Confirmed: User no longer exists")

        try:
            await workspace_service.get_workspace(workspace.id)
        except WorkspaceNotFoundError:
            print("   ✅ Confirmed: Workspace was cascade deleted")

    async def run(self) -> None:
        """Run all demos."""
        try:
            # Setup
            await self.setup_database()

            # Run demos
            alice, bob = await self.demo_user_profile_service()
            personal_ws, client_ws = await self.demo_workspace_service(alice.id, bob.id)
            await self.demo_repo_service(personal_ws.id, alice.id)
            await self.demo_vault_service(client_ws.id, alice.id)
            await self.demo_cross_service_operations()

            print("\n" + "=" * 60)
            print("✅ ALL DOMAIN SERVICES DEMOS COMPLETED SUCCESSFULLY!")
            print("=" * 60)

        finally:
            # Cleanup
            await self.engine.dispose()
            # Remove demo database file
            db_file = Path("demo_services.db")
            if db_file.exists():
                db_file.unlink()
            print("\n🧹 Cleaned up demo database")


async def main() -> None:
    """Run the demo."""
    demo = DemoServices()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())