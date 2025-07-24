"""
Value Merging Handler

Records user preferences for combining categorical values into target groups.
Saves merging rules as CSV for consistent application across the cleaning pipeline.

Example use cases:
- Combine "Other" and "Something else" into "Independent" for party affiliation
- Group similar response categories for cleaner visualizations
- Consolidate rare categories into meaningful groups
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')

class ValueMergingHandler:
    """
    Handles user preferences for merging categorical values into target groups.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the handler.
        
        Args:
            output_dir: Directory to save merging preference CSV files (defaults to package settings folder)
        """
        # Use settings folder within package if no output_dir specified
        if output_dir is None:
            from wave_visualizer.settings import CLEANING_DIR
            self.output_dir = CLEANING_DIR
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True)
        
        self.merging_settings_file = self.output_dir / "value_merging_settings.csv"
        
        # Storage for user preferences
        self.merging_rules = {}
        
    def analyze_column_values(self, dataframe: pd.DataFrame, column_name: str) -> Dict[str, Any]:
        """
        Analyze unique values in a column to help user decide on merging.
        
        Args:
            dataframe: DataFrame containing the data
            column_name: Name of the column to analyze
            
        Returns:
            Dict: Analysis results including unique values and counts
        """
        if column_name not in dataframe.columns:
            raise ValueError(f"Column '{column_name}' not found in dataframe")
        
        column_data = dataframe[column_name].dropna()
        unique_values = column_data.unique()
        value_counts = column_data.value_counts()
        
        return {
            'column_name': column_name,
            'total_non_missing': len(column_data),
            'unique_count': len(unique_values),
            'unique_values': unique_values.tolist(),
            'value_counts': value_counts.to_dict(),
            'sample_values': unique_values[:10].tolist()
        }
    
    def get_user_merging_preferences(self, 
                                   column_name: str, 
                                   column_analysis: Dict[str, Any],
                                   interactive: bool = True) -> Dict[str, List[Any]]:
        """
        Get user preferences for merging values in a specific column.
        
        Args:
            column_name: Name of the column
            column_analysis: Analysis results from analyze_column_values
            interactive: If True, prompt user; if False, return empty rules
            
        Returns:
            Dict: Mapping of target values to lists of source values to merge
        """
        if not interactive:
            return {}
        
        print(f"\n{'='*60}")
        print(f"VALUE MERGING FOR: {column_name}")
        print(f"{'='*60}")
        print(f"Total non-missing values: {column_analysis['total_non_missing']}")
        print(f"Unique values: {column_analysis['unique_count']}")
        print()
        
        # Show value counts
        print("Value distribution:")
        value_counts = column_analysis['value_counts']
        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (value, count) in enumerate(sorted_values):
            percentage = (count / column_analysis['total_non_missing']) * 100
            print(f"  {i+1:2d}. {value}: {count} ({percentage:.1f}%)")
            if i >= 19:  # Show top 20
                remaining = len(sorted_values) - 20
                if remaining > 0:
                    print(f"      ... and {remaining} more values")
                break
        
        print(f"\nOptions:")
        print("1. No merging needed for this column")
        print("2. Create merging rules for this column")
        print()
        
        while True:
            try:
                choice = input("Choose option (1-2): ").strip()
                
                if choice == '1':
                    return {}
                
                elif choice == '2':
                    return self._collect_merging_rules(column_name, sorted_values)
                
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    continue
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return {}
            except Exception as e:
                print(f"Error: {str(e)}. Please try again.")
                continue
    
    def _collect_merging_rules(self, column_name: str, sorted_values: List[tuple]) -> Dict[str, List[Any]]:
        """
        Collect specific merging rules from user.
        
        Args:
            column_name: Name of the column
            sorted_values: List of (value, count) tuples sorted by frequency
            
        Returns:
            Dict: Mapping of target values to source values to merge
        """
        merging_rules = {}
        available_values = [value for value, count in sorted_values]
        
        print(f"\nCreating merging rules for '{column_name}':")
        print("You can create multiple merge groups. For each group, specify:")
        print("- Target name (what the merged values should become)")
        print("- Source values (which original values to merge into the target)")
        print()
        
        group_number = 1
        
        while True:
            try:
                print(f"\n--- Merge Group {group_number} ---")
                
                # Show remaining available values
                if available_values:
                    print("Available values to merge:")
                    for i, value in enumerate(available_values[:15], 1):
                        print(f"  {i:2d}. {value}")
                    if len(available_values) > 15:
                        print(f"      ... and {len(available_values) - 15} more")
                    print()
                else:
                    print("No more values available to merge.")
                    break
                
                # Ask if user wants to create another group
                if group_number > 1:
                    create_group = input("Create another merge group? (y/n): ").strip().lower()
                    if create_group not in ['y', 'yes']:
                        break
                
                # Get target name
                target_name = input("Enter target name for this merge group: ").strip()
                if not target_name:
                    print("Target name cannot be empty.")
                    continue
                
                # Get source values
                print("Select source values to merge into this target:")
                print("Options:")
                print("1. Enter values by name (comma-separated)")
                print("2. Enter numbers from the list above (comma-separated)")
                
                selection_method = input("Choose method (1-2): ").strip()
                
                source_values = []
                
                if selection_method == '1':
                    values_input = input("Enter values to merge (comma-separated): ").strip()
                    if values_input:
                        candidate_values = [v.strip() for v in values_input.split(',')]
                        for val in candidate_values:
                            if val in available_values:
                                source_values.append(val)
                                available_values.remove(val)
                            else:
                                print(f"Warning: '{val}' not found in available values")
                
                elif selection_method == '2':
                    numbers_input = input("Enter numbers (comma-separated): ").strip()
                    if numbers_input:
                        try:
                            numbers = [int(n.strip()) for n in numbers_input.split(',')]
                            for num in numbers:
                                if 1 <= num <= len(available_values):
                                    val = available_values[num-1]
                                    source_values.append(val)
                                    available_values.remove(val)
                                else:
                                    print(f"Warning: Number {num} is out of range")
                        except ValueError:
                            print("Invalid numbers entered.")
                            continue
                
                if source_values:
                    merging_rules[target_name] = source_values
                    print(f"Created merge rule: {source_values} → '{target_name}'")
                    group_number += 1
                else:
                    print("No valid source values selected.")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"Error: {str(e)}. Please try again.")
                continue
        
        return merging_rules
    
    def collect_merging_preferences(self, 
                                  dataframe: pd.DataFrame,
                                  interactive: bool = True,
                                  columns_to_process: Optional[List[str]] = None) -> bool:
        """
        Collect merging preferences for specified columns or let user choose.
        
        Args:
            dataframe: DataFrame to analyze
            interactive: If True, prompt user; if False, use defaults
            columns_to_process: Specific columns to process, None to let user choose
            
        Returns:
            bool: True if collection was successful
        """
        print("="*60)
        print("VALUE MERGING HANDLER")
        print("="*60)
        
        if not interactive:
            print("Non-interactive mode: No merging rules will be created")
            return True
        
        # Determine which columns to process
        if columns_to_process is None:
            # Let user choose columns
            categorical_columns = []
            for col in dataframe.columns:
                if dataframe[col].dtype == 'object' or dataframe[col].nunique() < 20:
                    categorical_columns.append(col)
            
            if not categorical_columns:
                print("No suitable categorical columns found for merging.")
                return True
            
            print(f"Found {len(categorical_columns)} potential columns for value merging:")
            for i, col in enumerate(categorical_columns[:20], 1):
                unique_count = dataframe[col].nunique()
                print(f"  {i:2d}. {col} ({unique_count} unique values)")
            
            if len(categorical_columns) > 20:
                print(f"      ... and {len(categorical_columns) - 20} more columns")
            
            print("\nSelect columns to configure merging rules:")
            columns_input = input("Enter column numbers (comma-separated) or 'none': ").strip()
            
            if columns_input.lower() == 'none':
                print("No merging rules will be created.")
                return True
            
            try:
                selected_indices = [int(n.strip()) - 1 for n in columns_input.split(',')]
                columns_to_process = [categorical_columns[i] for i in selected_indices 
                                    if 0 <= i < len(categorical_columns)]
            except (ValueError, IndexError):
                print("Invalid selection. No merging rules will be created.")
                return True
        
        # Process selected columns
        for column in columns_to_process:
            if column not in dataframe.columns:
                print(f"Warning: Column '{column}' not found in dataframe")
                continue
            
            try:
                analysis = self.analyze_column_values(dataframe, column)
                merging_rules = self.get_user_merging_preferences(column, analysis, interactive)
                
                if merging_rules:
                    self.merging_rules[column] = merging_rules
                    print(f"Merging rules saved for column '{column}'")
                else:
                    print(f"No merging rules created for column '{column}'")
                    
            except Exception as e:
                print(f"Error processing column '{column}': {str(e)}")
                continue
        
        return True
    
    def save_preferences_to_csv(self) -> bool:
        """
        Save merging preferences to CSV file.
        
        Returns:
            bool: True if save was successful
        """
        try:
            if not self.merging_rules:
                print("No merging rules to save.")
                return True
            
            # Convert merging rules to CSV format
            rows = []
            for column_name, merge_groups in self.merging_rules.items():
                for target_value, source_values in merge_groups.items():
                    for source_value in source_values:
                        rows.append({
                            'column_name': column_name,
                            'source_value': source_value,
                            'target_value': target_value
                        })
            
            if rows:
                merging_df = pd.DataFrame(rows)
                merging_df.to_csv(self.merging_settings_file, index=False)
                print(f"Merging settings saved to: {self.merging_settings_file}")
                print(f"Total merging rules: {len(rows)}")
            
            return True
            
        except Exception as e:
            print(f"Error saving merging preferences: {str(e)}")
            return False
    
    def load_preferences_from_csv(self) -> bool:
        """
        Load previously saved merging preferences from CSV file.
        
        Returns:
            bool: True if load was successful
        """
        try:
            if not self.merging_settings_file.exists():
                print("No existing merging settings file found.")
                return True
            
            merging_df = pd.read_csv(self.merging_settings_file)
            
            # Convert CSV back to nested dictionary structure
            self.merging_rules = {}
            for _, row in merging_df.iterrows():
                column = row['column_name']
                source_val = row['source_value']
                target_val = row['target_value']
                
                if column not in self.merging_rules:
                    self.merging_rules[column] = {}
                
                if target_val not in self.merging_rules[column]:
                    self.merging_rules[column][target_val] = []
                
                self.merging_rules[column][target_val].append(source_val)
            
            print(f"Loaded merging settings for {len(self.merging_rules)} columns")
            return True
            
        except Exception as e:
            print(f"Error loading merging preferences: {str(e)}")
            return False
    
    def get_merging_rules(self, column_name: str) -> Dict[str, List[Any]]:
        """
        Get merging rules for a specific column.
        
        Args:
            column_name: Name of the column
            
        Returns:
            Dict: Merging rules for the column (target -> [source_values])
        """
        return self.merging_rules.get(column_name, {})
    
    def apply_merging_rules(self, column_data: pd.Series, column_name: str) -> pd.Series:
        """
        Apply merging rules to a column of data.
        
        Args:
            column_data: Pandas Series containing the data
            column_name: Name of the column (for looking up rules)
            
        Returns:
            pd.Series: Data with merging rules applied
        """
        merging_rules = self.get_merging_rules(column_name)
        
        if not merging_rules:
            return column_data.copy()
        
        merged_data = column_data.copy()
        
        # Apply each merging rule
        for target_value, source_values in merging_rules.items():
            for source_value in source_values:
                mask = (merged_data == source_value)
                merged_data.loc[mask] = target_value
        
        return merged_data
    
    def process_merging_preferences(self, 
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
        settings_exist = self.merging_settings_file.exists()
        
        if settings_exist and not force_reconfigure:
            print("Found existing merging settings.")
            if interactive:
                use_existing = input("Use existing settings? (y/n): ").strip().lower()
                if use_existing in ['y', 'yes']:
                    return self.load_preferences_from_csv()
        
        # Collect new preferences
        success = self.collect_merging_preferences(dataframe, interactive)
        if not success:
            return False
        
        # Save preferences
        return self.save_preferences_to_csv()

def main():
    """
    Example usage of ValueMergingHandler.
    """
    print("ValueMergingHandler - Example Usage")
    print("To use this module:")
    print()
    print("from wave_visualizer.data_prep.cleaning.value_merging_handler import ValueMergingHandler")
    print("import pandas as pd")
    print()
    print("# Initialize handler")
    print("handler = ValueMergingHandler()")
    print()
    print("# Process merging preferences")
    print("success = handler.process_merging_preferences(df, interactive=True)")
    print()
    print("# Apply merging rules to a column")
    print("merged_column = handler.apply_merging_rules(df['party_col'], 'party_col')")

if __name__ == "__main__":
    main() 