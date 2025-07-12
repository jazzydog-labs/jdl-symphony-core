#!/usr/bin/env python3
"""Demo: API Health Check and Endpoints"""
import asyncio
import sys
from pathlib import Path

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

console = Console()


async def demo_api():
    """Demonstrate API health check and endpoints."""
    console.print("\n[bold blue]🎵 Symphony API Demo[/bold blue]\n")
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            # Test root endpoint
            console.print("📍 Testing root endpoint...")
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                data = response.json()
                console.print(Panel(
                    f"Service: {data['service']}\n"
                    f"Version: {data['version']}\n"
                    f"Docs: {data['docs']}",
                    title="✅ Root Endpoint",
                    border_style="green"
                ))
            
            # Test health check
            console.print("\n🏥 Testing health check endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                
                # Create status table
                table = Table(title="Health Check Status")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green" if data["status"] == "healthy" else "red")
                
                table.add_row("API Service", data["service"])
                table.add_row("Overall Status", data["status"])
                table.add_row("Database", data["database"])
                
                console.print(table)
                
                if "error" in data:
                    console.print(f"\n[yellow]⚠️  Database Error: {data['error']}[/yellow]")
                    console.print("[dim]Note: This is expected if Docker is not running[/dim]")
            
            # Show available endpoints
            console.print("\n📋 Available Endpoints:")
            endpoints_table = Table()
            endpoints_table.add_column("Method", style="cyan")
            endpoints_table.add_column("Path", style="green")
            endpoints_table.add_column("Description")
            
            endpoints_table.add_row("GET", "/", "API information")
            endpoints_table.add_row("GET", "/health", "Health check with database status")
            endpoints_table.add_row("GET", "/api/v1/docs", "Interactive API documentation (coming soon)")
            
            console.print(endpoints_table)
            
    except httpx.ConnectError:
        console.print("[red]❌ Could not connect to API server![/red]")
        console.print("[yellow]Please ensure the server is running with: just run[/yellow]")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(demo_api())