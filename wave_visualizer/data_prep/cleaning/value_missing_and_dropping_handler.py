"""
Value Missing and Dropping Handler

Identifies columns with missing values in the dataset and prompts user for 
handling strategies. Saves user preferences as CSV for consistent application
across the cleaning pipeline.

Supported strategies:
- Drop missing values
- Drop specific values (including NaN)
- Impute with average/min/max
- Label missing as "Unknown" or custom label
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')

class ValueMissingAndDroppingHandler:
    """
    Handles user preferences for missing value treatment and specific value dropping.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the handler.
        
        Args:
            output_dir: Directory to save user preference CSV files (defaults to package settings folder)
        """
        # Use settings folder within package if no output_dir specified
        if output_dir is None:
            from wave_visualizer.settings import CLEANING_DIR
            self.output_dir = CLEANING_DIR
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True)
        
        self.missing_settings_file = self.output_dir / "missing_value_settings.csv"
        self.drop_settings_file = self.output_dir / "drop_value_settings.csv"
        
        # Storage for user preferences
        self.missing_strategies = {}
        self.drop_values = {}
        
    def analyze_missing_values(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze missing values in the dataset.
        
        Args:
            dataframe: DataFrame to analyze
            
        Returns:
            pd.DataFrame: Summary of missing values by column
        """
        missing_summary = []
        
        for column in dataframe.columns:
            missing_count = dataframe[column].isna().sum()
            total_count = len(dataframe)
            missing_pct = (missing_count / total_count) * 100
            
            # Get unique values for context
            unique_values = dataframe[column].dropna().nunique()
            sample_values = dataframe[column].dropna().unique()[:5].tolist()
            
            missing_summary.append({
                'column': column,
                'missing_count': missing_count,
                'total_count': total_count,
                'missing_percentage': missing_pct,
                'unique_values': unique_values,
                'sample_values': str(sample_values)
            })
        
        return pd.DataFrame(missing_summary)
    
    def get_user_missing_strategy(self, 
                                 column_name: str, 
                                 missing_info: Dict[str, Any],
                                 interactive: bool = True) -> Dict[str, Any]:
        """
        Get user preference for handling missing values in a specific column.
        
        Args:
            column_name: Name of the column
            missing_info: Information about missing values in this column
            interactive: If True, prompt user; if False, use defaults
            
        Returns:
            Dict: User's strategy for this column
        """
        if not interactive:
            # Default strategy: mark as unknown
            return {
                'column': column_name,
                'strategy': 'mark_unknown',
                'custom_label': 'Unknown',
                'impute_method': None,
                'impute_value': None
            }
        
        print(f"\n{'='*60}")
        print(f"MISSING VALUE STRATEGY FOR: {column_name}")
        print(f"{'='*60}")
        print(f"Missing values: {missing_info['missing_count']} ({missing_info['missing_percentage']:.1f}%)")
        print(f"Total values: {missing_info['total_count']}")
        print(f"Unique non-missing values: {missing_info['unique_values']}")
        print(f"Sample values: {missing_info['sample_values']}")
        print()
        
        print("Available strategies:")
        print("1. Drop rows with missing values in this column")
        print("2. Mark missing values with custom label (e.g., 'Unknown')")
        print("3. Impute missing values (average, median, mode, min, max)")
        print("4. Impute with custom value")
        print("5. Keep missing values as NaN")
        print()
        
        while True:
            try:
                choice = input("Choose strategy (1-5): ").strip()
                
                if choice == '1':
                    return {
                        'column': column_name,
                        'strategy': 'drop_missing',
                        'custom_label': None,
                        'impute_method': None,
                        'impute_value': None
                    }
                
                elif choice == '2':
                    custom_label = input("Enter custom label for missing values (default: 'Unknown'): ").strip()
                    if not custom_label:
                        custom_label = 'Unknown'
                    
                    return {
                        'column': column_name,
                        'strategy': 'mark_unknown',
                        'custom_label': custom_label,
                        'impute_method': None,
                        'impute_value': None
                    }
                
                elif choice == '3':
                    print("\nImputation methods:")
                    print("a. Mean/Average (for numeric columns)")
                    print("b. Median (for numeric columns)")
                    print("c. Mode (most common value)")
                    print("d. Minimum value")
                    print("e. Maximum value")
                    
                    impute_choice = input("Choose imputation method (a-e): ").strip().lower()
                    
                    method_map = {
                        'a': 'mean',
                        'b': 'median', 
                        'c': 'mode',
                        'd': 'min',
                        'e': 'max'
                    }
                    
                    if impute_choice in method_map:
                        return {
                            'column': column_name,
                            'strategy': 'impute',
                            'custom_label': None,
                            'impute_method': method_map[impute_choice],
                            'impute_value': None
                        }
                    else:
                        print("Invalid choice. Please try again.")
                        continue
                
                elif choice == '4':
                    custom_value = input("Enter custom value for imputation: ").strip()
                    
                    return {
                        'column': column_name,
                        'strategy': 'impute',
                        'custom_label': None,
                        'impute_method': 'custom',
                        'impute_value': custom_value
                    }
                
                elif choice == '5':
                    return {
                        'column': column_name,
                        'strategy': 'keep_nan',
                        'custom_label': None,
                        'impute_method': None,
                        'impute_value': None
                    }
                
                else:
                    print("Invalid choice. Please enter 1-5.")
                    continue
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return None
            except Exception as e:
                print(f"Error: {str(e)}. Please try again.")
                continue
    
    def get_user_drop_values(self, 
                           column_name: str, 
                           unique_values: List[Any],
                           interactive: bool = True) -> List[Any]:
        """
        Get user preference for specific values to drop from a column.
        
        Args:
            column_name: Name of the column
            unique_values: List of unique values in the column
            interactive: If True, prompt user; if False, return empty list
            
        Returns:
            List: Values to drop from this column
        """
        if not interactive:
            return []
        
        print(f"\n{'='*60}")
        print(f"DROP SPECIFIC VALUES FOR: {column_name}")
        print(f"{'='*60}")
        print(f"Unique values in column ({len(unique_values)} total):")
        
        # Show values in a readable format
        for i, value in enumerate(unique_values[:20]):  # Show first 20
            print(f"  {i+1:2d}. {value}")
        
        if len(unique_values) > 20:
            print(f"  ... and {len(unique_values) - 20} more values")
        
        print()
        print("Options:")
        print("1. Don't drop any specific values")
        print("2. Drop specific values by entering them")
        print("3. Drop values by number (from list above)")
        print()
        
        while True:
            try:
                choice = input("Choose option (1-3): ").strip()
                
                if choice == '1':
                    return []
                
                elif choice == '2':
                    print("Enter values to drop (comma-separated):")
                    print("Example: value1, value2, value3")
                    drop_input = input("Values to drop: ").strip()
                    
                    if not drop_input:
                        return []
                    
                    # Parse comma-separated values
                    drop_values = [val.strip() for val in drop_input.split(',')]
                    
                    # Try to convert to appropriate types
                    converted_values = []
                    for val in drop_values:
                        # Try to match with actual values in the column
                        for unique_val in unique_values:
                            if str(unique_val).strip() == val:
                                converted_values.append(unique_val)
                                break
                        else:
                            # Try to convert type
                            try:
                                # Try numeric conversion
                                if '.' in val:
                                    converted_values.append(float(val))
                                else:
                                    converted_values.append(int(val))
                            except ValueError:
                                # Keep as string
                                converted_values.append(val)
                    
                    print(f"Will drop values: {converted_values}")
                    confirm = input("Confirm? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return converted_values
                    else:
                        continue
                
                elif choice == '3':
                    print("Enter numbers corresponding to values to drop (comma-separated):")
                    print("Example: 1, 3, 5")
                    numbers_input = input("Numbers: ").strip()
                    
                    if not numbers_input:
                        return []
                    
                    try:
                        numbers = [int(n.strip()) for n in numbers_input.split(',')]
                        drop_values = []
                        
                        for num in numbers:
                            if 1 <= num <= len(unique_values):
                                drop_values.append(unique_values[num-1])
                            else:
                                print(f"Warning: Number {num} is out of range")
                        
                        print(f"Will drop values: {drop_values}")
                        confirm = input("Confirm? (y/n): ").strip().lower()
                        if confirm in ['y', 'yes']:
                            return drop_values
                        else:
                            continue
                            
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by commas.")
                        continue
                
                else:
                    print("Invalid choice. Please enter 1-3.")
                    continue
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return []
            except Exception as e:
                print(f"Error: {str(e)}. Please try again.")
                continue
    
    def collect_user_preferences(self, 
                                dataframe: pd.DataFrame,
                                interactive: bool = True,
                                columns_to_process: Optional[List[str]] = None) -> bool:
        """
        Collect user preferences for all columns with missing values or for specific columns.
        
        Args:
            dataframe: DataFrame to analyze
            interactive: If True, prompt user; if False, use defaults
            columns_to_process: Specific columns to process, None for all columns with missing values
            
        Returns:
            bool: True if collection was successful
        """
        print("="*60)
        print("VALUE MISSING AND DROPPING HANDLER")
        print("="*60)
        
        # Analyze missing values
        missing_analysis = self.analyze_missing_values(dataframe)
        
        # Determine which columns to process
        if columns_to_process is None:
            # Process only columns with missing values
            columns_with_missing = missing_analysis[missing_analysis['missing_count'] > 0]['column'].tolist()
        else:
            columns_with_missing = [col for col in columns_to_process if col in dataframe.columns]
        
        if not columns_with_missing:
            print("No missing values found in the dataset!")
            return True
        
        print(f"Found {len(columns_with_missing)} columns to process:")
        for col in columns_with_missing:
            missing_info = missing_analysis[missing_analysis['column'] == col].iloc[0].to_dict()
            print(f"  - {col}: {missing_info['missing_count']} missing ({missing_info['missing_percentage']:.1f}%)")
        
        # Collect missing value strategies
        for column in columns_with_missing:
            missing_info = missing_analysis[missing_analysis['column'] == column].iloc[0].to_dict()
            
            strategy = self.get_user_missing_strategy(column, missing_info, interactive)
            if strategy is not None:
                self.missing_strategies[column] = strategy
        
        # Collect drop value preferences for all columns
        print(f"\n{'='*60}")
        print("CHECKING FOR VALUES TO DROP")
        print(f"{'='*60}")
        
        if interactive:
            process_drops = input("Do you want to drop specific values from any columns? (y/n): ").strip().lower()
            if process_drops in ['y', 'yes']:
                for column in dataframe.columns:
                    unique_values = dataframe[column].dropna().unique().tolist()
                    if len(unique_values) > 1:  # Only process columns with multiple values
                        drop_values = self.get_user_drop_values(column, unique_values, interactive)
                        if drop_values:
                            self.drop_values[column] = drop_values
        
        return True
    
    def save_preferences_to_csv(self) -> bool:
        """
        Save user preferences to CSV files.
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Save missing value strategies
            if self.missing_strategies:
                missing_df = pd.DataFrame(list(self.missing_strategies.values()))
                missing_df.to_csv(self.missing_settings_file, index=False)
                print(f"Missing value settings saved to: {self.missing_settings_file}")
            
            # Save drop value settings
            if self.drop_values:
                drop_rows = []
                for column, values_to_drop in self.drop_values.items():
                    for value in values_to_drop:
                        drop_rows.append({
                            'column': column,
                            'value_to_drop': value
                        })
                
                drop_df = pd.DataFrame(drop_rows)
                drop_df.to_csv(self.drop_settings_file, index=False)
                print(f"Drop value settings saved to: {self.drop_settings_file}")
            
            return True
            
        except Exception as e:
            print(f"Error saving preferences: {str(e)}")
            return False
    
    def load_preferences_from_csv(self) -> bool:
        """
        Load previously saved preferences from CSV files.
        
        Returns:
            bool: True if load was successful
        """
        try:
            # Load missing value strategies
            if self.missing_settings_file.exists():
                missing_df = pd.read_csv(self.missing_settings_file)
                for _, row in missing_df.iterrows():
                    self.missing_strategies[row['column']] = row.to_dict()
                print(f"Loaded missing value settings for {len(self.missing_strategies)} columns")
            
            # Load drop value settings
            if self.drop_settings_file.exists():
                drop_df = pd.read_csv(self.drop_settings_file)
                for column in drop_df['column'].unique():
                    values = drop_df[drop_df['column'] == column]['value_to_drop'].tolist()
                    self.drop_values[column] = values
                print(f"Loaded drop value settings for {len(self.drop_values)} columns")
            
            return True
            
        except Exception as e:
            print(f"Error loading preferences: {str(e)}")
            return False
    
    def process_user_preferences(self, 
                               dataframe: pd.DataFrame,
                               interactive: bool = True,
                               force_reconfigure: bool = False) -> bool:
        """
        Complete workflow: load existing preferences or collect new ones, then save.
        
        Args:
            dataframe: DataFrame to analyze
            interactive: If True, prompt user for preferences
            force_reconfigure: If True, ignore existing settings and reconfigure
            
        Returns:
            bool: True if process completed successfully
        """
        # Check if settings already exist
        settings_exist = (self.missing_settings_file.exists() or 
                         self.drop_settings_file.exists())
        
        if settings_exist and not force_reconfigure:
            print("Found existing missing value and drop settings.")
            if interactive:
                use_existing = input("Use existing settings? (y/n): ").strip().lower()
                if use_existing in ['y', 'yes']:
                    return self.load_preferences_from_csv()
        
        # Collect new preferences
        success = self.collect_user_preferences(dataframe, interactive)
        if not success:
            return False
        
        # Save preferences
        return self.save_preferences_to_csv()

def main():
    """
    Example usage of ValueMissingAndDroppingHandler.
    """
    print("ValueMissingAndDroppingHandler - Example Usage")
    print("To use this module:")
    print()
    print("from wave_visualizer.data_prep.cleaning.value_missing_and_dropping_handler import ValueMissingAndDroppingHandler")
    print("import pandas as pd")
    print()
    print("# Initialize handler")
    print("handler = ValueMissingAndDroppingHandler('./cleaning_settings/')")
    print()
    print("# Process user preferences")
    print("success = handler.process_user_preferences(df, interactive=True)")
    print()
    print("# Load existing preferences")
    print("handler.load_preferences_from_csv()")

if __name__ == "__main__":
    main() 