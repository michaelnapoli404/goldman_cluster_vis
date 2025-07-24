"""
Customization module for wave_visualizer package.

This module handles visualization configuration settings including:
- Color schemes and styling parameters
- Wave transition selections  
- Plot layout and formatting options
- Integration with cleaning pipeline validation

Dependencies: Requires cleaning pipeline to be completed first.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from .color_mapping import ColorMappingHandler
from .wave_parser import parse_wave_config, generate_column_names


class VisualizationCustomizer:
    """
    Manages visualization customization settings for wave_visualizer package.
    
    Validates that cleaning pipeline is complete before allowing configuration.
    Saves all settings to persistent CSV files in visualization_settings folder.
    """
    
    def __init__(self, package_root: Optional[str] = None):
        """
        Initialize the VisualizationCustomizer.
        
        Args:
            package_root: Root directory of the package (optional)
        """
        # Use settings folder within package
        from wave_visualizer.settings import VISUALIZATION_DIR, CLEANING_DIR
        self.viz_settings_dir = VISUALIZATION_DIR
        self.cleaning_settings_dir = CLEANING_DIR
        
        # Ensure directories exist
        self.viz_settings_dir.mkdir(exist_ok=True)
        self.cleaning_settings_dir.mkdir(exist_ok=True)
        
        # Initialize color mapping handler
        self.color_handler = ColorMappingHandler()
        
        # Load configuration components
        self._validate_cleaning_pipeline()
        
        print("Cleaning pipeline validation passed - all required files found")
        
    def _validate_cleaning_pipeline(self):
        """Validate that cleaning pipeline has been completed."""
        required_files = [
            self.cleaning_settings_dir / "missing_value_settings.csv",
            self.cleaning_settings_dir / "value_merging_settings.csv"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        
        if missing_files:
            missing_names = [f.name for f in missing_files]
            raise RuntimeError(
                f"Cleaning pipeline not complete! Missing files: {missing_names}\n"
                f"Please run the cleaning.py module first to complete data preprocessing."
            )
        
    def configure_visualization(self, 
                              variable_name: str,
                              wave_config: str = 'w1_to_w2',
                              filter_column: Optional[str] = None,
                              filter_value: Optional[str] = None,
                              custom_title: Optional[str] = None,
                              top_n: int = 15) -> Dict:
        """
        Configure visualization settings for a specific analysis.
        
        Args:
            variable_name: Column name to analyze (e.g., 'HFClust_labeled')
            wave_config: Wave transition configuration (e.g., 'w1_to_w2', 'w2_to_w3', 'w1_to_w5', 'w4_to_w7', 'all_waves')
            filter_column: Optional column name for filtering data
            filter_value: Optional value to filter by
            custom_title: Optional custom title for plots
            top_n: Number of top patterns to show in pattern analysis
            
        Returns:
            Dictionary with complete visualization configuration
        """
        # Parse wave configuration dynamically
        try:
            source_wave_prefix, target_wave_prefix = parse_wave_config(wave_config)
            # Extract clean wave names for display (remove trailing underscore)
            source_wave = source_wave_prefix.rstrip('_')
            target_wave = target_wave_prefix.rstrip('_')
        except ValueError as e:
            print(f"Warning: {str(e)}")
            print("Falling back to default: W1 → W2")
            source_wave_prefix, target_wave_prefix = 'W1_', 'W2_'
            source_wave, target_wave = 'W1', 'W2'
            
        # Build basic configuration
        config = {
            'variable_name': variable_name,
            'source_wave': source_wave,
            'target_wave': target_wave,
            'wave_description': f"Transition from {source_wave} to {target_wave}",
            'title': custom_title or f"{source_wave} → {target_wave} Transitions",
            'filter_column': filter_column,
            'filter_value': filter_value,
            'top_n_patterns': top_n,
            'plot_params': {
                'figure_width': 1000,
                'figure_height': 600,
                'title_size': 18,
                'label_size': 12,
                'legend_size': 10,
                'dpi': 300,
                'export_format': 'html',
                'show_percentages': True,
                'show_counts': True,
                'interactive': True,
                'top_n_patterns': 15,
                # Sankey diagram specific parameters
                'node_padding': 15,
                'node_thickness': 20,
                'margin_left': 50,
                'margin_right': 50,
                'margin_top': 80,
                'margin_bottom': 50
            }
        }
        
        # Add source and target column names using dynamic generation
        source_column, target_column = generate_column_names(
            source_wave_prefix=source_wave_prefix,
            target_wave_prefix=target_wave_prefix,
            variable_name=variable_name
        )
        config['source_column'] = source_column
        config['target_column'] = target_column
        
        print(f"Configuration created for {variable_name} ({wave_config})")
        if filter_column and filter_value:
            print(f"  → Filter: {filter_column} = '{filter_value}'")
            
        return config 
        
    def get_semantic_colors(self, variable_name: str, values: List[str]) -> List[str]:
        """
        Get semantic colors for specific variable values.
        
        Args:
            variable_name: Name of the variable (e.g., 'HFClust_labeled')
            values: List of values to get colors for
            
        Returns:
            List of color hex codes in same order as values
        """
        return self.color_handler.get_colors_for_variable(
            variable_name=variable_name,
            values=values
        )