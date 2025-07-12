#!/usr/bin/env python3
"""Demo script showcasing repository pattern and Unit of Work."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from symphony.config.demo import get_demo_settings
from symphony.domain.models import Repo, UserProfile, Vault, Workspace
from symphony.infrastructure.database.base import Base
from symphony.infrastructure.database.connection import get_engine
from symphony.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork

console = Console()


async def demo_repositories():
    """Demonstrate repository pattern implementation."""
    console.print("🎵 Symphony Repository Pattern Demo")
    console.print("=" * 60)

    # Set up demo database with persistent SQLite file for this demo
    demo_settings = get_demo_settings()
    demo_settings.demo_database_url = "sqlite+aiosqlite:///demo_repos.db"
    
    # Get engine and create tables
    engine = get_engine(demo_settings)
    
    # Drop and recreate tables for clean demo
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 1. Create entities using Unit of Work
    console.print("\n1. Creating entities with Unit of Work...")
    
    async with SQLAlchemyUnitOfWork(demo_settings) as uow:
        # Create user
        user = UserProfile(
            id=uuid4(),
            username="alice_dev",
            email="alice@symphony.dev",
            preferences={"theme": "dark", "notifications": True},
        )
        user = await uow.user_profiles.save(user)
        console.print(f"✅ Created user: {user.username}")
        
        # Create workspace
        workspace = Workspace(
            id=uuid4(),
            name="AI Research Lab",
            description="Machine learning experiments and models",
            user_profile_id=user.id,
            workspace_type="research",
            settings={"auto_backup": True},
        )
        workspace = await uow.workspaces.save(workspace)
        console.print(f"✅ Created workspace: {workspace.name}")
        
        # Create repos
        repo1 = Repo(
            id=uuid4(),
            name="neural-nets",
            path="/research/neural-nets",
            workspace_id=workspace.id,
            remote_url="git@github.com:alice/neural-nets.git",
        )
        repo2 = Repo(
            id=uuid4(),
            name="data-pipeline",
            path="/research/data-pipeline",
            workspace_id=workspace.id,
        )
        await uow.repos.save(repo1)
        await uow.repos.save(repo2)
        console.print("✅ Created 2 repos")
        
        # Create vault
        vault = Vault(
            id=uuid4(),
            name="research-notes",
            path="/research/notes",
            workspace_id=workspace.id,
        )
        await uow.vaults.save(vault)
        console.print("✅ Created vault")

    # 2. Query using repositories
    console.print("\n2. Querying with repository methods...")
    
    async with SQLAlchemyUnitOfWork(demo_settings) as uow:
        # Find user by username
        found_user = await uow.user_profiles.get_by_username("alice_dev")
        if found_user:
            console.print(f"✅ Found user by username: {found_user.email}")
        
        # Count workspaces for user
        workspace_count = await uow.user_profiles.count_workspaces(user.id)
        console.print(f"✅ User has {workspace_count} workspace(s)")
        
        # Get workspaces by type
        research_workspaces = await uow.workspaces.get_by_user_and_type(
            user.id, "research"
        )
        console.print(f"✅ Found {len(research_workspaces)} research workspace(s)")
        
        # Count resources in workspace
        resource_counts = await uow.workspaces.count_resources(workspace.id)
        console.print(f"✅ Workspace resources: {resource_counts}")

    # 3. Demonstrate validation queries
    console.print("\n3. Testing validation queries...")
    
    async with SQLAlchemyUnitOfWork(demo_settings) as uow:
        # Check if username exists
        exists = await uow.user_profiles.username_exists("alice_dev")
        console.print(f"✅ Username 'alice_dev' exists: {exists}")
        
        # Check if username exists (excluding current user)
        exists = await uow.user_profiles.username_exists("alice_dev", exclude_id=user.id)
        console.print(f"✅ Username exists (excluding self): {exists}")
        
        # Check if repo name exists in workspace
        exists = await uow.repos.name_exists_in_workspace(workspace.id, "neural-nets")
        console.print(f"✅ Repo 'neural-nets' exists in workspace: {exists}")

    # 4. Demonstrate transaction rollback
    console.print("\n4. Testing transaction rollback...")
    
    try:
        async with SQLAlchemyUnitOfWork(demo_settings) as uow:
            # Create a user
            temp_user = UserProfile(
                id=uuid4(),
                username="temp_user",
                email="temp@example.com",
            )
            await uow.user_profiles.save(temp_user)
            console.print("✅ Created temporary user")
            
            # Force an error to trigger rollback
            raise Exception("Simulated error!")
            
    except Exception:
        console.print("❌ Transaction rolled back due to error")
    
    # Verify rollback worked
    async with SQLAlchemyUnitOfWork(demo_settings) as uow:
        temp_user_exists = await uow.user_profiles.username_exists("temp_user")
        console.print(f"✅ Temporary user exists: {temp_user_exists} (should be False)")

    # 5. Show repository architecture
    console.print("\n5. Repository Architecture:")
    
    architecture_table = Table(title="Clean Architecture Layers")
    architecture_table.add_column("Layer", style="cyan")
    architecture_table.add_column("Component", style="green")
    architecture_table.add_column("Responsibility")
    
    architecture_table.add_row(
        "Domain", 
        "Repository Interfaces",
        "Define contracts without infrastructure details"
    )
    architecture_table.add_row(
        "Domain",
        "Unit of Work Interface",
        "Transaction boundary abstraction"
    )
    architecture_table.add_row(
        "Infrastructure",
        "SQLAlchemy Repositories",
        "Concrete implementations with database logic"
    )
    architecture_table.add_row(
        "Infrastructure",
        "SQLAlchemy Unit of Work",
        "Manages sessions and transactions"
    )
    
    console.print(architecture_table)

    # 6. Show benefits
    console.print("\n6. Repository Pattern Benefits:")
    benefits = [
        "✓ Decouples domain logic from persistence",
        "✓ Enables easy testing with mock repositories",
        "✓ Consistent API across all aggregates",
        "✓ Unit of Work ensures transactional consistency",
        "✓ Easy to swap persistence implementations",
    ]
    
    console.print(Panel("\n".join(benefits), title="Benefits", border_style="green"))

    # 7. Example usage in services
    console.print("\n7. Usage in Domain Services:")
    
    code_example = '''from symphony.domain.unit_of_work import UnitOfWork

class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create_user(self, username: str, email: str) -> UserProfile:
        async with self.uow:
            # Check if username already exists
            if await self.uow.user_profiles.username_exists(username):
                raise ValueError(f"Username {username} already taken")
            
            # Create and save user
            user = UserProfile(username=username, email=email)
            return await self.uow.user_profiles.save(user)'''
    
    console.print(Panel(code_example, title="Service Example", border_style="blue"))

    # Clean up
    await engine.dispose()
    
    # Remove demo database file
    import os
    if os.path.exists("demo_repos.db"):
        os.remove("demo_repos.db")
    
    console.print("\n✨ Repository pattern demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_repositories())