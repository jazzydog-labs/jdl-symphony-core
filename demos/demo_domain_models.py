#!/usr/bin/env python3
"""Demo script to showcase Symphony domain models and business rules."""

import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from symphony.domain import (
    InvalidEmailError,
    InvalidUsernameError,
    Repo,
    UserProfile,
    ValidationError,
    Vault,
    Workspace,
    WorkspaceType,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}\n")


def demo_user_profile() -> UserProfile:
    """Demonstrate UserProfile creation and validation."""
    print_section("UserProfile Domain Model")
    
    # Create a valid user profile
    print("Creating a valid user profile...")
    user = UserProfile(
        id=uuid4(),
        username="john_doe",
        email="john.doe@example.com",
        preferences={"theme": "dark", "language": "en"},
    )
    print(f"✓ Created user: {user.username} ({user.email})")
    print(f"  ID: {user.id}")
    print(f"  Created: {user.created_at}")
    
    # Demonstrate username validation
    print("\nTesting username validation...")
    invalid_usernames = ["ab", "123start", "user@name", "user name", ""]
    for username in invalid_usernames:
        try:
            UserProfile(username=username, email="test@example.com")
        except ValueError as e:
            print(f"✗ Invalid username '{username}': {e}")
    
    # Demonstrate email validation
    print("\nTesting email validation...")
    invalid_emails = ["notanemail", "@example.com", "user@", "user@domain", ""]
    for email in invalid_emails:
        try:
            UserProfile(username="validuser", email=email)
        except ValueError as e:
            print(f"✗ Invalid email '{email}': {e}")
    
    # Demonstrate business rules
    print("\nTesting business rules...")
    print(f"Can create workspace (0 existing): {user.can_create_workspace(0)}")
    print(f"Can create workspace (49 existing): {user.can_create_workspace(49)}")
    print(f"Can create workspace (50 existing): {user.can_create_workspace(50)}")
    
    # Demonstrate updates
    print("\nUpdating user preferences...")
    user.update_preferences({"notifications": True, "theme": "light"})
    print(f"✓ Updated preferences: {user.preferences}")
    print(f"  Updated at: {user.updated_at}")
    
    return user


def demo_workspace(user_id: uuid4) -> Workspace:
    """Demonstrate Workspace creation and validation."""
    print_section("Workspace Domain Model")
    
    # Create workspaces of different types
    print("Creating workspaces of different types...")
    workspaces = []
    
    for ws_type in ["general", "client", "personal", "research"]:
        workspace = Workspace(
            id=uuid4(),
            name=f"My {ws_type.title()} Workspace",
            description=f"A workspace for {ws_type} work",
            user_profile_id=user_id,
            workspace_type=ws_type,  # type: ignore
            settings={"auto_save": True},
        )
        workspaces.append(workspace)
        print(f"✓ Created {ws_type} workspace: {workspace.name}")
        print(f"  ID: {workspace.id}")
        print(f"  Type: {workspace.workspace_type}")
    
    # Test workspace name validation
    print("\nTesting workspace name validation...")
    invalid_names = ["", "   ", "a" * 256]
    for name in invalid_names:
        try:
            Workspace(name=name, user_profile_id=user_id)
        except ValueError as e:
            print(f"✗ Invalid workspace name: {e}")
    
    # Test business rules
    workspace = workspaces[0]
    print("\nTesting workspace business rules...")
    print(f"Can delete (no resources): {workspace.can_be_deleted(False)}")
    print(f"Can delete (has resources): {workspace.can_be_deleted(True)}")
    
    # Demonstrate shared resources
    print("\nAdding shared resources...")
    template_id = uuid4()
    contact_id = uuid4()
    workspace.add_shared_resource(template_id, "template")
    workspace.add_shared_resource(contact_id, "contact")
    print(f"✓ Added shared resources: {workspace.shared_resources}")
    
    # Update workspace
    print("\nUpdating workspace...")
    workspace.rename("Updated Workspace Name")
    workspace.update_description("This is an updated description")
    workspace.update_settings({"auto_save": False, "sync_enabled": True})
    print(f"✓ Updated workspace: {workspace.name}")
    print(f"  Description: {workspace.description}")
    print(f"  Settings: {workspace.settings}")
    
    return workspace


def demo_repo(workspace_id: uuid4) -> Repo:
    """Demonstrate Repo creation and validation."""
    print_section("Repo Domain Model")
    
    # Create a valid repo
    print("Creating a repository...")
    repo = Repo(
        id=uuid4(),
        name="my-awesome-project",
        path="/home/user/projects/my-awesome-project",
        workspace_id=workspace_id,
        remote_url="https://github.com/user/my-awesome-project.git",
    )
    print(f"✓ Created repo: {repo.name}")
    print(f"  ID: {repo.id}")
    print(f"  Path: {repo.path}")
    print(f"  Remote: {repo.remote_url}")
    
    # Test name validation
    print("\nTesting repo name validation...")
    invalid_names = ["", "repo/with/slash", "repo:name", "repo?name", "repo*name"]
    for name in invalid_names:
        try:
            Repo(name=name, path="/valid/path", workspace_id=workspace_id)
        except ValueError as e:
            print(f"✗ Invalid repo name: {e}")
    
    # Test remote URL validation
    print("\nTesting remote URL validation...")
    valid_urls = [
        "https://github.com/user/repo.git",
        "git@github.com:user/repo.git",
        "ssh://git@github.com/user/repo.git",
        "git://github.com/user/repo.git",
        "user@host:path/to/repo.git",
    ]
    
    for url in valid_urls:
        test_repo = Repo(
            name="test-repo",
            path="/test/path",
            workspace_id=workspace_id,
            remote_url=url,
        )
        print(f"✓ Valid remote URL: {url}")
    
    invalid_urls = ["not-a-url", "ftp://invalid.com/repo", "/local/path"]
    for url in invalid_urls:
        try:
            Repo(
                name="test-repo",
                path="/test/path",
                workspace_id=workspace_id,
                remote_url=url,
            )
        except ValueError as e:
            print(f"✗ Invalid remote URL '{url}': {e}")
    
    # Update repo
    print("\nUpdating repository...")
    repo.update_remote_url("git@gitlab.com:user/my-awesome-project.git")
    repo.rename("my-super-project")
    print(f"✓ Updated repo: {repo.name}")
    print(f"  New remote: {repo.remote_url}")
    print(f"  Updated at: {repo.updated_at}")
    
    return repo


def demo_vault(workspace_id: uuid4) -> Vault:
    """Demonstrate Vault creation and validation."""
    print_section("Vault Domain Model")
    
    # Create a valid vault
    print("Creating a vault...")
    vault = Vault(
        id=uuid4(),
        name="secure-notes",
        path="/home/user/vaults/secure-notes",
        workspace_id=workspace_id,
    )
    print(f"✓ Created vault: {vault.name}")
    print(f"  ID: {vault.id}")
    print(f"  Path: {vault.path}")
    
    # Test name validation (similar to repo)
    print("\nTesting vault name validation...")
    invalid_names = ["", "vault/with/slash", "vault:name", "vault?name"]
    for name in invalid_names:
        try:
            Vault(name=name, path="/valid/path", workspace_id=workspace_id)
        except ValueError as e:
            print(f"✗ Invalid vault name: {e}")
    
    # Test path validation
    print("\nTesting vault path validation...")
    invalid_paths = ["", "   "]
    for path in invalid_paths:
        try:
            Vault(name="valid-name", path=path, workspace_id=workspace_id)
        except ValueError as e:
            print(f"✗ Invalid vault path: {e}")
    
    # Update vault
    print("\nUpdating vault...")
    vault.rename("personal-notes")
    vault.update_path("/home/user/vaults/personal-notes")
    print(f"✓ Updated vault: {vault.name}")
    print(f"  New path: {vault.path}")
    print(f"  Updated at: {vault.updated_at}")
    
    return vault


def demo_aggregate_relationships() -> None:
    """Demonstrate relationships between aggregates."""
    print_section("Aggregate Relationships")
    
    # Create a user
    user = UserProfile(
        username="demo_user",
        email="demo@example.com",
        preferences={"demo": True},
    )
    print(f"Created user: {user.username}")
    
    # Create multiple workspaces for the user
    workspaces = []
    for i, ws_type in enumerate(["client", "personal", "research"]):
        workspace = Workspace(
            name=f"{ws_type.title()} Projects",
            description=f"Workspace for {ws_type} work",
            user_profile_id=user.id,
            workspace_type=ws_type,  # type: ignore
        )
        workspaces.append(workspace)
        print(f"  └─ Created workspace: {workspace.name} (type: {workspace.workspace_type})")
        
        # Add repos and vaults to each workspace
        for j in range(2):
            repo = Repo(
                name=f"{ws_type}-project-{j+1}",
                path=f"/projects/{ws_type}/project-{j+1}",
                workspace_id=workspace.id,
            )
            print(f"      ├─ Added repo: {repo.name}")
            
            vault = Vault(
                name=f"{ws_type}-vault-{j+1}",
                path=f"/vaults/{ws_type}/vault-{j+1}",
                workspace_id=workspace.id,
            )
            print(f"      └─ Added vault: {vault.name}")
    
    print(f"\nTotal structure:")
    print(f"- 1 UserProfile")
    print(f"- 3 Workspaces (independent contexts)")
    print(f"- 6 Repos (2 per workspace)")
    print(f"- 6 Vaults (2 per workspace)")


def main() -> None:
    """Run all domain model demos."""
    print("\n" + "=" * 60)
    print("Symphony Domain Models Demo".center(60))
    print("=" * 60)
    print("\nThis demo showcases the domain models and their business rules.")
    print("Phase 0 focuses on pure domain logic without persistence.\n")
    
    try:
        # Demo each aggregate
        user = demo_user_profile()
        workspace = demo_workspace(user.id)
        repo = demo_repo(workspace.id)
        vault = demo_vault(workspace.id)
        
        # Demo relationships
        demo_aggregate_relationships()
        
        print_section("Demo Complete!")
        print("✓ All domain models demonstrated successfully")
        print("✓ Validation rules enforced")
        print("✓ Business logic implemented")
        print("\nNext steps: Implement persistence layer with repositories")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()