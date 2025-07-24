"""
Values to Labels Converter

Converts coded values in dataset columns to human-readable labels using 
metadata extracted by metadata_handler and saved in CSV format.

This module reads the metadata CSV files and applies the value-to-label 
mappings to transform coded data into meaningful text.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import warnings

warnings.filterwarnings('ignore')

class ValuesToLabelsConverter:
    """
    Converts coded values to human-readable labels using metadata CSV files.
    """
    
    def __init__(self, metadata_dir: str = None):
        """
        Initialize the converter with metadata directory.
        
        Args:
            metadata_dir: Directory containing metadata CSV files from metadata_handler
                         (defaults to package settings folder)
        """
        # Use settings folder within package if no metadata_dir specified
        if metadata_dir is None:
            from wave_visualizer.settings import METADATA_DIR
            self.metadata_dir = METADATA_DIR
        else:
            self.metadata_dir = Path(metadata_dir)
        self.variable_labels_file = self.metadata_dir / "variable_labels.csv"
        self.value_labels_file = self.metadata_dir / "value_labels.csv"
        
        # Storage for loaded metadata
        self.variable_labels = {}
        self.value_labels = {}
        
        # Load metadata on initialization
        self._load_metadata()
    
    def _load_metadata(self) -> bool:
        """
        Load metadata from CSV files created by metadata_handler.
        
        Returns:
            bool: True if metadata loaded successfully, False otherwise
        """
        try:
            # Load variable labels
            if self.variable_labels_file.exists():
                var_labels_df = pd.read_csv(self.variable_labels_file)
                self.variable_labels = dict(zip(
                    var_labels_df['variable_name'], 
                    var_labels_df['variable_label']
                ))
                print(f"Loaded {len(self.variable_labels)} variable labels")
            else:
                print(f"Warning: Variable labels file not found: {self.variable_labels_file}")
                print("Run metadata_handler first to generate metadata CSV files")
            
            # Load value labels
            if self.value_labels_file.exists():
                value_labels_df = pd.read_csv(self.value_labels_file)
                
                # Group by variable to create nested dictionary
                for variable in value_labels_df['variable_name'].unique():
                    var_data = value_labels_df[value_labels_df['variable_name'] == variable]
                    self.value_labels[variable] = dict(zip(
                        var_data['value'], 
                        var_data['value_label']
                    ))
                
                print(f"Loaded value labels for {len(self.value_labels)} variables")
            else:
                print(f"Warning: Value labels file not found: {self.value_labels_file}")
                print("This may be normal if your dataset has no value labels")
            
            return True
            
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")
            return False
    
    def convert_column(self, 
                      column_data: pd.Series, 
                      variable_name: str,
                      keep_original: bool = False,
                      missing_strategy: str = "keep_original") -> Union[pd.Series, pd.DataFrame]:
        """
        Convert coded values in a column to human-readable labels.
        
        Args:
            column_data: Pandas Series containing the coded values
            variable_name: Name of the variable (for looking up metadata)
            keep_original: If True, return DataFrame with both original and labeled columns
            missing_strategy: How to handle values without labels ("keep_original", "mark_missing", "drop")
            
        Returns:
            pd.Series or pd.DataFrame: Converted data with labels
        """
        print(f"Converting column '{variable_name}' from codes to labels...")
        
        # Get value labels for this variable
        value_mapping = self.value_labels.get(variable_name, {})
        
        if not value_mapping:
            print(f"  No value labels found for '{variable_name}' - keeping original values")
            if keep_original:
                return pd.DataFrame({
                    f'{variable_name}_original': column_data,
                    f'{variable_name}_labeled': column_data
                })
            else:
                return column_data.copy()
        
        # Create labeled column
        labeled_column = column_data.copy()
        
        # Track conversion statistics
        total_values = len(column_data)
        converted_count = 0
        missing_count = 0
        
        # Apply value mappings
        for original_value, label in value_mapping.items():
            mask = (column_data == original_value)
            converted_count += mask.sum()
            labeled_column.loc[mask] = label
        
        # Handle values without labels based on strategy
        unconverted_mask = ~column_data.isin(value_mapping.keys()) & column_data.notna()
        unconverted_count = unconverted_mask.sum()
        
        if unconverted_count > 0:
            if missing_strategy == "keep_original":
                # Keep original values for unmapped codes
                pass  # labeled_column already has original values
            elif missing_strategy == "mark_missing":
                # Mark unmapped values as "Unknown"
                labeled_column.loc[unconverted_mask] = "Unknown"
            elif missing_strategy == "drop":
                # This will be handled at the dataset level, not here
                print(f"  Note: {unconverted_count} values marked for dropping (unmapped codes)")
        
        # Count actual missing values (NaN)
        missing_count = column_data.isna().sum()
        
        # Print conversion summary
        print(f"  Conversion summary:")
        print(f"    - Total values: {total_values}")
        print(f"    - Successfully converted: {converted_count}")
        print(f"    - Unmapped codes: {unconverted_count}")
        print(f"    - Missing (NaN): {missing_count}")
        print(f"    - Available labels: {len(value_mapping)}")
        
        # Show some example mappings
        if value_mapping:
            print(f"  Example mappings:")
            for i, (code, label) in enumerate(list(value_mapping.items())[:3]):
                print(f"    {code} → '{label}'")
            if len(value_mapping) > 3:
                print(f"    ... and {len(value_mapping) - 3} more mappings")
        
        if keep_original:
            return pd.DataFrame({
                f'{variable_name}_original': column_data,
                f'{variable_name}_labeled': labeled_column
            })
        else:
            return labeled_column
    
    def convert_multiple_columns(self, 
                                dataframe: pd.DataFrame, 
                                columns: List[str],
                                keep_original: bool = False,
                                missing_strategy: str = "keep_original") -> pd.DataFrame:
        """
        Convert multiple columns from codes to labels.
        
        Args:
            dataframe: DataFrame containing the data
            columns: List of column names to convert
            keep_original: If True, keep both original and labeled columns
            missing_strategy: How to handle values without labels
            
        Returns:
            pd.DataFrame: DataFrame with converted columns
        """
        print("="*60)
        print("CONVERTING MULTIPLE COLUMNS TO LABELS")
        print("="*60)
        
        result_df = dataframe.copy()
        
        for column in columns:
            if column not in dataframe.columns:
                print(f"Warning: Column '{column}' not found in dataframe")
                continue
            
            converted_data = self.convert_column(
                dataframe[column], 
                column, 
                keep_original=keep_original,
                missing_strategy=missing_strategy
            )
            
            if isinstance(converted_data, pd.DataFrame):
                # Add both original and labeled columns
                for col_name in converted_data.columns:
                    result_df[col_name] = converted_data[col_name]
            else:
                # Replace the original column with labeled version
                result_df[f'{column}_labeled'] = converted_data
                if not keep_original:
                    # Optional: could remove original column
                    pass
        
        print("="*60)
        print("Multiple column conversion completed!")
        print("="*60)
        
        return result_df
    
    def get_available_variables(self) -> List[str]:
        """
        Get list of variables that have value labels available.
        
        Returns:
            List[str]: List of variable names with value labels
        """
        return list(self.value_labels.keys())
    
    def get_variable_mappings(self, variable_name: str) -> Dict[Any, str]:
        """
        Get the value-to-label mappings for a specific variable.
        
        Args:
            variable_name: Name of the variable
            
        Returns:
            Dict: Mapping of values to labels
        """
        return self.value_labels.get(variable_name, {})
    
    def preview_conversion(self, 
                          column_data: pd.Series, 
                          variable_name: str,
                          n_examples: int = 10) -> pd.DataFrame:
        """
        Preview what the conversion would look like without actually converting.
        
        Args:
            column_data: Pandas Series containing the coded values
            variable_name: Name of the variable
            n_examples: Number of examples to show
            
        Returns:
            pd.DataFrame: Preview showing original values and their labels
        """
        value_mapping = self.value_labels.get(variable_name, {})
        
        if not value_mapping:
            print(f"No value labels available for '{variable_name}'")
            return pd.DataFrame({'original_value': [], 'would_become': []})
        
        # Get unique values from the column
        unique_values = column_data.dropna().unique()[:n_examples]
        
        preview_data = []
        for value in unique_values:
            label = value_mapping.get(value, f"[NO LABEL] {value}")
            preview_data.append({
                'original_value': value,
                'would_become': label,
                'count_in_data': (column_data == value).sum()
            })
        
        preview_df = pd.DataFrame(preview_data)
        
        print(f"Conversion preview for '{variable_name}':")
        print(preview_df.to_string(index=False))
        
        return preview_df
    
    def validate_metadata(self) -> Dict[str, Any]:
        """
        Validate the loaded metadata and return summary information.
        
        Returns:
            Dict: Summary of metadata validation
        """
        validation_result = {
            'metadata_loaded': len(self.variable_labels) > 0 or len(self.value_labels) > 0,
            'variable_labels_count': len(self.variable_labels),
            'value_labels_count': len(self.value_labels),
            'variables_with_value_labels': list(self.value_labels.keys()),
            'metadata_files_exist': {
                'variable_labels': self.variable_labels_file.exists(),
                'value_labels': self.value_labels_file.exists()
            }
        }
        
        print("Metadata Validation Summary:")
        print(f"  Variable labels loaded: {validation_result['variable_labels_count']}")
        print(f"  Variables with value labels: {validation_result['value_labels_count']}")
        print(f"  Variables: {', '.join(validation_result['variables_with_value_labels'][:5])}")
        if len(validation_result['variables_with_value_labels']) > 5:
            print(f"    ... and {len(validation_result['variables_with_value_labels']) - 5} more")
        
        return validation_result

def main():
    """
    Example usage of ValuesToLabelsConverter.
    """
    print("ValuesToLabelsConverter - Example Usage")
    print("To use this module:")
    print()
    print("from wave_visualizer.data_prep.cleaning.values_to_labels import ValuesToLabelsConverter")
    print("import pandas as pd")
    print()
    print("# Initialize converter (loads metadata automatically)")
    print("converter = ValuesToLabelsConverter('./metadata_output/')")
    print()
    print("# Convert a single column")
    print("labeled_column = converter.convert_column(df['PID1'], 'PID1')")
    print()
    print("# Convert multiple columns")
    print("df_labeled = converter.convert_multiple_columns(df, ['PID1', 'W2_PID1'])")
    print()
    print("# Preview conversion")
    print("converter.preview_conversion(df['PID1'], 'PID1')")

if __name__ == "__main__":
    main() 