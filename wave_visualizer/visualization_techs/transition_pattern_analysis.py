"""
Transition Pattern Analysis module for wave_visualizer package.

Creates bar chart visualizations showing ranked transition patterns with stability analysis.
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, Optional, Tuple, Any
from ..data_prep.wave_parser import parse_wave_config, generate_column_names
from ..data_prep.cleaning.row_reduction import RowReductionHandler
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_pattern_analysis_visualization(data: pd.DataFrame = None,
                                         variable_name: str = 'HFClust_labeled', 
                                         wave_config: str = 'w1_to_w2',
                                         filter_column: str = None,
                                         filter_value: str = None,
                                         show_plot: bool = True,
                                         **kwargs) -> Tuple[go.Figure, Dict]:
    """
    Create pattern analysis visualization showing ranked transition patterns.
    
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
    
    # Create transition patterns
    transition_data = data[[source_column, target_column]].dropna()
    
    # Create transition patterns with meaningful names
    patterns = []
    for _, row in transition_data.iterrows():
        source_name = row[source_column]
        target_name = row[target_column]
        pattern = f"{source_name} -> {target_name}"
        patterns.append(pattern)
    
    # Count patterns and create summary
    pattern_counts = pd.Series(patterns).value_counts()
    pattern_df = pd.DataFrame({
        'Pattern': pattern_counts.index,
        'Count': pattern_counts.values,
        'Percentage': (pattern_counts.values / len(transition_data)) * 100
    })
    
    # Add pattern type classification (stable vs changed)
    pattern_df['Type'] = pattern_df['Pattern'].apply(
        lambda x: 'Stable' if x.split(' -> ')[0] == x.split(' -> ')[1] else 'Changed'
    )
    
    # Get top 15 patterns for visualization
    top_patterns = pattern_df.head(15)
    
    # Generate title
    source_wave = source_wave_prefix.rstrip('_').upper()
    target_wave = target_wave_prefix.rstrip('_').upper()
    
    if filter_column and filter_value:
        title = f"Transition Patterns: {source_wave} TO {target_wave}<br><sub>{filter_value} Subset</sub>"
    else:
        title = f"Transition Patterns: {source_wave} TO {target_wave}"
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Color mapping: green for stable, orange for changes
    colors = ['#2E8B57' if ptype == 'Stable' else '#FF8C00' for ptype in top_patterns['Type']]
    
    fig.add_trace(go.Bar(
        x=top_patterns['Count'],
        y=top_patterns['Pattern'],
        orientation='h',
        marker_color=colors,
        text=[f'{count} ({pct:.1f}%)' for count, pct in zip(top_patterns['Count'], top_patterns['Percentage'])],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<br>Percentage: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title="Number of Respondents",
        yaxis_title="Transition Pattern", 
        height=600,
        width=1000,
        margin=dict(l=200, r=100, t=100, b=50),
        font=dict(size=12),
        showlegend=False
    )
    
    if show_plot:
        fig.show()
    
    # Calculate statistics
    total_transitions = len(transition_data)
    unique_patterns = len(pattern_df)
    
    stable_count = pattern_df[pattern_df['Type'] == 'Stable']['Count'].sum()
    changed_count = pattern_df[pattern_df['Type'] == 'Changed']['Count'].sum()
    
    # Top 5 patterns for summary
    top_5_patterns = []
    for _, row in top_patterns.head(5).iterrows():
        top_5_patterns.append({
            'pattern': row['Pattern'],
            'count': row['Count'],
            'percentage': row['Percentage'],
            'type': row['Type']
        })
    
    statistics = {
        'total_transitions': total_transitions,
        'unique_patterns': unique_patterns,
        'stable_count': stable_count,
        'stable_percentage': (stable_count / total_transitions) * 100,
        'changed_count': changed_count,
        'changed_percentage': (changed_count / total_transitions) * 100,
        'top_5_patterns': top_5_patterns,
        'wave_transition': wave_config,
        'variable_analyzed': variable_name
    }
    
    return fig, statistics 