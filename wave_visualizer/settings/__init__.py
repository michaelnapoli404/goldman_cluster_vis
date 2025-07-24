"""
Settings Module

Contains all persistent settings and configurations for the wave visualizer package.
This folder stores user-configured settings that persist across sessions.

Structure:
- metadata_output/: Variable labels and value mappings from metadata_handler
- cleaning_settings/: Missing value handling and data cleaning preferences
- visualization_settings/: Plot colors, themes, and display configurations

All settings are stored as CSV files for easy reading, editing, and sharing.
"""

from pathlib import Path

# Define settings paths for easy access
SETTINGS_DIR = Path(__file__).parent
METADATA_DIR = SETTINGS_DIR / "metadata_output"
CLEANING_DIR = SETTINGS_DIR / "cleaning_settings" 
VISUALIZATION_DIR = SETTINGS_DIR / "visualization_settings"

def get_settings_directory() -> Path:
    """Get the path to the settings directory."""
    return SETTINGS_DIR

def reset_all_settings() -> bool:
    """
    Reset all settings by clearing the settings folders.
    Use with caution - this will remove all saved configurations.
    """
    import shutil
    
    try:
        for subdir in [METADATA_DIR, CLEANING_DIR, VISUALIZATION_DIR]:
            if subdir.exists():
                shutil.rmtree(subdir)
            subdir.mkdir(exist_ok=True)
        
        print("All settings have been reset.")
        return True
    except Exception as e:
        print(f"Error resetting settings: {str(e)}")
        return False

def backup_settings(backup_path: str) -> bool:
    """
    Create a backup of all current settings.
    
    Args:
        backup_path: Path where to save the backup
    """
    import shutil
    
    try:
        backup_dir = Path(backup_path)
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(SETTINGS_DIR, backup_dir)
        print(f"Settings backed up to: {backup_dir}")
        return True
    except Exception as e:
        print(f"Error backing up settings: {str(e)}")
        return False 