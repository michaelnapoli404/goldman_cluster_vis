"""
Metadata Handler

Extracts variable labels and value-to-label mappings from SPSS .sav files
and saves them in a structured CSV format for use by other modules.

This version is specifically designed to work with .sav files only and
automatically detects .sav files in the data folder.
"""

import pandas as pd
import os
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import glob

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class MetadataHandler:
    """
    Handles extraction and storage of dataset metadata from SPSS .sav files only.
    Automatically detects .sav files in the data folder.
    """
    
    def __init__(self, data_folder: str = "./data/", output_dir: str = None):
        """
        Initialize the MetadataHandler.
        
        Args:
            data_folder: Folder containing .sav files
            output_dir: Directory to save metadata CSV files (defaults to package settings folder)
        """
        self.data_folder = Path(data_folder)
        
        # Use settings folder within package if no output_dir specified
        if output_dir is None:
            from wave_visualizer.settings import METADATA_DIR
            self.output_dir = METADATA_DIR
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True)
        
        # Output file paths
        self.variable_labels_file = self.output_dir / "variable_labels.csv"
        self.value_labels_file = self.output_dir / "value_labels.csv"
        
        # Storage for extracted metadata
        self.variable_labels = {}
        self.value_labels = {}
        self.data_file_path = None
        
    def find_sav_files(self) -> List[Path]:
        """
        Find all .sav files in the data folder.
        
        Returns:
            List[Path]: List of .sav file paths
        """
        if not self.data_folder.exists():
            print(f"Error: Data folder does not exist: {self.data_folder}")
            print(f"Please create the folder and place your .sav files there.")
            return []
        
        sav_files = list(self.data_folder.glob("*.sav"))
        
        if not sav_files:
            print(f"Error: No .sav files found in {self.data_folder}")
            print(f"Please place your SPSS .sav files in the data folder.")
            return []
        
        return sav_files
    
    def select_sav_file(self, interactive: bool = True) -> Optional[Path]:
        """
        Select which .sav file to process.
        
        Args:
            interactive: If True, prompt user to select; if False, use first file
            
        Returns:
            Path: Selected .sav file path, None if no valid selection
        """
        sav_files = self.find_sav_files()
        
        if not sav_files:
            return None
        
        if len(sav_files) == 1:
            selected_file = sav_files[0]
            print(f"Found one .sav file: {selected_file.name}")
            return selected_file
        
        if not interactive:
            # Use first file if not interactive
            selected_file = sav_files[0]
            print(f"Using first .sav file: {selected_file.name}")
            return selected_file
        
        # Multiple files - let user choose
        print(f"Found {len(sav_files)} .sav files in {self.data_folder}:")
        for i, file_path in enumerate(sav_files, 1):
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  {i}. {file_path.name} ({file_size:.1f} MB)")
        
        while True:
            try:
                choice = input(f"Select file (1-{len(sav_files)}): ").strip()
                file_index = int(choice) - 1
                
                if 0 <= file_index < len(sav_files):
                    return sav_files[file_index]
                else:
                    print(f"Invalid choice. Please enter 1-{len(sav_files)}")
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                return None
    
    def validate_file_format(self, file_path: Path) -> bool:
        """
        Validate that the file is a .sav file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file is .sav format, False otherwise
        """
        if not file_path.exists():
            print(f"Error: File does not exist: {file_path}")
            return False
        
        if file_path.suffix.lower() != '.sav':
            print(f"Error: File is not a .sav file: {file_path}")
            print(f"This handler only works with SPSS .sav files.")
            print(f"File extension found: {file_path.suffix}")
            return False
        
        return True
    
    def extract_metadata(self, file_path: Path) -> bool:
        """
        Extract metadata from the specified .sav file.
        
        Args:
            file_path: Path to the .sav file
            
        Returns:
            bool: True if metadata extraction was successful, False otherwise
        """
        if not self.validate_file_format(file_path):
            return False
        
        print(f"Extracting metadata from: {file_path.name}")
        print(f"File size: {file_path.stat().st_size / (1024 * 1024):.1f} MB")
        
        try:
            import pyreadstat
            
            # Read the file with metadata
            print("Reading SPSS file...")
            df, meta = pyreadstat.read_sav(str(file_path))
            
            # Extract variable labels
            if meta.column_labels:
                self.variable_labels = dict(zip(meta.column_names, meta.column_labels))
            else:
                self.variable_labels = {col: col for col in meta.column_names}
            
            # Extract value labels
            if meta.variable_value_labels:
                self.value_labels = meta.variable_value_labels
            
            print(f"Successfully extracted SPSS metadata:")
            print(f"  - Total variables: {len(meta.column_names)}")
            print(f"  - Variables with labels: {len(self.variable_labels)}")
            print(f"  - Variables with value labels: {len(self.value_labels)}")
            print(f"  - Total observations: {len(df)}")
            
            # Store the file path for reference
            self.data_file_path = file_path
            
            return True
            
        except ImportError:
            print("Error: pyreadstat package required for SPSS files.")
            print("Install with: pip install pyreadstat")
            return False
        except Exception as e:
            print(f"Error reading SPSS file: {str(e)}")
            return False
    
    def save_metadata_to_csv(self) -> bool:
        """
        Save extracted metadata to CSV files.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Save variable labels
            if self.variable_labels:
                var_labels_df = pd.DataFrame([
                    {'variable_name': var, 'variable_label': label}
                    for var, label in self.variable_labels.items()
                ])
                var_labels_df.to_csv(self.variable_labels_file, index=False)
                print(f"Variable labels saved to: {self.variable_labels_file}")
            
            # Save value labels in a structured format
            if self.value_labels:
                value_labels_rows = []
                for variable, value_mapping in self.value_labels.items():
                    for value, label in value_mapping.items():
                        value_labels_rows.append({
                            'variable_name': variable,
                            'value': value,
                            'value_label': label
                        })
                
                if value_labels_rows:
                    value_labels_df = pd.DataFrame(value_labels_rows)
                    value_labels_df.to_csv(self.value_labels_file, index=False)
                    print(f"Value labels saved to: {self.value_labels_file}")
                else:
                    print("No value labels found to save")
            else:
                print("No value labels found to save")
            
            return True
            
        except Exception as e:
            print(f"Error saving metadata to CSV: {str(e)}")
            return False
    
    def get_variable_label(self, variable_name: str) -> str:
        """
        Get the label for a specific variable.
        
        Args:
            variable_name: Name of the variable
            
        Returns:
            str: Variable label or the variable name if no label exists
        """
        return self.variable_labels.get(variable_name, variable_name)
    
    def get_value_labels(self, variable_name: str) -> Dict[Any, str]:
        """
        Get value labels for a specific variable.
        
        Args:
            variable_name: Name of the variable
            
        Returns:
            Dict: Mapping of values to labels, empty dict if no labels exist
        """
        return self.value_labels.get(variable_name, {})
    
    def show_metadata_summary(self) -> None:
        """
        Display a summary of the extracted metadata.
        """
        if not self.variable_labels and not self.value_labels:
            print("No metadata has been extracted yet.")
            return
        
        print("="*60)
        print("METADATA SUMMARY")
        print("="*60)
        
        if self.data_file_path:
            print(f"Source file: {self.data_file_path.name}")
        
        print(f"Total variables: {len(self.variable_labels)}")
        print(f"Variables with value labels: {len(self.value_labels)}")
        
        if self.value_labels:
            print("\nVariables with value labels:")
            for var_name, value_map in list(self.value_labels.items())[:10]:  # Show first 10
                print(f"  {var_name}: {len(value_map)} labels")
                # Show first few labels as example
                sample_labels = list(value_map.items())[:3]
                for value, label in sample_labels:
                    print(f"    {value} -> '{label}'")
                if len(value_map) > 3:
                    print(f"    ... and {len(value_map) - 3} more")
            
            if len(self.value_labels) > 10:
                print(f"  ... and {len(self.value_labels) - 10} more variables")
    
    def process_metadata(self, interactive: bool = True) -> bool:
        """
        Complete metadata processing pipeline: select file, extract, and save.
        
        Args:
            interactive: If True, prompt user for file selection
            
        Returns:
            bool: True if entire process was successful, False otherwise
        """
        print("="*60)
        print("METADATA HANDLER - Processing .sav File Metadata")
        print("="*60)
        
        # Select .sav file
        selected_file = self.select_sav_file(interactive)
        if not selected_file:
            print("No valid .sav file selected.")
            return False
        
        # Extract metadata
        if not self.extract_metadata(selected_file):
            print("Failed to extract metadata")
            return False
        
        # Show summary
        self.show_metadata_summary()
        
        # Save to CSV
        if not self.save_metadata_to_csv():
            print("Failed to save metadata")
            return False
        
        print("="*60)
        print("Metadata processing completed successfully!")
        print(f"Files saved in: {self.output_dir}")
        print("="*60)
        
        return True

def main():
    """
    Example usage of MetadataHandler.
    """
    print("MetadataHandler - SPSS .sav File Processor")
    print("To use this module:")
    print()
    print("1. Place your .sav files in the ./data/ folder")
    print("2. Run the processor:")
    print()
    print("from wave_visualizer.data_prep.cleaning.metadata_handler import MetadataHandler")
    print()
    print("# Initialize handler")
    print("handler = MetadataHandler('./data/')")
    print()
    print("# Process metadata")
    print("success = handler.process_metadata()")

if __name__ == "__main__":
    main() 