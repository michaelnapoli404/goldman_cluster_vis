"""
Input validation and sanitization for wave_visualizer package.

Provides comprehensive validation functions to ensure data integrity,
parameter correctness, and graceful error handling throughout the package.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, List, Optional, Union, Dict, Tuple
import re
import os
from .exceptions import (
    DataValidationError, ColumnNotFoundError, WaveConfigurationError,
    FilteringError, SettingsError
)
from .utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validates DataFrame inputs and data quality."""
    
    @staticmethod
    def validate_dataframe(data: Any, min_rows: int = 1, min_cols: int = 1) -> pd.DataFrame:
        """
        Validate that input is a proper DataFrame with minimum requirements.
        
        Args:
            data: Input data to validate
            min_rows: Minimum number of rows required
            min_cols: Minimum number of columns required
            
        Returns:
            pd.DataFrame: Validated DataFrame
            
        Raises:
            DataValidationError: If validation fails
        """
        if not isinstance(data, pd.DataFrame):
            raise DataValidationError(
                f"Expected pandas DataFrame, got {type(data).__name__}",
                "Please provide data as a pandas DataFrame"
            )
        
        if len(data) < min_rows:
            raise DataValidationError(
                f"DataFrame has {len(data)} rows, minimum {min_rows} required",
                "Dataset appears to be empty or too small for analysis"
            )
        
        if len(data.columns) < min_cols:
            raise DataValidationError(
                f"DataFrame has {len(data.columns)} columns, minimum {min_cols} required",
                "Dataset must contain at least one column"
            )
        
        logger.debug(f"DataFrame validation passed: {len(data)} rows, {len(data.columns)} columns")
        return data
    
    @staticmethod
    def validate_column_exists(data: pd.DataFrame, column_name: str, context: str = "operation") -> None:
        """
        Validate that a column exists in the DataFrame.
        
        Args:
            data: DataFrame to check
            column_name: Name of the column to validate
            context: Context description for error messages
            
        Raises:
            ColumnNotFoundError: If column is not found
        """
        if column_name not in data.columns:
            raise ColumnNotFoundError(
                column_name=column_name,
                available_columns=list(data.columns)
            )
        
        logger.debug(f"Column '{column_name}' validated for {context}")
    
    @staticmethod
    def validate_column_type(data: pd.DataFrame, column_name: str, 
                           expected_types: List[str]) -> None:
        """
        Validate that a column has an appropriate data type.
        
        Args:
            data: DataFrame containing the column
            column_name: Name of the column to check
            expected_types: List of acceptable data types
            
        Raises:
            DataValidationError: If column type is invalid
        """
        actual_type = str(data[column_name].dtype)
        
        if not any(expected_type in actual_type for expected_type in expected_types):
            raise DataValidationError(
                f"Column '{column_name}' has type '{actual_type}', expected one of {expected_types}",
                f"Column may need preprocessing or type conversion"
            )
        
        logger.debug(f"Column '{column_name}' type validation passed: {actual_type}")
    
    @staticmethod
    def validate_categorical_column(data: pd.DataFrame, column_name: str, 
                                  max_unique: int = 50) -> None:
        """
        Validate that a column is suitable for categorical analysis.
        
        Args:
            data: DataFrame containing the column
            column_name: Name of the column to check
            max_unique: Maximum number of unique values for categorical data
            
        Raises:
            DataValidationError: If column is not suitable for categorical analysis
        """
        unique_count = data[column_name].nunique()
        
        if unique_count > max_unique:
            raise DataValidationError(
                f"Column '{column_name}' has {unique_count} unique values, "
                f"maximum {max_unique} for categorical analysis",
                "Consider grouping values or using a different analysis approach"
            )
        
        if unique_count < 2:
            raise DataValidationError(
                f"Column '{column_name}' has only {unique_count} unique value(s)",
                "Categorical analysis requires at least 2 different values"
            )
        
        logger.debug(f"Categorical validation passed for '{column_name}': {unique_count} unique values")


class ParameterValidator:
    """Validates function parameters and configuration options."""
    
    @staticmethod
    def validate_string_parameter(value: Any, parameter_name: str, 
                                 allowed_values: Optional[List[str]] = None,
                                 min_length: int = 1) -> str:
        """
        Validate string parameter.
        
        Args:
            value: Value to validate
            parameter_name: Name of the parameter for error messages
            allowed_values: List of allowed values (optional)
            min_length: Minimum string length
            
        Returns:
            str: Validated string value
            
        Raises:
            DataValidationError: If validation fails
        """
        if not isinstance(value, str):
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be a string, got {type(value).__name__}",
                f"Provide a string value for {parameter_name}"
            )
        
        if len(value.strip()) < min_length:
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be at least {min_length} characters long",
                "Provide a non-empty string value"
            )
        
        value = value.strip()
        
        if allowed_values and value not in allowed_values:
            raise DataValidationError(
                f"Parameter '{parameter_name}' has invalid value '{value}'",
                f"Allowed values: {', '.join(allowed_values)}"
            )
        
        logger.debug(f"String parameter '{parameter_name}' validated: '{value}'")
        return value
    
    @staticmethod
    def validate_numeric_parameter(value: Any, parameter_name: str,
                                 min_value: Optional[float] = None,
                                 max_value: Optional[float] = None,
                                 allow_none: bool = False) -> Union[float, None]:
        """
        Validate numeric parameter.
        
        Args:
            value: Value to validate
            parameter_name: Name of the parameter for error messages
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)
            allow_none: Whether None values are allowed
            
        Returns:
            float or None: Validated numeric value
            
        Raises:
            DataValidationError: If validation fails
        """
        if value is None and allow_none:
            return None
        
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be numeric, got {type(value).__name__}",
                f"Provide a numeric value for {parameter_name}"
            )
        
        if min_value is not None and numeric_value < min_value:
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be >= {min_value}, got {numeric_value}",
                f"Increase the value of {parameter_name}"
            )
        
        if max_value is not None and numeric_value > max_value:
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be <= {max_value}, got {numeric_value}",
                f"Decrease the value of {parameter_name}"
            )
        
        logger.debug(f"Numeric parameter '{parameter_name}' validated: {numeric_value}")
        return numeric_value
    
    @staticmethod
    def validate_list_parameter(value: Any, parameter_name: str,
                              min_length: int = 0, max_length: Optional[int] = None,
                              element_type: Optional[type] = None) -> List[Any]:
        """
        Validate list parameter.
        
        Args:
            value: Value to validate
            parameter_name: Name of the parameter for error messages
            min_length: Minimum list length
            max_length: Maximum list length (optional)
            element_type: Required type for list elements (optional)
            
        Returns:
            List[Any]: Validated list
            
        Raises:
            DataValidationError: If validation fails
        """
        if not isinstance(value, (list, tuple)):
            raise DataValidationError(
                f"Parameter '{parameter_name}' must be a list, got {type(value).__name__}",
                f"Provide a list value for {parameter_name}"
            )
        
        value = list(value)  # Convert tuple to list if needed
        
        if len(value) < min_length:
            raise DataValidationError(
                f"Parameter '{parameter_name}' must have at least {min_length} elements, got {len(value)}",
                f"Add more elements to {parameter_name}"
            )
        
        if max_length is not None and len(value) > max_length:
            raise DataValidationError(
                f"Parameter '{parameter_name}' must have at most {max_length} elements, got {len(value)}",
                f"Remove some elements from {parameter_name}"
            )
        
        if element_type is not None:
            invalid_elements = [i for i, elem in enumerate(value) if not isinstance(elem, element_type)]
            if invalid_elements:
                raise DataValidationError(
                    f"Parameter '{parameter_name}' contains invalid element types at positions {invalid_elements}",
                    f"All elements must be of type {element_type.__name__}"
                )
        
        logger.debug(f"List parameter '{parameter_name}' validated: {len(value)} elements")
        return value


class WaveConfigValidator:
    """Validates wave configuration strings and settings."""
    
    @staticmethod
    def validate_wave_config_format(wave_config: str) -> Tuple[str, str]:
        """
        Validate wave configuration string format.
        
        Args:
            wave_config: Wave configuration string to validate
            
        Returns:
            Tuple[str, str]: Source and target wave identifiers
            
        Raises:
            WaveConfigurationError: If format is invalid
        """
        wave_config = wave_config.strip().lower()
        
        # Pattern for wave transitions (e.g., w1_to_w2, wave1_to_wave3)
        wave_pattern = r'^w(\d+)_to_w(\d+)$'
        match = re.match(wave_pattern, wave_config)
        
        if not match:
            if wave_config == 'all_waves':
                return 'all', 'all'
            
            raise WaveConfigurationError(
                wave_config,
                ["w1_to_w2", "w2_to_w3", "w1_to_w3", "all_waves", "w{N}_to_w{M}"]
            )
        
        source_wave, target_wave = match.groups()
        
        if source_wave == target_wave:
            raise WaveConfigurationError(
                wave_config,
                "Source and target waves must be different"
            )
        
        logger.debug(f"Wave config validated: {wave_config} -> W{source_wave} to W{target_wave}")
        return f"w{source_wave}", f"w{target_wave}"


class FilePathValidator:
    """Validates file paths and directory structures."""
    
    @staticmethod
    def validate_input_file(file_path: Union[str, Path], 
                          allowed_extensions: Optional[List[str]] = None) -> Path:
        """
        Validate input file path.
        
        Args:
            file_path: Path to validate
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Path: Validated path object
            
        Raises:
            SettingsError: If file validation fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise SettingsError(
                f"File not found: {path}",
                "Check that the file path is correct and the file exists"
            )
        
        if not path.is_file():
            raise SettingsError(
                f"Path is not a file: {path}",
                "Provide a path to a file, not a directory"
            )
        
        if allowed_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                raise SettingsError(
                    f"File has invalid extension: {path.suffix}",
                    f"Allowed extensions: {', '.join(allowed_extensions)}"
                )
        
        logger.debug(f"Input file validated: {path}")
        return path
    
    @staticmethod
    def validate_output_directory(dir_path: Union[str, Path], 
                                create_if_missing: bool = True) -> Path:
        """
        Validate output directory path.
        
        Args:
            dir_path: Directory path to validate
            create_if_missing: Whether to create directory if it doesn't exist
            
        Returns:
            Path: Validated directory path
            
        Raises:
            SettingsError: If directory validation fails
        """
        path = Path(dir_path)
        
        if not path.exists():
            if create_if_missing:
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Created output directory: {path}")
                except OSError as e:
                    raise SettingsError(
                        f"Cannot create directory: {path}",
                        f"Permission error or invalid path: {e}"
                    )
            else:
                raise SettingsError(
                    f"Directory not found: {path}",
                    "Create the directory or set create_if_missing=True"
                )
        
        if not path.is_dir():
            raise SettingsError(
                f"Path is not a directory: {path}",
                "Provide a path to a directory, not a file"
            )
        
        # Check write permissions
        if not os.access(path, os.W_OK):
            raise SettingsError(
                f"No write permission for directory: {path}",
                "Check directory permissions"
            )
        
        logger.debug(f"Output directory validated: {path}")
        return path


class FilterValidator:
    """Validates data filtering operations."""
    
    @staticmethod
    def validate_filter_operation(data: pd.DataFrame, filter_column: str, 
                                filter_value: Any) -> None:
        """
        Validate that a filter operation can be performed.
        
        Args:
            data: DataFrame to filter
            filter_column: Column to filter by
            filter_value: Value to filter for
            
        Raises:
            FilteringError: If filter validation fails
        """
        # Check if column exists
        if filter_column not in data.columns:
            raise ColumnNotFoundError(
                column_name=filter_column,
                available_columns=list(data.columns)
            )
        
        # Get available values in the column
        available_values = data[filter_column].dropna().unique().tolist()
        
        # Check if filter value exists
        if filter_value not in available_values:
            raise FilteringError(
                filter_column=filter_column,
                filter_value=str(filter_value),
                available_values=available_values
            )
        
        # Check if filtering would result in empty dataset
        filtered_count = (data[filter_column] == filter_value).sum()
        if filtered_count == 0:
            raise FilteringError(
                filter_column=filter_column,
                filter_value=str(filter_value),
                available_values=available_values
            )
        
        logger.debug(f"Filter validation passed: {filter_column}={filter_value} "
                    f"({filtered_count} rows will remain)")


# Convenience functions for common validations
def validate_visualization_inputs(data: pd.DataFrame, variable_name: str,
                                wave_config: str, filter_column: Optional[str] = None,
                                filter_value: Optional[str] = None) -> None:
    """
    Validate all inputs for visualization creation.
    
    Args:
        data: Input DataFrame
        variable_name: Variable to analyze
        wave_config: Wave configuration string
        filter_column: Optional filter column
        filter_value: Optional filter value
        
    Raises:
        Various validation errors if inputs are invalid
    """
    # Validate DataFrame
    DataValidator.validate_dataframe(data, min_rows=10, min_cols=2)
    
    # Validate wave configuration first
    WaveConfigValidator.validate_wave_config_format(wave_config)
    
    # For wave-based variables, check if wave-prefixed columns exist
    # rather than the base variable name
    from wave_visualizer.data_prep.wave_parser import parse_wave_config, generate_column_names
    try:
        source_wave_prefix, target_wave_prefix = parse_wave_config(wave_config)
        source_column, target_column = generate_column_names(
            source_wave_prefix, target_wave_prefix, variable_name
        )
        
        # Validate the actual wave-prefixed columns exist
        DataValidator.validate_column_exists(data, source_column, "visualization")
        DataValidator.validate_column_exists(data, target_column, "visualization")
        DataValidator.validate_categorical_column(data, source_column)
        DataValidator.validate_categorical_column(data, target_column)
        
    except Exception:
        # Fallback to checking the base variable name if wave parsing fails
        DataValidator.validate_column_exists(data, variable_name, "visualization")
        DataValidator.validate_categorical_column(data, variable_name)
    
    # Validate filtering if specified  
    if filter_column and filter_value:
        FilterValidator.validate_filter_operation(data, filter_column, filter_value)
    
    logger.debug("All visualization inputs validated successfully")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename safe for file systems
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    logger.debug(f"Filename sanitized: '{filename}'")
    return filename 