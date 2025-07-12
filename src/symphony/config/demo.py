"""Demo configuration utilities."""

import os

from symphony.config.settings import Settings


def get_demo_settings() -> Settings:
    """
    Get settings configured for demo mode.
    
    This returns settings that:
    - Use an in-memory SQLite database
    - Have demo_mode=True flag set
    - Use safe default values for required fields
    """
    # Check if real settings are available
    if os.getenv("POSTGRES_SERVER"):
        # If real settings exist, just override demo_mode
        settings = Settings()
        settings.demo_mode = True
        return settings
    
    # Otherwise create demo settings with safe defaults
    return Settings(
        postgres_server="demo-not-used",
        postgres_user="demo-not-used", 
        postgres_password="demo-not-used",
        postgres_db="demo-not-used",
        secret_key="demo-secret-key-not-for-production",
        demo_mode=True,
        debug=True,  # Enable SQL echo for demos
    )