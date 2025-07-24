"""
Heatmaps module for wave_visualizer package.

Creates matrix visualizations showing transition frequencies and patterns using color intensity.
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Optional, Tuple, Any
from ..data_prep.wave_parser import parse_wave_config, generate_column_names
from ..data_prep.cleaning.row_reduction import RowReductionHandler
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_heatmap_visualization(data: pd.DataFrame = None,
                                variable_name: str = 'HFClust_labeled',
                                wave_config: str = 'w1_to_w2',
                                filter_column: str = None,
                                filter_value: str = None,
                                show_plot: bool = True,
                                **kwargs) -> Tuple[go.Figure, Dict]:
    """
    Create heatmap visualization showing transition percentages.
    
    Args:
        data: DataFrame with processed data
        variable_name: Variable to analyze
        wave_config: Wave configuration (e.g., 'w1_to_w3')
        filter_column: Column to filter by
        filter_value: Value to filter for
        show_plot: Whether to display the plot
        
    Returns:
        Tuple of (Figure object, Statistics dictionary)
    """
    # Load data if not provided
    if data is None:
        from pathlib import Path
        package_dir = Path(__file__).parent.parent.parent
        data_path = package_dir / 'wave_visualizer' / 'settings' / 'processed_data.csv'
        data = pd.read_csv(data_path)
        logger.info(f"Data loaded: {len(data):,} observations")
    
    # Apply filtering if specified
    if filter_column and filter_value:
        logger.info(f"Applying filter: {filter_column} = '{filter_value}'")
        filter_handler = RowReductionHandler()
        settings = {
            "filters": [{
                "column": filter_column,
                "values": [filter_value]
            }]
        }
        original_count = len(data)
        data = filter_handler.apply_filters(data, settings)
        filtered_count = len(data)
        logger.info(f"Filtered to {filtered_count:,} observations ({filtered_count/original_count*100:.1f}%)")
    
    # Parse wave configuration
    source_wave_prefix, target_wave_prefix = parse_wave_config(wave_config)
    source_column, target_column = generate_column_names(
        source_wave_prefix, target_wave_prefix, variable_name
    )
    
    # Create transition matrix
    transition_data = data[[source_column, target_column]].dropna()
    
    # Create count matrix
    count_matrix = pd.crosstab(transition_data[source_column], 
                              transition_data[target_column], 
                              margins=False)
    
    # Convert to percentage matrix (row-wise percentages)
    pct_matrix = count_matrix.div(count_matrix.sum(axis=1), axis=0) * 100
    
    # Get category labels
    categories = sorted(pct_matrix.index.tolist())
    
    # Generate title
    source_wave = source_wave_prefix.rstrip('_').upper()
    target_wave = target_wave_prefix.rstrip('_').upper()
    
    if filter_column and filter_value:
        title = f"Heatmap: {source_wave} TO {target_wave} Transitions<br><sub>{filter_value} Subset</sub>"
    else:
        title = f"Heatmap: {source_wave} TO {target_wave} Transitions"
    
    # Create the heatmap
    fig = go.Figure()
    
    fig.add_trace(
        go.Heatmap(
            z=pct_matrix.values,
            x=categories,
            y=categories,
            colorscale='Reds',
            showscale=True,
            text=pct_matrix.values,
            texttemplate="%{text:.1f}%",
            textfont={"size": 12, "color": "white"},
            hovertemplate='From: %{y}<br>To: %{x}<br>Percentage: %{z:.1f}%<extra></extra>'
        )
    )
    
    # Update layout to match user's preferred style
    fig.update_layout(
        height=600,
        width=800,
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title=f"To Cluster ({target_wave})",
        yaxis_title=f"From Cluster ({source_wave})",
        margin=dict(l=100, r=100, t=100, b=50)
    )
    
    if show_plot:
        fig.show()
    
    # Calculate statistics
    total_transitions = len(transition_data)
    
    # Calculate stability (diagonal values)
    diagonal_stability = {}
    for i, category in enumerate(categories):
        if i < len(pct_matrix) and i < len(pct_matrix.columns):
            stability_pct = pct_matrix.iloc[i, i]
            diagonal_stability[category] = stability_pct
    
    # Overall stability
    overall_stability = np.mean(list(diagonal_stability.values())) if diagonal_stability else 0
    
    statistics = {
        'total_transitions': total_transitions,
        'categories': categories,
        'transition_matrix_pct': pct_matrix.round(1).to_dict(),
        'diagonal_stability': diagonal_stability,
        'overall_stability': overall_stability,
        'wave_transition': wave_config,
        'variable_analyzed': variable_name
    }
    
    return fig, statistics 