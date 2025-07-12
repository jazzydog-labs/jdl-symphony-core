"""Demo script for the application layer with CQRS patterns."""

import asyncio
from datetime import datetime

from symphony.application import ApplicationService
from symphony.application.commands.repo import CreateRepoCommand, SyncRepoCommand, UpdateRepoCommand
from symphony.application.commands.user_profile import CreateUserProfileCommand, UpdateUserProfileCommand
from symphony.application.commands.vault import CreateVaultCommand, LockVaultCommand, UnlockVaultCommand
from symphony.application.commands.workspace import CreateWorkspaceCommand, UpdateWorkspaceCommand
from symphony.application.queries.repo import GetRepoQuery, ListWorkspaceReposQuery
from symphony.application.queries.user_profile import GetUserProfileByUsernameQuery, GetUserProfileQuery
from symphony.application.queries.vault import GetVaultQuery, ListWorkspaceVaultsQuery
from symphony.application.queries.workspace import (
    GetWorkspaceQuery,
    GetWorkspaceStatsQuery,
    ListUserWorkspacesQuery,
)
from symphony.config.demo import get_demo_settings
from symphony.infrastructure.database.base import Base
from symphony.infrastructure.database.connection import get_engine
from symphony.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


async def demo_application_layer() -> None:
    """Demonstrate the application layer with CQRS patterns."""
    print("🎭 Application Layer Demo - CQRS Pattern Implementation")
    print("=" * 60)
    
    # Get demo settings
    settings = get_demo_settings()
    # Use persistent file for this demo
    settings.demo_database_url = "sqlite+aiosqlite:///demo_application.db"
    engine = get_engine(settings)
    
    # Setup database schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database schema created")
    
    # Create unit of work and application service
    uow = SQLAlchemyUnitOfWork(settings)
    app_service = ApplicationService(uow)
    
    print("\n📋 1. User Profile Operations via Commands & Queries")
    print("-" * 50)
    
    # Create user via command
    create_user_cmd = CreateUserProfileCommand(
        username="alice_cqrs",
        email="alice@cqrs.example.com",
        preferences={"theme": "dark", "notifications": True}
    )
    user_dto = await app_service.commands.execute(create_user_cmd)
    print(f"✅ Created user: {user_dto.username} ({user_dto.id})")
    
    # Get user via query
    get_user_query = GetUserProfileQuery(user_id=user_dto.id)
    retrieved_user = await app_service.queries.execute(get_user_query)
    print(f"📖 Retrieved user: {retrieved_user.username} - {retrieved_user.email}")
    
    # Get user by username via query
    get_by_username_query = GetUserProfileByUsernameQuery(username="alice_cqrs")
    user_by_username = await app_service.queries.execute(get_by_username_query)
    print(f"🔍 Found by username: {user_by_username.email}")
    
    # Update user via command
    update_user_cmd = UpdateUserProfileCommand(
        user_id=user_dto.id,
        preferences={"theme": "light", "notifications": False, "language": "en"}
    )
    updated_user = await app_service.commands.execute(update_user_cmd)
    print(f"🔄 Updated preferences: {updated_user.preferences}")
    
    print("\n🏢 2. Workspace Operations via CQRS")
    print("-" * 50)
    
    # Create workspace via command
    create_workspace_cmd = CreateWorkspaceCommand(
        user_id=user_dto.id,
        name="CQRS Demo Workspace",
        workspace_type="research",
        description="Demonstrating CQRS patterns",
        settings={"auto_sync": True, "backup_enabled": True}
    )
    workspace_dto = await app_service.commands.execute(create_workspace_cmd)
    print(f"✅ Created workspace: {workspace_dto.name} ({workspace_dto.id})")
    
    # List user workspaces via query
    list_workspaces_query = ListUserWorkspacesQuery(user_id=user_dto.id)
    user_workspaces = await app_service.queries.execute(list_workspaces_query)
    print(f"📋 User has {len(user_workspaces)} workspace(s)")
    
    # Get workspace stats via query
    stats_query = GetWorkspaceStatsQuery(workspace_id=workspace_dto.id)
    workspace_stats = await app_service.queries.execute(stats_query)
    print(f"📊 Workspace stats: {workspace_stats.repo_count} repos, {workspace_stats.vault_count} vaults")
    
    # Update workspace via command
    update_workspace_cmd = UpdateWorkspaceCommand(
        workspace_id=workspace_dto.id,
        user_id=user_dto.id,
        description="Updated via CQRS command",
        settings={"auto_sync": False, "backup_enabled": True, "max_files": 1000}
    )
    updated_workspace = await app_service.commands.execute(update_workspace_cmd)
    print(f"🔄 Updated workspace description: {updated_workspace.description}")
    
    print("\n📁 3. Repository Operations via CQRS")
    print("-" * 50)
    
    # Create repository via command
    create_repo_cmd = CreateRepoCommand(
        workspace_id=workspace_dto.id,
        user_id=user_dto.id,
        name="cqrs-demo-repo",
        path="/projects/cqrs-demo",
        remote_url="https://github.com/user/cqrs-demo.git",
        metadata={"language": "Python", "framework": "FastAPI"}
    )
    repo_dto = await app_service.commands.execute(create_repo_cmd)
    print(f"✅ Created repo: {repo_dto.name} ({repo_dto.id})")
    
    # Get repo via query
    get_repo_query = GetRepoQuery(repo_id=repo_dto.id, user_id=user_dto.id)
    retrieved_repo = await app_service.queries.execute(get_repo_query)
    print(f"📖 Retrieved repo: {retrieved_repo.name} at {retrieved_repo.path}")
    print(f"🔗 Remote URL: {retrieved_repo.remote_url}")
    print(f"📝 Metadata: {retrieved_repo.metadata}")
    
    # Update repo via command
    update_repo_cmd = UpdateRepoCommand(
        repo_id=repo_dto.id,
        user_id=user_dto.id,
        metadata={"language": "Python", "framework": "FastAPI", "version": "3.11", "tests": "pytest"}
    )
    updated_repo = await app_service.commands.execute(update_repo_cmd)
    print(f"🔄 Updated repo metadata: {updated_repo.metadata}")
    
    # Sync repo via command
    sync_repo_cmd = SyncRepoCommand(repo_id=repo_dto.id, user_id=user_dto.id)
    synced_repo = await app_service.commands.execute(sync_repo_cmd)
    print(f"🔄 Synced repo at: {synced_repo.last_synced}")
    
    # List workspace repos via query
    list_repos_query = ListWorkspaceReposQuery(workspace_id=workspace_dto.id, user_id=user_dto.id)
    workspace_repos = await app_service.queries.execute(list_repos_query)
    print(f"📋 Workspace has {len(workspace_repos)} repo(s)")
    
    print("\n🔐 4. Vault Operations via CQRS")
    print("-" * 50)
    
    # Create vault via command
    create_vault_cmd = CreateVaultCommand(
        workspace_id=workspace_dto.id,
        user_id=user_dto.id,
        name="secrets-vault",
        path="/secure/secrets",
        metadata={"encryption": "AES256", "backup": "daily"}
    )
    vault_dto = await app_service.commands.execute(create_vault_cmd)
    print(f"✅ Created vault: {vault_dto.name} ({vault_dto.id})")
    print(f"🔓 Vault is locked: {vault_dto.is_locked}")
    
    # Get vault via query
    get_vault_query = GetVaultQuery(vault_id=vault_dto.id, user_id=user_dto.id)
    retrieved_vault = await app_service.queries.execute(get_vault_query)
    print(f"📖 Retrieved vault: {retrieved_vault.name} at {retrieved_vault.path}")
    
    # Lock vault via command
    lock_vault_cmd = LockVaultCommand(vault_id=vault_dto.id, user_id=user_dto.id)
    locked_vault = await app_service.commands.execute(lock_vault_cmd)
    print(f"🔒 Locked vault: {locked_vault.is_locked}")
    
    # Unlock vault via command
    unlock_vault_cmd = UnlockVaultCommand(vault_id=vault_dto.id, user_id=user_dto.id)
    unlocked_vault = await app_service.commands.execute(unlock_vault_cmd)
    print(f"🔓 Unlocked vault: {unlocked_vault.is_locked}")
    
    # List workspace vaults via query
    list_vaults_query = ListWorkspaceVaultsQuery(workspace_id=workspace_dto.id, user_id=user_dto.id)
    workspace_vaults = await app_service.queries.execute(list_vaults_query)
    print(f"📋 Workspace has {len(workspace_vaults)} vault(s)")
    
    print("\n📊 5. Final Workspace Statistics")
    print("-" * 50)
    
    # Get final workspace stats
    final_stats = await app_service.queries.execute(stats_query)
    print(f"📈 Final workspace stats:")
    print(f"   - Repositories: {final_stats.repo_count}")
    print(f"   - Vaults: {final_stats.vault_count}")
    print(f"   - Total resources: {final_stats.total_resources}")
    
    print("\n✨ 6. CQRS Pattern Benefits Demonstrated")
    print("-" * 50)
    print("✅ Command/Query Separation: Write operations via commands, reads via queries")
    print("✅ Single Responsibility: Each handler focused on one operation")
    print("✅ Type Safety: Strong typing with DTOs and command/query objects")
    print("✅ Scalability: Commands and queries can be optimized independently")
    print("✅ Testing: Each handler can be unit tested in isolation")
    print("✅ Flexibility: Easy to add new operations without changing existing code")
    
    print(f"\n🎉 Application layer demo completed successfully!")
    print(f"⏰ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(demo_application_layer())