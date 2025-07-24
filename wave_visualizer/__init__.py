"""
Wave Visualizer Package

A comprehensive Python package for visualizing longitudinal survey data transitions 
across multiple waves, with robust data preprocessing and customizable visualization options.

This package provides professional-grade tools for analyzing political and social science
survey data, with a focus on tracking changes across multiple survey waves. It includes
sophisticated data cleaning pipelines, semantic color mapping systems, and interactive
visualization generation with automatic export capabilities.

Key Features:
    - Automatic data cleaning and preprocessing pipelines
    - Dynamic wave configuration supporting unlimited survey waves
    - Semantic color mapping for consistent variable representation
    - Interactive alluvial plots (Sankey diagrams) for transition visualization
    - Professional export system (HTML + high-resolution images)
    - Comprehensive logging and error handling
    - Type-safe APIs with full IDE support

Quick Start:
    >>> import wave_visualizer
    >>> 
    >>> # Create a visualization with one line
    >>> fig, stats = wave_visualizer.create_alluvial_visualization(
    ...     variable_name='HFClust_labeled',
    ...     wave_config='w1_to_w3',
    ...     filter_column='PID1_labeled',
    ...     filter_value='Republican'
    ... )
    >>> 
    >>> # Export to local exports folder
    >>> wave_visualizer.export_figure(fig, 'republican_analysis')

Author: michaelnapoli404
Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "michaelnapoli404"

# Import main components
from .data_prep.customization import VisualizationCustomizer

# Import data cleaning modules
from .data_prep.cleaning.metadata_handler import MetadataHandler
from .data_prep.cleaning.values_to_labels import ValuesToLabelsConverter
from .data_prep.cleaning.value_missing_and_dropping_handler import ValueMissingAndDroppingHandler
from .data_prep.cleaning.value_merging_handler import ValueMergingHandler
from .data_prep.cleaning.row_reduction import RowReductionHandler

from .data_prep.cleaning.cleaning import DataCleaningPipeline
from .data_prep.color_mapping import ColorMappingHandler
from .data_prep.export_handler import export_figure, create_exports_folder
from .utils.logger import configure_package_logging, get_logger
from .validators import validate_visualization_inputs

# Import visualization components  
from .visualization_techs import (
    create_alluvial_visualization,
    create_heatmap_visualization,
    create_pattern_analysis_visualization,
    AlluvialVisualizationBuilder
)

# Import and expose export functions  
from .data_prep.export_handler import export_figure

# Expose main functions at package level
__all__ = [
    # Configuration
    'VisualizationCustomizer',
    
    # Data Cleaning
    'MetadataHandler',
    'ValuesToLabelsConverter',
    'ValueMissingAndDroppingHandler',
    'ValueMergingHandler',
    'RowReductionHandler',
    
    # Visualization Components
    'AlluvialVisualizationBuilder',
    
    # Main Functions
    'create_alluvial_visualization',
    'create_heatmap_visualization', 
    'create_pattern_analysis_visualization',
    'export_figure',
    
    # Utilities
    'logger',
    'CleaningPipeline',
    'ExportHandler',
    
    # Validation
    'validate_visualization_inputs'
] 

def add_color_mapping(variable_name: str, value_name: str, color_hex: str, description: str = ""):
    """
    Add a semantic color mapping for a specific variable value.
    
    Args:
        variable_name: Variable name (e.g., 'PID1_labeled')
        value_name: Value name (e.g., 'Republican') 
        color_hex: Hex color code (e.g., '#d62728')
        description: Optional description
        
    Example:
        wave_visualizer.add_color_mapping('PID1_labeled', 'Republican', '#d62728', 'Traditional red for Republicans')
        wave_visualizer.add_color_mapping('PID1_labeled', 'Democrat', '#1f77b4', 'Traditional blue for Democrats')
    """
    handler = ColorMappingHandler()
    success = handler.add_color_mapping(variable_name, value_name, color_hex, description)
    if success:
        print(f"Color mapping added: {variable_name}.{value_name} → {color_hex}")
    else:
        print(f"Failed to add color mapping for {variable_name}.{value_name}")
    return success

def list_color_mappings(variable_name: str = None):
    """
    List all color mappings, optionally filtered by variable.
    
    Args:
        variable_name: Optional variable name to filter by
        
    Returns:
        Dict of color mappings
    """
    handler = ColorMappingHandler()
    
    if variable_name:
        mappings = handler.get_available_mappings(variable_name)
        print(f"\nColor mappings for {variable_name}:")
        print("-" * 40)
        for value, color in mappings.items():
            print(f"  {value:20s} → {color}")
    else:
        all_mappings = handler.list_all_mappings()
        print("\nAll color mappings:")
        print("-" * 40)
        for var, mappings in all_mappings.items():
            print(f"\n{var}:")
            for value, color in mappings.items():
                print(f"  {value:20s} → {color}")
    
    return handler.get_available_mappings(variable_name) if variable_name else handler.list_all_mappings() 

def add_wave_definition(wave_name: str, column_prefix: str, description: str = ""):
    """
    Add a new wave definition to enable analysis of additional waves.
    
    Args:
        wave_name: Wave name (e.g., 'Wave4', 'Wave5')
        column_prefix: Column prefix used in dataset (e.g., 'W4_', 'W5_')
        description: Optional description of the wave
        
    Example:
        # When you get W4 data, just add it to the system:
        wave_visualizer.add_wave_definition('Wave4', 'W4_', 'Fourth wave data collection')
        
        # Now you can use w1_to_w4, w2_to_w4, w3_to_w4, etc.
        wave_visualizer.create_alluvial_visualization(wave_config='w1_to_w4', ...)
    """
    from .data_prep.wave_parser import add_wave_definition as _add_wave_def
    return _add_wave_def(wave_name, column_prefix, description)

def get_available_waves():
    """
    Get list of currently available wave numbers.
    
    Returns:
        List of wave numbers that can be used in wave configurations
        
    Example:
        waves = wave_visualizer.get_available_waves()
        print(f"Available waves: {waves}")  # e.g., [1, 2, 3, 4]
    """
    from .data_prep.wave_parser import get_available_waves as _get_waves
    return _get_waves()

def list_wave_definitions():
    """
    Display all currently defined waves and their column prefixes.
    """
    from .data_prep.wave_parser import _get_wave_parser
    
    parser = _get_wave_parser()
    
    print("\nWave Definitions:")
    print("-" * 40)
    for wave_num in sorted(parser.wave_numbers.keys()):
        wave_name, column_prefix = parser.wave_numbers[wave_num]
        print(f"  Wave {wave_num}: {column_prefix:<4} ({wave_name})")
    
    print(f"\nTotal waves: {len(parser.wave_numbers)}")
    
    # Show example usage
    if len(parser.wave_numbers) >= 2:
        waves = sorted(parser.wave_numbers.keys())
        print(f"\nExample usage:")
        print(f"  wave_visualizer.create_alluvial_visualization(wave_config='w{waves[0]}_to_w{waves[1]}', ...)")
        if len(waves) >= 3:
            print(f"  wave_visualizer.create_alluvial_visualization(wave_config='w{waves[0]}_to_w{waves[-1]}', ...)")
    
    return parser.wave_definitions.copy() 