#!/usr/bin/env python3
"""Demo: Configuration System"""
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from symphony.config import get_settings

console = Console()


def demo_config():
    """Demonstrate the configuration system."""
    console.print("\n[bold blue]⚙️  Symphony Configuration Demo[/bold blue]\n")
    
    # Load settings
    settings = get_settings()
    
    # Show configuration sources
    console.print("📁 Configuration Sources:")
    console.print("   • Environment variables")
    console.print("   • .env file")
    console.print("   • Default values\n")
    
    # Display current configuration
    config_table = Table(title="Current Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Type", style="dim")
    
    # API Settings
    config_table.add_row("API Version", settings.api_v1_str, "str")
    config_table.add_row("Project Name", settings.project_name, "str")
    config_table.add_row("Debug Mode", str(settings.debug), "bool")
    
    # Database Settings
    config_table.add_row("Database Server", settings.postgres_server, "str")
    config_table.add_row("Database Port", str(settings.postgres_port), "int")
    config_table.add_row("Database Name", settings.postgres_db, "str")
    config_table.add_row("Database User", settings.postgres_user, "str")
    config_table.add_row("Database Password", "***hidden***", "str")
    
    # Security Settings
    config_table.add_row("Algorithm", settings.algorithm, "str")
    config_table.add_row("Token Expiry", f"{settings.access_token_expire_minutes} minutes", "int")
    
    # CORS Settings
    config_table.add_row("CORS Origins", ", ".join(settings.backend_cors_origins), "list[str]")
    
    console.print(config_table)
    
    # Show Pydantic validation
    console.print("\n🛡️  Pydantic Validation Features:")
    validation_features = [
        "✓ Type validation and coercion",
        "✓ Environment variable loading",
        "✓ Field validators for custom logic",
        "✓ Automatic database URL assembly",
        "✓ CORS origins parsing from comma-separated strings"
    ]
    for feature in validation_features:
        console.print(f"   {feature}")
    
    # Show example code
    console.print("\n📝 Example Usage:")
    code = '''from symphony.config import get_settings

# Get cached settings instance
settings = get_settings()

# Access configuration values
print(f"API running on: {settings.api_v1_str}")
print(f"Database URL: {settings.database_url}")

# Settings are validated and type-safe
print(f"Debug mode: {settings.debug}")  # bool
print(f"Port: {settings.postgres_port}")  # int'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Configuration Usage", border_style="blue"))
    
    # Show environment variable override
    console.print("\n🔧 Environment Variable Override:")
    console.print("   You can override any setting via environment variables:")
    console.print("   [dim]export POSTGRES_PORT=5433[/dim]")
    console.print("   [dim]export DEBUG=false[/dim]")
    console.print("   [dim]export BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001[/dim]")
    
    return True


if __name__ == "__main__":
    demo_config()