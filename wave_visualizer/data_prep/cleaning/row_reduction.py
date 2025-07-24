"""
Row Reduction Handler for Wave Visualizer

This module provides functionality for filtering rows in survey data based on
specific criteria. It allows interactive selection of filtering conditions and
can save/load these settings for consistent application across different sessions.

Key Features:
- Interactive row filtering based on categorical variables
- Save/load filtering settings to/from CSV files
- Robust error handling and validation
- Support for multiple filtering criteria
- Statistical reporting on filtering results

This module is part of the data cleaning pipeline and helps ensure that
analysis is performed on the appropriate subset of data.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RowReductionHandler:
    """
    Handles row filtering operations for survey data.
    
    This class provides methods to interactively select filtering criteria,
    apply filters to data, and manage persistent settings for consistent
    filtering across different analysis sessions.
    """
    
    def __init__(self):
        """Initialize the RowReductionHandler."""
        self.settings_file = "wave_visualizer/settings/cleaning_settings/row_reduction_settings.csv"
        self.settings_dir = Path("wave_visualizer/settings/cleaning_settings")
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
    def get_categorical_columns(self, data: pd.DataFrame) -> List[str]:
        """
        Identify categorical columns in the dataset.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            List of column names that contain categorical data
        """
        categorical_columns = []
        
        for column in data.columns:
            # Check if column is object type or has limited unique values
            if (data[column].dtype == 'object' or 
                (data[column].dtype in ['int64', 'float64'] and 
                 data[column].nunique() <= 20)):  # Assume <=20 unique values means categorical
                categorical_columns.append(column)
                
        return categorical_columns
    
    def display_column_info(self, data: pd.DataFrame, column: str) -> None:
        """
        Display information about a specific column.
        
        Args:
            data: DataFrame containing the column
            column: Name of the column to analyze
        """
        if column not in data.columns:
            print(f"  WARNING: Column '{column}' not found in dataset")
            return
            
        print(f"\nColumn: {column}")
        print(f"Data type: {data[column].dtype}")
        print(f"Total values: {len(data[column])}")
        print(f"Non-null values: {data[column].count()}")
        print(f"Null values: {data[column].isnull().sum()}")
        print(f"Unique values: {data[column].nunique()}")
        
        # Show value counts for categorical data
        if data[column].nunique() <= 20:
            print("\nValue counts:")
            value_counts = data[column].value_counts(dropna=False)
            for value, count in value_counts.head(10).items():
                percentage = (count / len(data)) * 100
                print(f"  {value}: {count} ({percentage:.1f}%)")
            
            if len(value_counts) > 10:
                print(f"  ... and {len(value_counts) - 10} more values")
    
    def get_filtering_criteria(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Interactively collect filtering criteria from the user.
        
        Args:
            data: DataFrame to be filtered
            
        Returns:
            Dictionary containing filtering criteria
        """
        print("\n" + "="*60)
        print("ROW FILTERING SETUP")
        print("="*60)
        print("Choose which rows to keep in your analysis.")
        print("You can filter by categorical variables (e.g., party affiliation, demographics).")
        
        categorical_columns = self.get_categorical_columns(data)
        
        if not categorical_columns:
            print("\nNo suitable categorical columns found for filtering.")
            return {"filters": []}
        
        print(f"\nAvailable categorical columns ({len(categorical_columns)}):")
        for i, column in enumerate(categorical_columns, 1):
            unique_count = data[column].nunique()
            print(f"{i}. {column} ({unique_count} unique values)")
        
        filters = []
        
        while True:
            print(f"\nCurrent filters: {len(filters)}")
            if filters:
                for i, filter_item in enumerate(filters, 1):
                    values_str = ", ".join(str(v) for v in filter_item['values'][:3])
                    if len(filter_item['values']) > 3:
                        values_str += f" (and {len(filter_item['values'])-3} more)"
                    print(f"  {i}. Keep rows where {filter_item['column']} is: {values_str}")
            
            print(f"\nOptions:")
            print("1. Add a new filter")
            if filters:
                print("2. Remove a filter")
                print("3. Clear all filters")
            print("0. Finish and apply filters" if filters else "0. Skip filtering (keep all rows)")
            
            try:
                choice = input("\nEnter your choice: ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    # Add new filter
                    filter_item = self._add_filter(data, categorical_columns)
                    if filter_item:
                        filters.append(filter_item)
                elif choice == "2" and filters:
                    # Remove filter
                    self._remove_filter(filters)
                elif choice == "3" and filters:
                    # Clear all filters
                    filters.clear()
                    print("All filters cleared.")
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nFiltering setup cancelled.")
                return {"filters": []}
        
        return {"filters": filters}
    
    def _add_filter(self, data: pd.DataFrame, categorical_columns: List[str]) -> Optional[Dict[str, Any]]:
        """
        Add a single filter interactively.
        
        Args:
            data: DataFrame to filter
            categorical_columns: List of available categorical columns
            
        Returns:
            Dictionary containing filter specification, or None if cancelled
        """
        print(f"\nSelect a column to filter by:")
        for i, column in enumerate(categorical_columns, 1):
            print(f"{i}. {column}")
        
        try:
            column_choice = input("Enter column number: ").strip()
            column_idx = int(column_choice) - 1
            
            if column_idx < 0 or column_idx >= len(categorical_columns):
                print("Invalid column number.")
                return None
            
            column = categorical_columns[column_idx]
            
            # Display column information
            self.display_column_info(data, column)
            
            # Get unique values
            unique_values = data[column].dropna().unique()
            unique_values = sorted(unique_values) if len(unique_values) < 50 else unique_values
            
            print(f"\nUnique values in {column}:")
            for i, value in enumerate(unique_values, 1):
                count = (data[column] == value).sum()
                percentage = (count / len(data)) * 100
                print(f"{i}. {value} ({count} rows, {percentage:.1f}%)")
            
            print(f"\nSelect which values to KEEP (enter numbers separated by commas):")
            print(f"Example: 1,3,5 to keep values 1, 3, and 5")
            
            selection = input("Enter your selection: ").strip()
            
            if not selection:
                print("No selection made.")
                return None
            
            # Parse selection
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                selected_values = []
                
                for idx in indices:
                    if 0 <= idx < len(unique_values):
                        selected_values.append(unique_values[idx])
                    else:
                        print(f"Warning: Index {idx + 1} is out of range")
                
                if not selected_values:
                    print("No valid values selected.")
                    return None
                
                # Calculate impact
                total_rows = len(data)
                kept_rows = data[column].isin(selected_values).sum()
                removed_rows = total_rows - kept_rows
                
                print(f"\nFilter impact:")
                print(f"  Total rows: {total_rows:,}")
                print(f"  Rows to keep: {kept_rows:,} ({(kept_rows/total_rows)*100:.1f}%)")
                print(f"  Rows to remove: {removed_rows:,} ({(removed_rows/total_rows)*100:.1f}%)")
                
                confirm = input("\nConfirm this filter? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Filter cancelled.")
                    return None
                
                return {
                    "column": column,
                    "values": selected_values,
                    "kept_rows": kept_rows,
                    "total_rows": total_rows
                }
                
            except ValueError:
                print("Invalid selection format. Please use numbers separated by commas.")
                return None
                
        except (ValueError, KeyboardInterrupt):
            print("Filter setup cancelled.")
            return None
    
    def _remove_filter(self, filters: List[Dict[str, Any]]) -> None:
        """
        Remove a filter from the list.
        
        Args:
            filters: List of current filters
        """
        if not filters:
            return
        
        print("\nCurrent filters:")
        for i, filter_item in enumerate(filters, 1):
            values_str = ", ".join(str(v) for v in filter_item['values'][:3])
            if len(filter_item['values']) > 3:
                values_str += f" (and {len(filter_item['values'])-3} more)"
            print(f"{i}. {filter_item['column']}: {values_str}")
        
        try:
            choice = input("Enter filter number to remove: ").strip()
            filter_idx = int(choice) - 1
            
            if 0 <= filter_idx < len(filters):
                removed_filter = filters.pop(filter_idx)
                print(f"Removed filter for column '{removed_filter['column']}'")
            else:
                print("Invalid filter number.")
                
        except ValueError:
            print("Invalid input.")
    
    def apply_filters(self, data: pd.DataFrame, settings: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filtering criteria to the data.
        
        Args:
            data: DataFrame to filter
            settings: Dictionary containing filter specifications
            
        Returns:
            Filtered DataFrame
        """
        if not settings.get("filters"):
            logger.info("No filters specified. Returning original data.")
            return data.copy()
        
        original_count = len(data)
        filtered_data = data.copy()
        
        logger.info(f"Applying {len(settings['filters'])} filters to {original_count:,} rows")
        
        for i, filter_item in enumerate(settings["filters"], 1):
            column = filter_item["column"]
            values = filter_item["values"]
            
            if column not in filtered_data.columns:
                logger.warning(f"Filter {i}: Column '{column}' not found. Skipping.")
                continue
            
            before_count = len(filtered_data)
            filtered_data = filtered_data[filtered_data[column].isin(values)]
            after_count = len(filtered_data)
            
            logger.info(f"Filter {i} ({column}): {before_count:,} → {after_count:,} rows")
        
        final_count = len(filtered_data)
        removed_count = original_count - final_count
        removal_rate = (removed_count / original_count) * 100
        
        print(f"\nFiltering Results:")
        print(f"  Original rows: {original_count:,}")
        print(f"  Final rows: {final_count:,}")
        print(f"  Removed rows: {removed_count:,} ({removal_rate:.1f}%)")
        
        if final_count == 0:
            logger.error("All rows were filtered out! Check your filtering criteria.")
            raise ValueError("Filtering removed all data rows")
        elif final_count < 100:
            logger.warning(f"Very few rows remain ({final_count}). Consider reviewing filters.")
        
        return filtered_data
    
    def save_settings(self, settings: Dict[str, Any]) -> None:
        """
        Save filtering settings to CSV file.
        
        Args:
            settings: Dictionary containing filter specifications
        """
        try:
            # Convert to DataFrame format for CSV storage
            if settings.get("filters"):
                records = []
                for filter_item in settings["filters"]:
                    for value in filter_item["values"]:
                        records.append({
                            "column": filter_item["column"],
                            "value": value,
                            "action": "keep"
                        })
                
                df = pd.DataFrame(records)
                df.to_csv(self.settings_file, index=False)
                logger.info(f"Row filtering settings saved to {self.settings_file}")
            else:
                # Save empty file to indicate no filtering
                df = pd.DataFrame(columns=["column", "value", "action"])
                df.to_csv(self.settings_file, index=False)
                logger.info("No filtering settings saved (no filters specified)")
                
        except Exception as e:
            logger.error(f"Failed to save row filtering settings: {e}")
            raise
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load filtering settings from CSV file.
        
        Returns:
            Dictionary containing filter specifications
        """
        if not os.path.exists(self.settings_file):
            logger.info("No existing row filtering settings found")
            return {"filters": []}
        
        try:
            df = pd.read_csv(self.settings_file)
            
            if df.empty:
                return {"filters": []}
            
            # Group by column and collect values
            filters = []
            for column in df["column"].unique():
                column_data = df[df["column"] == column]
                values = column_data["value"].tolist()
                
                filters.append({
                    "column": column,
                    "values": values
                })
            
            logger.info(f"Loaded row filtering settings for {len(filters)} columns")
            return {"filters": filters}
            
        except Exception as e:
            logger.error(f"Failed to load row filtering settings: {e}")
            return {"filters": []}
    
    def interactive_setup(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run interactive setup for row filtering.
        
        Args:
            data: DataFrame to be filtered
            
        Returns:
            Dictionary containing filter specifications
        """
        print(f"\nDataset shape: {data.shape[0]:,} rows × {data.shape[1]} columns")
        
        # Check for existing settings
        existing_settings = self.load_settings()
        
        if existing_settings.get("filters"):
            print(f"\nFound existing filtering settings:")
            for filter_item in existing_settings["filters"]:
                values_str = ", ".join(str(v) for v in filter_item['values'][:3])
                if len(filter_item['values']) > 3:
                    values_str += f" (and {len(filter_item['values'])-3} more)"
                print(f"  - Keep {filter_item['column']}: {values_str}")
            
            use_existing = input("\nUse existing settings? (y/n): ").strip().lower()
            if use_existing == 'y':
                return existing_settings
        
        # Get new filtering criteria
        settings = self.get_filtering_criteria(data)
        
        # Save settings if any filters were specified
        if settings.get("filters"):
            self.save_settings(settings)
        
        return settings


def process_row_reduction(data: pd.DataFrame, 
                         interactive: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Main function to process row reduction/filtering.
    
    Args:
        data: DataFrame to process
        interactive: Whether to run in interactive mode
        
    Returns:
        Tuple of (filtered_data, settings_dict)
    """
    handler = RowReductionHandler()
    
    if interactive:
        # Interactive mode: get user input
        settings = handler.interactive_setup(data)
    else:
        # Non-interactive mode: load existing settings or use defaults
        settings = handler.load_settings()
        if settings.get("filters"):
            print(f"Applying {len(settings['filters'])} saved filtering rules...")
    
    # Apply filters
    if settings.get("filters"):
        filtered_data = handler.apply_filters(data, settings)
    else:
        filtered_data = data.copy()
        print("No row filtering applied - keeping all rows")
    
    return filtered_data, settings


# Example usage
if __name__ == "__main__":
    # This would normally be imported and used by the main cleaning pipeline
    pass 