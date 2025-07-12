#!/usr/bin/env python3
"""Run all Symphony demos in sequence."""
import asyncio
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# List of demos to run
DEMOS = [
    ("Configuration System", "demo_config.py", False),
    ("Domain Models", "demo_domain_models.py", False),
    ("Database Models & ORM Mapping", "demo_database_models.py", False),
    ("Repository Pattern & Unit of Work", "demo_repositories.py", False),
    ("Database Connection", "demo_database.py", True),
    ("API Endpoints", "demo_api.py", True),
]


def check_server_running():
    """Check if the API server is running."""
    import httpx
    try:
        response = httpx.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


async def start_server():
    """Start the API server in the background."""
    console.print("\n[yellow]🚀 Starting API server...[/yellow]")
    
    # Start server process
    process = await asyncio.create_subprocess_exec(
        "uv", "run", "uvicorn", "symphony.main:app", 
        "--host", "0.0.0.0", "--port", "8000",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent.parent
    )
    
    # Wait for server to be ready
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Waiting for server to start...", total=None)
        
        for _ in range(30):  # Wait up to 30 seconds
            if check_server_running():
                progress.update(task, description="[green]✓ Server is ready!")
                await asyncio.sleep(1)
                return process
            await asyncio.sleep(1)
    
    console.print("[red]❌ Server failed to start![/red]")
    return None


async def run_all_demos():
    """Run all demos in sequence."""
    console.print(Panel(
        "[bold blue]🎼 Symphony Demo Suite[/bold blue]\n\n"
        "This will demonstrate all implemented features:\n"
        "• Configuration System\n"
        "• Domain Models with Business Logic\n"
        "• Database Models & ORM Mapping\n"
        "• Repository Pattern & Unit of Work\n"
        "• Database Connection & Alembic\n"
        "• API Health Check & Endpoints",
        border_style="blue"
    ))
    
    # Check if we need to start the server
    server_process = None
    needs_server = any(demo[2] for demo in DEMOS)
    
    if needs_server and not check_server_running():
        server_process = await start_server()
        if not server_process:
            console.print("[red]Cannot run demos that require the server.[/red]")
            return
    
    # Run each demo
    for i, (name, script, requires_server) in enumerate(DEMOS, 1):
        if requires_server and not check_server_running():
            console.print(f"\n[yellow]⚠️  Skipping {name} - server not running[/yellow]")
            continue
            
        console.print(f"\n[bold cyan]━━━ Demo {i}/{len(DEMOS)}: {name} ━━━[/bold cyan]")
        
        # Run the demo script
        demo_path = Path(__file__).parent / script
        result = subprocess.run(
            [sys.executable, str(demo_path)],
            capture_output=False
        )
        
        if result.returncode != 0:
            console.print(f"[red]❌ Demo failed: {name}[/red]")
        
        # Pause between demos
        if i < len(DEMOS):
            console.print("\n[dim]Press Enter to continue to next demo...[/dim]")
            input()
    
    # Cleanup
    if server_process:
        console.print("\n[yellow]🛑 Stopping API server...[/yellow]")
        server_process.terminate()
        await server_process.wait()
    
    # Summary
    console.print(Panel(
        "[bold green]✅ Demo Suite Complete![/bold green]\n\n"
        "You've seen:\n"
        "• Pydantic-based configuration with validation\n"
        "• Domain models with business logic and validation\n"
        "• SQLAlchemy ORM models with relationships\n"
        "• Domain-to-database model mapping\n"
        "• Async SQLAlchemy database setup\n"
        "• FastAPI application structure\n"
        "• Health monitoring endpoints\n\n"
        "[dim]Next: Repository implementations and CRUD operations[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    try:
        asyncio.run(run_all_demos())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")