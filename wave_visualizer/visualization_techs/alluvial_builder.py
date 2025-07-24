"""
Alluvial Visualization Builder

Refactored builder pattern implementation for creating alluvial visualizations.
Breaks down the large create_alluvial_visualization function into manageable,
focused methods with clear responsibilities.
"""

import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from ..interfaces import VisualizationBuilder
from ..data_prep.customization import VisualizationCustomizer
from ..data_prep.wave_parser import parse_wave_config
from ..utils.logger import get_logger, log_step, log_success
from ..exceptions import DataLoadingError, VisualizationError
from ..validators import validate_visualization_inputs

logger = get_logger(__name__)


class AlluvialVisualizationBuilder(VisualizationBuilder):
    """Builder for creating alluvial visualizations with step-by-step configuration."""
    
    def __init__(self):
        """Initialize the builder with default values."""
        self._data: Optional[pd.DataFrame] = None
        self._variable_name: str = 'HFClust_labeled'
        self._wave_config: str = 'w1_to_w2'
        self._filter_column: Optional[str] = None
        self._filter_value: Optional[str] = None
        self._custom_title: Optional[str] = None
        self._customizer: Optional[VisualizationCustomizer] = None
        
        # Internal state
        self._source_wave_prefix: Optional[str] = None
        self._target_wave_prefix: Optional[str] = None
        self._config: Optional[Dict[str, Any]] = None
        
        logger.debug("AlluvialVisualizationBuilder initialized")
    
    def set_data(self, data: Optional[pd.DataFrame] = None) -> 'AlluvialVisualizationBuilder':
        """
        Set the data for visualization.
        
        Args:
            data: DataFrame to visualize (if None, loads automatically)
            
        Returns:
            Self for method chaining
        """
        if data is None:
            self._data = self._load_default_data()
        else:
            self._data = data
        
        logger.debug(f"Data set: {len(self._data)} rows, {len(self._data.columns)} columns")
        return self
    
    def set_variable(self, variable_name: str) -> 'AlluvialVisualizationBuilder':
        """
        Set the variable to visualize.
        
        Args:
            variable_name: Name of the variable to analyze
            
        Returns:
            Self for method chaining
        """
        self._variable_name = variable_name
        logger.debug(f"Variable set: {variable_name}")
        return self
    
    def set_wave_config(self, wave_config: str) -> 'AlluvialVisualizationBuilder':
        """
        Set the wave configuration.
        
        Args:
            wave_config: Wave transition configuration (e.g., 'w1_to_w2')
            
        Returns:
            Self for method chaining
        """
        self._wave_config = wave_config
        logger.debug(f"Wave config set: {wave_config}")
        return self
    
    def apply_filter(self, column: str, value: str) -> 'AlluvialVisualizationBuilder':
        """
        Apply a filter to the data.
        
        Args:
            column: Column to filter by
            value: Value to filter for
            
        Returns:
            Self for method chaining
        """
        self._filter_column = column
        self._filter_value = value
        logger.debug(f"Filter applied: {column}={value}")
        return self
    
    def set_custom_title(self, title: str) -> 'AlluvialVisualizationBuilder':
        """
        Set a custom title for the visualization.
        
        Args:
            title: Custom title text
            
        Returns:
            Self for method chaining
        """
        self._custom_title = title
        logger.debug(f"Custom title set: {title}")
        return self
    
    def build(self) -> Tuple[go.Figure, Dict[str, Any]]:
        """
        Build and return the visualization.
        
        Returns:
            Tuple of (Figure object, Summary statistics dictionary)
            
        Raises:
            VisualizationError: If build process fails
        """
        try:
            log_step(logger, 1, "Building Alluvial Visualization")
            
            # Step 1: Prepare data
            self._prepare_data()
            
            # Step 2: Configure visualization
            self._configure_visualization()
            
            # Step 3: Process data for visualization
            transition_data = self._process_transition_data()
            
            # Step 4: Create the plot
            figure = self._create_plotly_figure(transition_data)
            
            # Step 5: Calculate statistics
            statistics = self._calculate_statistics(transition_data)
            
            log_success(logger, "Alluvial visualization built successfully")
            return figure, statistics
            
        except Exception as e:
            logger.error(f"Failed to build alluvial visualization: {e}")
            raise VisualizationError(f"Visualization build failed: {str(e)}")
    
    def _load_default_data(self) -> pd.DataFrame:
        """Load default processed data."""
        logger.info("Loading processed data automatically...")
        
        # Get the path relative to this package, not current working directory
        from pathlib import Path
        package_dir = Path(__file__).parent.parent.parent
        data_path = package_dir / 'wave_visualizer' / 'settings' / 'processed_data.csv'
        
        try:
            data = pd.read_csv(data_path)
            logger.info(f"Data loaded: {len(data):,} observations")
            return data
        except FileNotFoundError:
            raise DataLoadingError(
                "Processed data file not found. Please run the data cleaning pipeline first.",
                f"Expected file: {data_path}"
            )
        except Exception as e:
            raise DataLoadingError(f"Failed to load processed data: {str(e)}")
    
    def _prepare_data(self) -> None:
        """Prepare and validate data for visualization."""
        if self._data is None:
            self._data = self._load_default_data()
        
        # Comprehensive input validation
        validate_visualization_inputs(
            self._data, self._variable_name, self._wave_config, 
            self._filter_column, self._filter_value
        )
        
        # Apply filtering if specified
        if self._filter_column and self._filter_value:
            self._apply_data_filter()
        
        logger.debug("Data preparation completed")
    
    def _apply_data_filter(self) -> None:
        """Apply row filtering to the data."""
        logger.info(f"Applying filter: {self._filter_column} = '{self._filter_value}'")
        
        from ..data_prep.cleaning.row_reduction import RowReductionHandler
        filter_handler = RowReductionHandler()
        
        # Create settings dict in the expected format
        settings = {
            "filters": [{
                "column": self._filter_column,
                "values": [self._filter_value]
            }]
        }
        
        original_count = len(self._data)
        self._data = filter_handler.apply_filters(self._data, settings)
        filtered_count = len(self._data)
        
        logger.info(f"Filtered to {filtered_count:,} observations ({filtered_count/original_count*100:.1f}%)")
    
    def _configure_visualization(self) -> None:
        """Configure visualization settings and wave parsing."""
        # Parse wave configuration
        try:
            self._source_wave_prefix, self._target_wave_prefix = parse_wave_config(self._wave_config)
        except ValueError as e:
            logger.warning(f"Wave configuration error: {str(e)}")
            raise VisualizationError(f"Invalid wave configuration: {self._wave_config}")
        
        # Generate title if not provided
        if self._custom_title is None:
            self._custom_title = self._generate_automatic_title()
        
        # Set up customizer and get configuration
        if self._customizer is None:
            self._customizer = VisualizationCustomizer()
        
        self._config = self._customizer.configure_visualization(
            variable_name=self._variable_name,
            wave_config=self._wave_config,
            custom_title=self._custom_title
        )
        
        logger.debug("Visualization configuration completed")
    
    def _generate_automatic_title(self) -> str:
        """Generate automatic title based on wave configuration and filtering."""
        # Extract clean wave names for display
        source_wave = self._source_wave_prefix.rstrip('_')
        target_wave = self._target_wave_prefix.rstrip('_')
        
        main_title = f"{source_wave} -> {target_wave} Transitions"
        
        # Add subtitle for filtering
        if self._filter_column and self._filter_value:
            return f"{main_title}<br><sub>({self._filter_value} Subset)</sub>"
        else:
            return main_title
    
    def _process_transition_data(self) -> pd.DataFrame:
        """Process data to create transition counts."""
        from ..data_prep.wave_parser import generate_column_names
        
        # Generate column names for source and target waves
        source_column, target_column = generate_column_names(
            self._source_wave_prefix, self._target_wave_prefix, self._variable_name
        )
        
        # Create transition data
        transition_data = self._data[[source_column, target_column]].dropna()
        
        # Group by transitions and count
        transition_counts = (transition_data
                           .groupby([source_column, target_column])
                           .size()
                           .reset_index(name='count'))
        
        # Rename columns for clarity
        transition_counts.columns = ['source', 'target', 'count']
        
        # Calculate percentages
        total_transitions = transition_counts['count'].sum()
        transition_counts['percentage'] = (transition_counts['count'] / total_transitions) * 100
        
        # Sort by count (descending)
        transition_counts = transition_counts.sort_values('count', ascending=False)
        
        logger.debug(f"Processed {len(transition_counts)} unique transition patterns")
        return transition_counts
    
    def _create_plotly_figure(self, transition_data: pd.DataFrame) -> go.Figure:
        """Create the Plotly Sankey diagram figure."""
        # Get unique categories for each wave separately
        source_categories = sorted(transition_data['source'].unique())
        target_categories = sorted(transition_data['target'].unique())
        
        # Create separate node lists for proper alluvial display
        # Left side nodes (source wave)
        source_wave_name = self._source_wave_prefix.rstrip('_').upper()
        target_wave_name = self._target_wave_prefix.rstrip('_').upper()
        
        source_nodes = [f"{cat} ({source_wave_name})" for cat in source_categories]
        target_nodes = [f"{cat} ({target_wave_name})" for cat in target_categories]
        
        # Combine all nodes: source nodes first, then target nodes
        all_node_labels = source_nodes + target_nodes
        
        # Create mappings for indices
        source_to_index = {cat: i for i, cat in enumerate(source_categories)}
        target_to_index = {cat: i + len(source_categories) for i, cat in enumerate(target_categories)}
        
        # Prepare Sankey data with proper indexing
        source_indices = [source_to_index[source] for source in transition_data['source']]
        target_indices = [target_to_index[target] for target in transition_data['target']]
        values = transition_data['count'].tolist()
        
        # Get colors for unique categories (without wave labels)
        unique_categories = sorted(set(source_categories) | set(target_categories))
        base_colors = self._customizer.get_semantic_colors(self._variable_name, unique_categories)
        
        # Create color mappings
        color_map = {cat: color for cat, color in zip(unique_categories, base_colors)}
        
        # Apply colors to nodes: source colors + target colors
        node_colors = []
        for cat in source_categories:
            node_colors.append(color_map[cat])
        for cat in target_categories:
            node_colors.append(color_map[cat])
        
        # Create link colors (semi-transparent source colors)
        link_colors = []
        for source in transition_data['source']:
            base_color = color_map[source]
            if base_color.startswith('#'):
                # Convert hex to rgba with transparency
                rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
                link_colors.append(f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.6)")
            else:
                link_colors.append(base_color)
        
        # Create hover text
        hover_text = [
            f"{row['source']} → {row['target']}<br>"
            f"Count: {row['count']:,}<br>"
            f"Percentage: {row['percentage']:.1f}%"
            for _, row in transition_data.iterrows()
        ]
        
        # Create node positions for proper left-right layout
        num_source = len(source_categories)
        num_target = len(target_categories)
        
        # Position nodes: source on left (x=0.01), target on right (x=0.99)
        node_x = [0.01] * num_source + [0.99] * num_target
        node_y = []
        
        # Distribute source nodes vertically on left
        for i in range(num_source):
            node_y.append((i + 0.5) / num_source)
        
        # Distribute target nodes vertically on right  
        for i in range(num_target):
            node_y.append((i + 0.5) / num_target)
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            arrangement="snap",
            node=dict(
                pad=self._config['plot_params']['node_padding'],
                thickness=self._config['plot_params']['node_thickness'],
                line=dict(color="black", width=0.5),
                label=all_node_labels,
                color=node_colors,
                x=node_x,
                y=node_y
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=link_colors,
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_text
            )
        )])
        
        # Update layout
        fig.update_layout(
            title={
                'text': self._config['title'],
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': self._config['plot_params']['title_size']}
            },
            font=dict(size=self._config['plot_params']['label_size']),
            width=self._config['plot_params']['figure_width'],
            height=self._config['plot_params']['figure_height'],
            margin=dict(
                l=self._config['plot_params']['margin_left'],
                r=self._config['plot_params']['margin_right'],
                t=self._config['plot_params']['margin_top'],
                b=self._config['plot_params']['margin_bottom']
            )
        )

        return fig
    
    def _calculate_statistics(self, transition_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for the visualization."""
        total_transitions = transition_data['count'].sum()
        
        # Calculate stability (transitions where source == target)
        stable_transitions = transition_data[transition_data['source'] == transition_data['target']]
        stable_count = stable_transitions['count'].sum()
        stability_rate = (stable_count / total_transitions) * 100 if total_transitions > 0 else 0
        
        # Create top patterns list
        top_patterns = []
        for _, row in transition_data.head(10).iterrows():
            top_patterns.append({
                'source': row['source'],
                'target': row['target'],
                'count': row['count'],
                'percentage': row['percentage'],
                'stable': row['source'] == row['target']
            })
        
        return {
            'total_transitions': int(total_transitions),
            'unique_patterns': len(transition_data),
            'stability_rate': float(stability_rate),
            'top_patterns': top_patterns,
            'variable_analyzed': self._variable_name,
            'wave_transition': self._wave_config
        } 