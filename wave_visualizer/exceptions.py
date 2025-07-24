"""
Custom exception classes for wave_visualizer package.

Provides specific, informative exceptions for different error conditions
to improve debugging and user experience.
"""


class WaveVisualizerError(Exception):
    """Base exception class for all wave_visualizer errors."""
    
    def __init__(self, message: str, details: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Main error message
            details: Additional technical details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class DataLoadingError(WaveVisualizerError):
    """Raised when data cannot be loaded or is invalid."""
    pass


class DataValidationError(WaveVisualizerError):
    """Raised when data fails validation checks."""
    pass


class ColumnNotFoundError(WaveVisualizerError):
    """Raised when a required column is not found in the dataset."""
    
    def __init__(self, column_name: str, available_columns: list = None):
        self.column_name = column_name
        self.available_columns = available_columns or []
        
        message = f"Column '{column_name}' not found in dataset"
        if available_columns:
            suggestions = [col for col in available_columns if column_name.lower() in col.lower()]
            if suggestions:
                message += f". Did you mean: {', '.join(suggestions[:3])}?"
            else:
                message += f". Available columns: {', '.join(available_columns[:5])}"
                if len(available_columns) > 5:
                    message += f" (and {len(available_columns) - 5} more)"
        
        super().__init__(message)


class WaveConfigurationError(WaveVisualizerError):
    """Raised when wave configuration is invalid or unsupported."""
    
    def __init__(self, wave_config: str, supported_formats: list = None):
        self.wave_config = wave_config
        self.supported_formats = supported_formats or []
        
        message = f"Invalid wave configuration: '{wave_config}'"
        if supported_formats:
            message += f". Supported formats: {', '.join(supported_formats)}"
        
        super().__init__(message)


class VisualizationError(WaveVisualizerError):
    """Raised when visualization creation fails."""
    pass


class ExportError(WaveVisualizerError):
    """Raised when file export fails."""
    
    def __init__(self, filepath: str, format_type: str, original_error: Exception = None):
        self.filepath = filepath
        self.format_type = format_type
        self.original_error = original_error
        
        message = f"Failed to export {format_type.upper()} to '{filepath}'"
        if original_error:
            message += f": {str(original_error)}"
        
        super().__init__(message)


class MetadataError(WaveVisualizerError):
    """Raised when metadata processing fails."""
    pass


class SettingsError(WaveVisualizerError):
    """Raised when configuration or settings are invalid."""
    pass


class CleaningPipelineError(WaveVisualizerError):
    """Raised when data cleaning pipeline fails."""
    
    def __init__(self, step_name: str, original_error: Exception = None):
        self.step_name = step_name
        self.original_error = original_error
        
        message = f"Data cleaning failed at step: {step_name}"
        if original_error:
            message += f": {str(original_error)}"
        
        super().__init__(message)


class ColorMappingError(WaveVisualizerError):
    """Raised when color mapping operations fail."""
    pass


class FilteringError(WaveVisualizerError):
    """Raised when data filtering operations fail."""
    
    def __init__(self, filter_column: str, filter_value: str, available_values: list = None):
        self.filter_column = filter_column
        self.filter_value = filter_value
        self.available_values = available_values or []
        
        message = f"Filtering failed: '{filter_value}' not found in column '{filter_column}'"
        if available_values:
            suggestions = [val for val in available_values if str(filter_value).lower() in str(val).lower()]
            if suggestions:
                message += f". Did you mean: {', '.join(map(str, suggestions[:3]))}?"
            else:
                message += f". Available values: {', '.join(map(str, available_values[:5]))}"
                if len(available_values) > 5:
                    message += f" (and {len(available_values) - 5} more)"
        
        super().__init__(message)


# Utility functions for exception handling
def validate_column_exists(dataframe, column_name: str, context: str = "operation"):
    """
    Validate that a column exists in the dataframe.
    
    Args:
        dataframe: pandas DataFrame to check
        column_name: Name of the column to validate
        context: Context description for better error messages
        
    Raises:
        ColumnNotFoundError: If column is not found
    """
    if column_name not in dataframe.columns:
        raise ColumnNotFoundError(
            column_name=column_name,
            available_columns=list(dataframe.columns)
        )


def validate_wave_config(wave_config: str, supported_formats: list):
    """
    Validate wave configuration format.
    
    Args:
        wave_config: Wave configuration string to validate
        supported_formats: List of supported configuration formats
        
    Raises:
        WaveConfigurationError: If configuration is invalid
    """
    if wave_config not in supported_formats:
        raise WaveConfigurationError(
            wave_config=wave_config,
            supported_formats=supported_formats
        )


def validate_filter_value(dataframe, filter_column: str, filter_value):
    """
    Validate that a filter value exists in the specified column.
    
    Args:
        dataframe: pandas DataFrame to check
        filter_column: Column name to check
        filter_value: Value to validate
        
    Raises:
        FilteringError: If filter value is not found
    """
    if filter_column in dataframe.columns:
        available_values = dataframe[filter_column].dropna().unique().tolist()
        if filter_value not in available_values:
            raise FilteringError(
                filter_column=filter_column,
                filter_value=filter_value,
                available_values=available_values
            )


def handle_exception(logger, exception: Exception, context: str = "operation"):
    """
    Standardized exception handling with logging.
    
    Args:
        logger: Logger instance
        exception: Exception to handle
        context: Context description
        
    Returns:
        str: Formatted error message
    """
    if isinstance(exception, WaveVisualizerError):
        logger.error(f"{context} failed: {exception}")
        return str(exception)
    else:
        logger.error(f"Unexpected error in {context}: {exception}", exc_info=True)
        return f"Unexpected error occurred during {context}. Check logs for details." 