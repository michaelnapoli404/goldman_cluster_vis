"""
Color Mapping module for wave_visualizer package.

Handles semantic color assignments where users can specify exact colors 
for specific variable values (e.g., Republican=#d62728, Democrat=#1f77b4).
Falls back to default color schemes for unmapped values.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')

class ColorMappingHandler:
    """
    Handles semantic color mappings for visualization variables.
    """
    
    def __init__(self, settings_dir: Optional[str] = None):
        """
        Initialize the color mapping handler.
        
        Args:
            settings_dir: Directory containing color mapping CSV files
        """
        if settings_dir is None:
            from wave_visualizer.settings import VISUALIZATION_DIR
            self.settings_dir = VISUALIZATION_DIR
        else:
            self.settings_dir = Path(settings_dir)
        
        self.color_mappings_file = self.settings_dir / "value_color_mappings.csv"
        
        # Storage for loaded mappings
        self.value_color_mappings = {}  # {variable_name: {value_name: color_hex}}
        
        # Load existing mappings
        self._load_color_mappings()
    
    def _load_color_mappings(self) -> bool:
        """Load value-specific color mappings from CSV."""
        try:
            if not self.color_mappings_file.exists():
                print("No value color mappings found - will use default schemes")
                return True
            
            mappings_df = pd.read_csv(self.color_mappings_file)
            
            # Group by variable to create nested dictionary
            for variable in mappings_df['variable_name'].unique():
                var_data = mappings_df[mappings_df['variable_name'] == variable]
                self.value_color_mappings[variable] = dict(zip(
                    var_data['value_name'], 
                    var_data['color_hex']
                ))
            
            print(f"Loaded color mappings for {len(self.value_color_mappings)} variables")
            return True
            
        except Exception as e:
            print(f"Error loading color mappings: {str(e)}")
            return False
    

    
    def get_colors_for_variable(self, variable_name: str, values: List[str]) -> List[str]:
        """
        Get colors for specific variable values using semantic mappings.
        
        Args:
            variable_name: Name of the variable (e.g., 'PID1_labeled')
            values: List of value names to get colors for
            
        Returns:
            List of color hex codes in same order as values
        """
        colors = []
        variable_mappings = self.value_color_mappings.get(variable_name, {})
        
        # Default color palette for unmapped values
        default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        unmapped_count = 0
        
        for value in values:
            if value in variable_mappings:
                # Use semantic mapping
                colors.append(variable_mappings[value])
            else:
                # Use default color palette
                colors.append(default_colors[unmapped_count % len(default_colors)])
                unmapped_count += 1
        
        if variable_mappings:
            print(f"  → Colors assigned: {len(variable_mappings)} semantic, {unmapped_count} default")
        else:
            print(f"  → Colors assigned: 0 semantic, {unmapped_count} default (no mappings found for {variable_name})")
        
        return colors
    
    def add_color_mapping(self, variable_name: str, value_name: str, 
                         color_hex: str, description: str = "") -> bool:
        """
        Add a new color mapping for a variable value.
        
        Args:
            variable_name: Variable name (e.g., 'PID1_labeled')
            value_name: Value name (e.g., 'Republican')
            color_hex: Hex color code (e.g., '#d62728')
            description: Optional description
            
        Returns:
            bool: True if mapping was added successfully
        """
        try:
            # Update in-memory mapping
            if variable_name not in self.value_color_mappings:
                self.value_color_mappings[variable_name] = {}
            
            self.value_color_mappings[variable_name][value_name] = color_hex
            
            # Save to CSV
            return self._save_color_mappings()
            
        except Exception as e:
            print(f"Error adding color mapping: {str(e)}")
            return False
    
    def _save_color_mappings(self) -> bool:
        """Save current color mappings to CSV file."""
        try:
            rows = []
            for variable_name, value_mappings in self.value_color_mappings.items():
                for value_name, color_hex in value_mappings.items():
                    rows.append({
                        'variable_name': variable_name,
                        'value_name': value_name,
                        'color_hex': color_hex,
                        'description': f'Color for {value_name}'
                    })
            
            if rows:
                mappings_df = pd.DataFrame(rows)
                mappings_df.to_csv(self.color_mappings_file, index=False)
                print(f"Color mappings saved: {len(rows)} entries")
            
            return True
            
        except Exception as e:
            print(f"Error saving color mappings: {str(e)}")
            return False
    
    def get_available_mappings(self, variable_name: str) -> Dict[str, str]:
        """
        Get all available color mappings for a variable.
        
        Args:
            variable_name: Variable name to look up
            
        Returns:
            Dict mapping value names to color hex codes
        """
        return self.value_color_mappings.get(variable_name, {})
    
    def list_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Get all color mappings for all variables.
        
        Returns:
            Nested dict: {variable_name: {value_name: color_hex}}
        """
        return self.value_color_mappings.copy() 