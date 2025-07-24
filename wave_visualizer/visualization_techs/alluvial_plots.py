"""
Alluvial Plots module for wave_visualizer package.

Creates flowing stream/ribbon visualizations showing transitions between categories 
across waves. Optimized for longitudinal survey data with minimal cleaning requirements.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any

from ..data_prep.customization import VisualizationCustomizer
from ..data_prep.wave_parser import parse_wave_config
from ..utils.logger import get_logger
from ..exceptions import (
    DataLoadingError, ColumnNotFoundError, WaveConfigurationError, 
    VisualizationError, validate_column_exists, handle_exception
)
from ..validators import validate_visualization_inputs, sanitize_filename

logger = get_logger(__name__)


class AlluvialPlotGenerator:
    """
    Generates alluvial (Sankey-style) flow diagrams for wave transition analysis.
    """
    
    def __init__(self, data: pd.DataFrame, customizer: Optional[VisualizationCustomizer] = None):
        """
        Initialize the alluvial plot generator.
        
        Args:
            data: Cleaned dataset with wave columns
            customizer: VisualizationCustomizer instance (optional)
        """
        self.data = data
        self.customizer = customizer or VisualizationCustomizer()
        
        logger.info(f"AlluvialPlotGenerator initialized with {len(data):,} observations")


def create_alluvial_visualization(data: Optional[pd.DataFrame] = None,
                                 variable_name: str = 'HFClust_labeled',
                                 wave_config: str = 'w1_to_w2',
                                 filter_column: Optional[str] = None,
                                 filter_value: Optional[str] = None,
                                 custom_title: Optional[str] = None,
                                 show_plot: bool = True,
                                 **kwargs) -> Tuple[go.Figure, Dict[str, Any]]:
    """
    Convenience function to create alluvial visualization with automatic configuration.
    
    Args:
        data: Pre-cleaned dataset (optional - loads automatically if not provided)
        variable_name: Variable to analyze (e.g., 'HFClust_labeled')
        wave_config: Wave transition (e.g., 'w1_to_w2', 'w2_to_w3', 'w1_to_w5', 'w4_to_w7', 'all_waves')
        filter_column: Column to filter by (e.g., 'PID1_labeled')
        filter_value: Value to filter to (e.g., 'Republican')
        custom_title: Optional custom title
        show_plot: Whether to display the plot
        **kwargs: Additional configuration parameters
        
    Returns:
        Tuple of (Figure object, Summary statistics dictionary)
        
    Example:
        # Create visualization and export it
        fig, stats = wave_visualizer.create_alluvial_visualization(
            variable_name='HFClust_labeled',
            wave_config='w1_to_w3',
            filter_column='PID1_labeled',
            filter_value='Republican'
        )
        wave_visualizer.export_figure(fig, 'republican_analysis')
    """
    from .alluvial_builder import AlluvialVisualizationBuilder
    
    # Use builder pattern for clean, modular construction
    builder = AlluvialVisualizationBuilder()
    
    # Configure the builder
    builder.set_data(data)
    builder.set_variable(variable_name)
    builder.set_wave_config(wave_config)
    
    if filter_column and filter_value:
        builder.apply_filter(filter_column, filter_value)
    
    if custom_title:
        builder.set_custom_title(custom_title)
    
    # Build and return the visualization
    return builder.build()
 