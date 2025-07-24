"""
Interface protocols for wave_visualizer package.

Defines clear contracts for different components to improve modularity,
testability, and extensibility of the package architecture.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union, Protocol
import pandas as pd
import plotly.graph_objects as go


class DataProcessor(Protocol):
    """Protocol for data processing components."""
    
    def process(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Process the input data and return processed data."""
        ...
    
    def validate_input(self, data: pd.DataFrame) -> bool:
        """Validate that the input data is suitable for processing."""
        ...


class SettingsHandler(Protocol):
    """Protocol for components that handle user settings."""
    
    def load_settings(self) -> bool:
        """Load settings from persistent storage."""
        ...
    
    def save_settings(self) -> bool:
        """Save current settings to persistent storage."""
        ...
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        ...


class VisualizationProvider(Protocol):
    """Protocol for visualization generation components."""
    
    def create_visualization(self, data: pd.DataFrame, **kwargs) -> Tuple[go.Figure, Dict[str, Any]]:
        """Create a visualization from the provided data."""
        ...
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate visualization parameters."""
        ...


class ExportProvider(Protocol):
    """Protocol for export functionality."""
    
    def export(self, figure: go.Figure, filename: str, formats: List[str]) -> Dict[str, str]:
        """Export figure to specified formats."""
        ...
    
    def validate_export_parameters(self, filename: str, formats: List[str]) -> bool:
        """Validate export parameters."""
        ...


class UserInteractionHandler(ABC):
    """Abstract base class for components requiring user interaction."""
    
    @abstractmethod
    def get_user_input(self, prompt: str, options: List[str]) -> str:
        """Get user input with validation."""
        pass
    
    @abstractmethod
    def display_information(self, title: str, content: str) -> None:
        """Display information to the user."""
        pass
    
    @abstractmethod
    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for an action."""
        pass


class DataTransformer(ABC):
    """Abstract base class for data transformation operations."""
    
    @abstractmethod
    def transform_column(self, column_data: pd.Series, column_name: str) -> pd.Series:
        """Transform a single column of data."""
        pass
    
    @abstractmethod
    def can_transform(self, column_data: pd.Series, column_name: str) -> bool:
        """Check if this transformer can handle the given column."""
        pass
    
    def get_transform_name(self) -> str:
        """Get a human-readable name for this transformation."""
        return self.__class__.__name__


class ColorProvider(Protocol):
    """Protocol for color mapping providers."""
    
    def get_colors(self, variable_name: str, values: List[str]) -> List[str]:
        """Get colors for the specified variable values."""
        ...
    
    def add_color_mapping(self, variable_name: str, value_name: str, color: str) -> bool:
        """Add a new color mapping."""
        ...


class WaveConfigProvider(Protocol):
    """Protocol for wave configuration providers."""
    
    def parse_config(self, wave_config: str) -> Tuple[str, str]:
        """Parse wave configuration string."""
        ...
    
    def get_available_waves(self) -> List[int]:
        """Get list of available wave numbers."""
        ...
    
    def add_wave_definition(self, wave_name: str, column_prefix: str) -> bool:
        """Add a new wave definition."""
        ...


class ValidationProvider(Protocol):
    """Protocol for validation providers."""
    
    def validate_dataframe(self, data: pd.DataFrame) -> bool:
        """Validate DataFrame structure and content."""
        ...
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate function parameters."""
        ...


# Builder pattern interfaces
class VisualizationBuilder(ABC):
    """Abstract builder for creating visualizations step by step."""
    
    @abstractmethod
    def set_data(self, data: pd.DataFrame) -> 'VisualizationBuilder':
        """Set the data for visualization."""
        pass
    
    @abstractmethod
    def set_variable(self, variable_name: str) -> 'VisualizationBuilder':
        """Set the variable to visualize."""
        pass
    
    @abstractmethod
    def set_wave_config(self, wave_config: str) -> 'VisualizationBuilder':
        """Set the wave configuration."""
        pass
    
    @abstractmethod
    def apply_filter(self, column: str, value: str) -> 'VisualizationBuilder':
        """Apply a filter to the data."""
        pass
    
    @abstractmethod
    def build(self) -> Tuple[go.Figure, Dict[str, Any]]:
        """Build and return the visualization."""
        pass


class ConfigurationManager(Protocol):
    """Protocol for configuration management."""
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting."""
        ...
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a configuration setting."""
        ...
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """Load configuration from file."""
        ...
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save configuration to file."""
        ...


# Strategy pattern interfaces
class CleaningStrategy(ABC):
    """Abstract strategy for data cleaning operations."""
    
    @abstractmethod
    def apply(self, data: pd.DataFrame, column_name: str, **kwargs) -> pd.DataFrame:
        """Apply the cleaning strategy."""
        pass
    
    @abstractmethod
    def validate_applicability(self, data: pd.DataFrame, column_name: str) -> bool:
        """Check if this strategy is applicable to the data."""
        pass
    
    def get_strategy_name(self) -> str:
        """Get the name of this cleaning strategy."""
        return self.__class__.__name__


class MissingValueStrategy(CleaningStrategy):
    """Strategy for handling missing values."""
    pass


class ValueMergingStrategy(CleaningStrategy):
    """Strategy for merging similar values."""
    pass


class LabelConversionStrategy(CleaningStrategy):
    """Strategy for converting codes to labels."""
    pass


# Factory pattern interfaces
class VisualizationFactory(ABC):
    """Abstract factory for creating visualizations."""
    
    @abstractmethod
    def create_alluvial_plot(self, **kwargs) -> VisualizationProvider:
        """Create an alluvial plot provider."""
        pass
    
    @abstractmethod
    def create_heatmap(self, **kwargs) -> VisualizationProvider:
        """Create a heatmap provider."""
        pass
    
    @abstractmethod
    def create_pattern_analysis(self, **kwargs) -> VisualizationProvider:
        """Create a pattern analysis provider."""
        pass


class HandlerFactory(ABC):
    """Abstract factory for creating data handlers."""
    
    @abstractmethod
    def create_metadata_handler(self) -> DataProcessor:
        """Create a metadata handler."""
        pass
    
    @abstractmethod
    def create_cleaning_handler(self, strategy: CleaningStrategy) -> DataProcessor:
        """Create a cleaning handler with specified strategy."""
        pass
    
    @abstractmethod
    def create_export_handler(self) -> ExportProvider:
        """Create an export handler."""
        pass


# Observer pattern interfaces
class ProgressObserver(Protocol):
    """Protocol for observing processing progress."""
    
    def on_progress_update(self, step: str, progress: float, message: str) -> None:
        """Handle progress updates."""
        ...
    
    def on_step_completed(self, step: str, result: Any) -> None:
        """Handle step completion."""
        ...
    
    def on_error(self, step: str, error: Exception) -> None:
        """Handle errors during processing."""
        ...


class ProgressPublisher(Protocol):
    """Protocol for components that publish progress updates."""
    
    def add_observer(self, observer: ProgressObserver) -> None:
        """Add a progress observer."""
        ...
    
    def remove_observer(self, observer: ProgressObserver) -> None:
        """Remove a progress observer."""
        ...
    
    def notify_progress(self, step: str, progress: float, message: str) -> None:
        """Notify observers of progress."""
        ...


# Command pattern interfaces
class Command(ABC):
    """Abstract command for implementing undo/redo functionality."""
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        """Undo the command."""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Check if the command can be undone."""
        pass


class DataProcessingCommand(Command):
    """Command for data processing operations."""
    
    def __init__(self, processor: DataProcessor, data: pd.DataFrame, **kwargs):
        self.processor = processor
        self.data = data
        self.kwargs = kwargs
        self.result = None
        self.original_data = None
    
    def execute(self) -> pd.DataFrame:
        """Execute the data processing command."""
        self.original_data = self.data.copy()
        self.result = self.processor.process(self.data, **self.kwargs)
        return self.result
    
    def undo(self) -> pd.DataFrame:
        """Undo the data processing command."""
        if self.original_data is not None:
            return self.original_data.copy()
        raise ValueError("Cannot undo: no original data stored")
    
    def can_undo(self) -> bool:
        """Check if the command can be undone."""
        return self.original_data is not None 