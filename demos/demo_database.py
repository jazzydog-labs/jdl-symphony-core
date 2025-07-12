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

from symphony.infrastructure.database.connection import engine, get_db

console = Console()


async def demo_database():
    """Demonstrate database connection and setup."""
    console.print("\n[bold blue]🗄️  Symphony Database Demo[/bold blue]\n")
    
    # Show database architecture
    console.print("📐 Database Architecture:")
    console.print("   • SQLAlchemy 2.0 with async support")
    console.print("   • PostgreSQL with asyncpg driver")
    console.print("   • Connection pooling (size=10, overflow=20)")
    console.print("   • Alembic for migrations\n")
    
    # Test database connection
    console.print("🔌 Testing Database Connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            
            console.print(Panel(
                f"✅ Connected to PostgreSQL\n\nVersion: {version}",
                title="Database Status",
                border_style="green"
            ))
            
            # Show connection details
            console.print("\n📊 Connection Details:")
            details_table = Table()
            details_table.add_column("Property", style="cyan")
            details_table.add_column("Value", style="green")
            
            details_table.add_row("Engine", "AsyncEngine (sqlalchemy.ext.asyncio)")
            details_table.add_row("Pool Size", "10")
            details_table.add_row("Max Overflow", "20")
            details_table.add_row("Pool Pre-ping", "Enabled")
            details_table.add_row("Echo SQL", "Follows debug setting")
            
            console.print(details_table)
            
    except Exception as e:
        console.print(Panel(
            f"❌ Could not connect to database\n\nError: {str(e)}",
            title="Database Status",
            border_style="red"
        ))
        console.print("\n[yellow]💡 To start the database:[/yellow]")
        console.print("   1. Ensure Docker is running")
        console.print("   2. Run: [bold]just db-up[/bold]")
    
    # Show session management
    console.print("\n🔄 Session Management:")
    code = '''async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
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
    
    # Show Alembic setup
    console.print("\n📦 Alembic Migration Setup:")
    console.print("   ✓ Async migrations support")
    console.print("   ✓ Auto-generate from models")
    console.print("   ✓ Version control for schema")
    
    alembic_commands = Table(title="Migration Commands")
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
    
    return True


if __name__ == "__main__":
    asyncio.run(demo_database())