"""
Configuration management for wave_visualizer package.

Centralizes all configurable settings, paths, and parameters to improve
maintainability and provide users with easy customization options.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging


@dataclass
class PlotParameters:
    """Configuration for plot appearance and layout."""
    figure_width: int = 1200
    figure_height: int = 600
    title_size: int = 20
    label_size: int = 12
    node_thickness: int = 20
    node_padding: int = 15
    link_opacity: float = 0.6
    margin_left: int = 50
    margin_right: int = 50
    margin_top: int = 80
    margin_bottom: int = 50


@dataclass
class ExportSettings:
    """Configuration for file export options."""
    default_formats: list = None
    image_width: int = 1200
    image_height: int = 800
    image_scale: int = 2
    exports_folder_name: str = "exports"
    
    def __post_init__(self):
        if self.default_formats is None:
            self.default_formats = ["html", "png"]


@dataclass
class LoggingConfig:
    """Configuration for logging behavior."""
    default_level: str = "INFO"
    console_output: bool = True
    log_format: str = "INFO | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 3


@dataclass
class DataPaths:
    """Configuration for data file paths and directories."""
    settings_dir: Optional[Path] = None
    cleaning_settings_dir: Optional[Path] = None
    visualization_settings_dir: Optional[Path] = None
    metadata_output_dir: Optional[Path] = None
    processed_data_file: Optional[Path] = None
    
    def __post_init__(self):
        # Set default paths if not provided
        if self.settings_dir is None:
            package_dir = Path(__file__).parent
            self.settings_dir = package_dir / "settings"
        
        if self.cleaning_settings_dir is None:
            self.cleaning_settings_dir = self.settings_dir / "cleaning_settings"
        
        if self.visualization_settings_dir is None:
            self.visualization_settings_dir = self.settings_dir / "visualization_settings"
        
        if self.metadata_output_dir is None:
            self.metadata_output_dir = self.settings_dir / "metadata_output"
        
        if self.processed_data_file is None:
            self.processed_data_file = self.settings_dir / "processed_data.csv"


@dataclass
class WaveVisualizerConfig:
    """Main configuration class containing all package settings."""
    plot_params: PlotParameters = None
    export_settings: ExportSettings = None
    logging_config: LoggingConfig = None
    data_paths: DataPaths = None
    
    # Additional package-wide settings
    auto_save_settings: bool = True
    validate_data_on_load: bool = True
    default_missing_strategy: str = "mark_unknown"
    max_unique_values_for_categorical: int = 20
    
    def __post_init__(self):
        if self.plot_params is None:
            self.plot_params = PlotParameters()
        if self.export_settings is None:
            self.export_settings = ExportSettings()
        if self.logging_config is None:
            self.logging_config = LoggingConfig()
        if self.data_paths is None:
            self.data_paths = DataPaths()


class ConfigManager:
    """Manages configuration loading, saving, and access."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to custom configuration file (optional)
        """
        self._config = WaveVisualizerConfig()
        self._config_file = config_file
        self._user_config_dir = Path.home() / ".wave_visualizer"
        self._default_config_file = self._user_config_dir / "config.json"
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or use defaults."""
        config_path = self._config_file or self._default_config_file
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                self._update_config_from_dict(config_data)
            except Exception as e:
                # Fall back to defaults if config loading fails
                logging.warning(f"Failed to load config from {config_path}: {e}")
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from a dictionary."""
        # Update plot parameters
        if 'plot_params' in config_dict:
            for key, value in config_dict['plot_params'].items():
                if hasattr(self._config.plot_params, key):
                    setattr(self._config.plot_params, key, value)
        
        # Update export settings
        if 'export_settings' in config_dict:
            for key, value in config_dict['export_settings'].items():
                if hasattr(self._config.export_settings, key):
                    setattr(self._config.export_settings, key, value)
        
        # Update logging config
        if 'logging_config' in config_dict:
            for key, value in config_dict['logging_config'].items():
                if hasattr(self._config.logging_config, key):
                    setattr(self._config.logging_config, key, value)
        
        # Update package-wide settings
        for key in ['auto_save_settings', 'validate_data_on_load', 
                    'default_missing_strategy', 'max_unique_values_for_categorical']:
            if key in config_dict:
                setattr(self._config, key, config_dict[key])
    
    def save_config(self, config_file: Optional[str] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            config_file: Path to save configuration to (optional)
            
        Returns:
            bool: True if save was successful
        """
        save_path = config_file or self._default_config_file
        save_path = Path(save_path)
        
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary
            config_dict = {
                'plot_params': asdict(self._config.plot_params),
                'export_settings': asdict(self._config.export_settings),
                'logging_config': asdict(self._config.logging_config),
                'auto_save_settings': self._config.auto_save_settings,
                'validate_data_on_load': self._config.validate_data_on_load,
                'default_missing_strategy': self._config.default_missing_strategy,
                'max_unique_values_for_categorical': self._config.max_unique_values_for_categorical
            }
            
            # Save to JSON file
            with open(save_path, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save config to {save_path}: {e}")
            return False
    
    @property
    def config(self) -> WaveVisualizerConfig:
        """Get the current configuration."""
        return self._config
    
    def get_plot_params(self) -> PlotParameters:
        """Get plot parameters configuration."""
        return self._config.plot_params
    
    def get_export_settings(self) -> ExportSettings:
        """Get export settings configuration."""
        return self._config.export_settings
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self._config.logging_config
    
    def get_data_paths(self) -> DataPaths:
        """Get data paths configuration."""
        return self._config.data_paths
    
    def update_plot_params(self, **kwargs) -> None:
        """Update plot parameters."""
        for key, value in kwargs.items():
            if hasattr(self._config.plot_params, key):
                setattr(self._config.plot_params, key, value)
        
        if self._config.auto_save_settings:
            self.save_config()
    
    def update_export_settings(self, **kwargs) -> None:
        """Update export settings."""
        for key, value in kwargs.items():
            if hasattr(self._config.export_settings, key):
                setattr(self._config.export_settings, key, value)
        
        if self._config.auto_save_settings:
            self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = WaveVisualizerConfig()


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> WaveVisualizerConfig:
    """Get the current configuration."""
    return get_config_manager().config


def configure_package(**kwargs) -> None:
    """
    Configure package settings.
    
    Args:
        **kwargs: Configuration parameters to update
    """
    manager = get_config_manager()
    
    # Update appropriate configuration sections
    if any(key in kwargs for key in ['figure_width', 'figure_height', 'title_size']):
        plot_kwargs = {k: v for k, v in kwargs.items() 
                       if hasattr(manager.get_plot_params(), k)}
        if plot_kwargs:
            manager.update_plot_params(**plot_kwargs)
    
    if any(key in kwargs for key in ['default_formats', 'image_width', 'image_scale']):
        export_kwargs = {k: v for k, v in kwargs.items() 
                         if hasattr(manager.get_export_settings(), k)}
        if export_kwargs:
            manager.update_export_settings(**export_kwargs) 