#!/usr/bin/env python3
"""Demo: Database Connection and Alembic"""
import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from sqlalchemy import text

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from symphony.config.demo import get_demo_settings
from symphony.infrastructure.database.connection import get_engine, get_db

console = Console()


async def demo_database():
    """Demonstrate database connection and setup."""
    console.print("\n[bold blue]🗄️  Symphony Database Demo[/bold blue]\n")
    
    # Use demo settings
    demo_settings = get_demo_settings()
    engine = get_engine(demo_settings)
    
    # Show database architecture
    console.print("📐 Database Architecture:")
    console.print("   • SQLAlchemy 2.0 with async support")
    console.print("   • PostgreSQL with asyncpg driver (production)")
    console.print("   • SQLite in-memory for demos")
    console.print("   • Connection pooling (size=10, overflow=20)")
    console.print("   • Alembic for migrations\n")
    
    # Test database connection
    console.print("🔌 Testing Demo Database Connection...")
    console.print(f"   [dim]Using: {demo_settings.demo_database_url}[/dim]\n")
    
    try:
        async with engine.connect() as conn:
            # SQLite version query
            result = await conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            
            console.print(Panel(
                f"✅ Connected to Demo Database (SQLite)\n\nVersion: {version}",
                title="Database Status",
                border_style="green"
            ))
            
            # Show connection details
            console.print("\n📊 Connection Details:")
            details_table = Table()
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="green")
            
            details_table.add_row("Engine", "AsyncEngine (sqlalchemy.ext.asyncio)")
            details_table.add_row("Database", "SQLite (in-memory)")
            details_table.add_row("Demo Mode", "Yes")
            details_table.add_row("Pool Pre-ping", "Enabled")
            details_table.add_row("Echo SQL", str(demo_settings.debug))
            
            console.print(details_table)
            
    except Exception as e:
        console.print(Panel(
            f"❌ Could not connect to database\n\nError: {str(e)}",
            title="Database Status",
            border_style="red"
        ))
    
    # Show session management
    console.print("\n🔄 Session Management:")
    code = '''async def get_db(settings: Settings | None = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Args:
        settings: Optional settings to override defaults (e.g., for demo mode)
    """
    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()'''
    
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Session Lifecycle", border_style="blue"))
    
    # Show demo configuration
    console.print("\n🎯 Demo Configuration:")
    demo_code = '''from symphony.config.demo import get_demo_settings

# Get settings configured for demo mode
demo_settings = get_demo_settings()

# Create engine/session with demo database
engine = get_engine(demo_settings)
async for session in get_db(demo_settings):
    # Use session with in-memory database
    pass'''
    
    syntax = Syntax(demo_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Using Demo Mode", border_style="green"))
    
    # Show Alembic setup
    console.print("\n📦 Alembic Migration Setup:")
    console.print("   ✓ Async migrations support")
    console.print("   ✓ Auto-generate from models")
    console.print("   ✓ Version control for schema")
    console.print("   ✓ Demo mode uses SQLite (no migrations needed)")
    
    alembic_commands = Table(title="Migration Commands (Production)")
    alembic_commands.add_column("Command", style="cyan")
    alembic_commands.add_column("Description")
    
    alembic_commands.add_row("just db-migrate", "Apply pending migrations")
    alembic_commands.add_row("just db-revision \"name\"", "Create new migration")
    alembic_commands.add_row("alembic history", "View migration history")
    alembic_commands.add_row("alembic downgrade -1", "Rollback one migration")
    
    console.print(alembic_commands)
    
    # Show usage example
    console.print("\n💡 Usage in FastAPI:")
    fastapi_code = '''from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from symphony.infrastructure.database.connection import get_db

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()'''
    
    syntax = Syntax(fastapi_code, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="FastAPI Integration", border_style="green"))
    
    # Clean up
    await engine.dispose()
    
    return True


if __name__ == "__main__":
    asyncio.run(demo_database())