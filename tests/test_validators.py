"""
Unit tests for wave_visualizer.validators module.
"""

import pytest
import pandas as pd
import numpy as np
from wave_visualizer.validators import (
    DataValidator, ParameterValidator, WaveConfigValidator,
    FilePathValidator, FilterValidator, validate_visualization_inputs,
    sanitize_filename
)
from wave_visualizer.exceptions import (
    DataValidationError, ColumnNotFoundError, WaveConfigurationError,
    SettingsError, FilteringError
)


class TestDataValidator:
    """Test DataValidator class."""
    
    def test_validate_dataframe_valid(self, sample_data):
        """Test validation of valid DataFrame."""
        result = DataValidator.validate_dataframe(sample_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_data)
    
    def test_validate_dataframe_invalid_type(self):
        """Test validation with invalid input type."""
        with pytest.raises(DataValidationError, match="Expected pandas DataFrame"):
            DataValidator.validate_dataframe("not a dataframe")
    
    def test_validate_dataframe_too_few_rows(self):
        """Test validation with insufficient rows."""
        small_df = pd.DataFrame({'A': [1]})
        with pytest.raises(DataValidationError, match="minimum 10 required"):
            DataValidator.validate_dataframe(small_df, min_rows=10)
    
    def test_validate_column_exists_valid(self, sample_data):
        """Test column existence validation with valid column."""
        # Should not raise exception
        DataValidator.validate_column_exists(sample_data, 'W1_HFClust_labeled')
    
    def test_validate_column_exists_invalid(self, sample_data):
        """Test column existence validation with invalid column."""
        with pytest.raises(ColumnNotFoundError, match="Column 'nonexistent' not found"):
            DataValidator.validate_column_exists(sample_data, 'nonexistent')
    
    def test_validate_categorical_column_valid(self, sample_data):
        """Test categorical column validation with valid column."""
        # Should not raise exception
        DataValidator.validate_categorical_column(sample_data, 'W1_HFClust_labeled')
    
    def test_validate_categorical_column_too_many_unique(self, sample_data):
        """Test categorical validation with too many unique values."""
        # Create column with many unique values
        sample_data['many_unique'] = range(len(sample_data))
        with pytest.raises(DataValidationError, match="maximum 50 for categorical"):
            DataValidator.validate_categorical_column(sample_data, 'many_unique', max_unique=50)
    
    def test_validate_categorical_column_too_few_unique(self):
        """Test categorical validation with too few unique values."""
        df = pd.DataFrame({'constant': ['A'] * 100})
        with pytest.raises(DataValidationError, match="only 1 unique value"):
            DataValidator.validate_categorical_column(df, 'constant')


class TestParameterValidator:
    """Test ParameterValidator class."""
    
    def test_validate_string_parameter_valid(self):
        """Test string parameter validation with valid input."""
        result = ParameterValidator.validate_string_parameter("test", "param")
        assert result == "test"
    
    def test_validate_string_parameter_with_whitespace(self):
        """Test string parameter validation with whitespace."""
        result = ParameterValidator.validate_string_parameter("  test  ", "param")
        assert result == "test"
    
    def test_validate_string_parameter_invalid_type(self):
        """Test string parameter validation with invalid type."""
        with pytest.raises(DataValidationError, match="must be a string"):
            ParameterValidator.validate_string_parameter(123, "param")
    
    def test_validate_string_parameter_empty(self):
        """Test string parameter validation with empty string."""
        with pytest.raises(DataValidationError, match="at least 1 characters long"):
            ParameterValidator.validate_string_parameter("", "param")
    
    def test_validate_string_parameter_allowed_values(self):
        """Test string parameter validation with allowed values."""
        result = ParameterValidator.validate_string_parameter(
            "option1", "param", allowed_values=["option1", "option2"]
        )
        assert result == "option1"
    
    def test_validate_string_parameter_disallowed_value(self):
        """Test string parameter validation with disallowed value."""
        with pytest.raises(DataValidationError, match="invalid value"):
            ParameterValidator.validate_string_parameter(
                "option3", "param", allowed_values=["option1", "option2"]
            )
    
    def test_validate_numeric_parameter_valid(self):
        """Test numeric parameter validation with valid input."""
        result = ParameterValidator.validate_numeric_parameter(42.5, "param")
        assert result == 42.5
    
    def test_validate_numeric_parameter_invalid_type(self):
        """Test numeric parameter validation with invalid type."""
        with pytest.raises(DataValidationError, match="must be numeric"):
            ParameterValidator.validate_numeric_parameter("not_numeric", "param")
    
    def test_validate_numeric_parameter_with_bounds(self):
        """Test numeric parameter validation with bounds."""
        result = ParameterValidator.validate_numeric_parameter(
            15, "param", min_value=10, max_value=20
        )
        assert result == 15
    
    def test_validate_numeric_parameter_below_min(self):
        """Test numeric parameter validation below minimum."""
        with pytest.raises(DataValidationError, match="must be >= 10"):
            ParameterValidator.validate_numeric_parameter(5, "param", min_value=10)
    
    def test_validate_numeric_parameter_above_max(self):
        """Test numeric parameter validation above maximum."""
        with pytest.raises(DataValidationError, match="must be <= 20"):
            ParameterValidator.validate_numeric_parameter(25, "param", max_value=20)
    
    def test_validate_list_parameter_valid(self):
        """Test list parameter validation with valid input."""
        result = ParameterValidator.validate_list_parameter([1, 2, 3], "param")
        assert result == [1, 2, 3]
    
    def test_validate_list_parameter_tuple_input(self):
        """Test list parameter validation with tuple input."""
        result = ParameterValidator.validate_list_parameter((1, 2, 3), "param")
        assert result == [1, 2, 3]
    
    def test_validate_list_parameter_invalid_type(self):
        """Test list parameter validation with invalid type."""
        with pytest.raises(DataValidationError, match="must be a list"):
            ParameterValidator.validate_list_parameter("not_a_list", "param")
    
    def test_validate_list_parameter_length_constraints(self):
        """Test list parameter validation with length constraints."""
        result = ParameterValidator.validate_list_parameter(
            [1, 2], "param", min_length=1, max_length=3
        )
        assert result == [1, 2]
    
    def test_validate_list_parameter_too_short(self):
        """Test list parameter validation with insufficient length."""
        with pytest.raises(DataValidationError, match="at least 2 elements"):
            ParameterValidator.validate_list_parameter([1], "param", min_length=2)
    
    def test_validate_list_parameter_element_types(self):
        """Test list parameter validation with element type constraints."""
        result = ParameterValidator.validate_list_parameter(
            ["a", "b", "c"], "param", element_type=str
        )
        assert result == ["a", "b", "c"]
    
    def test_validate_list_parameter_invalid_element_types(self):
        """Test list parameter validation with invalid element types."""
        with pytest.raises(DataValidationError, match="invalid element types"):
            ParameterValidator.validate_list_parameter(
                ["a", 2, "c"], "param", element_type=str
            )


class TestWaveConfigValidator:
    """Test WaveConfigValidator class."""
    
    def test_validate_wave_config_format_valid(self):
        """Test wave config validation with valid format."""
        source, target = WaveConfigValidator.validate_wave_config_format("w1_to_w2")
        assert source == "w1"
        assert target == "w2"
    
    def test_validate_wave_config_format_all_waves(self):
        """Test wave config validation with all_waves."""
        source, target = WaveConfigValidator.validate_wave_config_format("all_waves")
        assert source == "all"
        assert target == "all"
    
    def test_validate_wave_config_format_invalid(self):
        """Test wave config validation with invalid format."""
        with pytest.raises(WaveConfigurationError):
            WaveConfigValidator.validate_wave_config_format("invalid_format")
    
    def test_validate_wave_config_format_same_waves(self):
        """Test wave config validation with same source and target."""
        with pytest.raises(WaveConfigurationError):
            WaveConfigValidator.validate_wave_config_format("w1_to_w1")


class TestFilterValidator:
    """Test FilterValidator class."""
    
    def test_validate_filter_operation_valid(self, sample_data):
        """Test filter validation with valid operation."""
        # Should not raise exception
        FilterValidator.validate_filter_operation(
            sample_data, 'W1_PID1_labeled', 'Republican'
        )
    
    def test_validate_filter_operation_invalid_column(self, sample_data):
        """Test filter validation with invalid column."""
        with pytest.raises(ColumnNotFoundError):
            FilterValidator.validate_filter_operation(
                sample_data, 'nonexistent_col', 'value'
            )
    
    def test_validate_filter_operation_invalid_value(self, sample_data):
        """Test filter validation with invalid value."""
        with pytest.raises(FilteringError):
            FilterValidator.validate_filter_operation(
                sample_data, 'W1_PID1_labeled', 'NonexistentParty'
            )


class TestConvenienceFunctions:
    """Test convenience validation functions."""
    
    def test_validate_visualization_inputs_valid(self, sample_data):
        """Test comprehensive validation with valid inputs."""
        # Should not raise exception
        validate_visualization_inputs(
            sample_data, 'HFClust_labeled', 'w1_to_w2', 'PID1_labeled', 'Republican'
        )
    
    def test_sanitize_filename_valid(self):
        """Test filename sanitization with valid input."""
        result = sanitize_filename("valid_filename")
        assert result == "valid_filename"
    
    def test_sanitize_filename_invalid_chars(self):
        """Test filename sanitization with invalid characters."""
        result = sanitize_filename("file<name>with:invalid*chars")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "*" not in result
    
    def test_sanitize_filename_empty(self):
        """Test filename sanitization with empty input."""
        result = sanitize_filename("")
        assert result == "untitled"
    
    def test_sanitize_filename_too_long(self):
        """Test filename sanitization with overly long input."""
        long_name = "a" * 150
        result = sanitize_filename(long_name)
        assert len(result) <= 100


@pytest.mark.unit
class TestValidatorErrorMessages:
    """Test that validators provide helpful error messages."""
    
    def test_column_not_found_suggests_alternatives(self, sample_data):
        """Test that ColumnNotFoundError suggests similar column names."""
        with pytest.raises(ColumnNotFoundError) as exc_info:
            DataValidator.validate_column_exists(sample_data, 'HFClust')  # Missing _labeled
        
        error_msg = str(exc_info.value)
        assert "HFClust_labeled" in error_msg  # Should suggest the correct column
    
    def test_filtering_error_shows_available_values(self, sample_data):
        """Test that FilteringError shows available values."""
        with pytest.raises(FilteringError) as exc_info:
            FilterValidator.validate_filter_operation(
                sample_data, 'W1_PID1_labeled', 'InvalidParty'
            )
        
        error_msg = str(exc_info.value)
        assert "Republican" in error_msg or "Democrat" in error_msg
    
    def test_wave_config_error_shows_supported_formats(self):
        """Test that WaveConfigurationError shows supported formats."""
        with pytest.raises(WaveConfigurationError) as exc_info:
            WaveConfigValidator.validate_wave_config_format("invalid")
        
        error_msg = str(exc_info.value)
        assert "w1_to_w2" in error_msg 