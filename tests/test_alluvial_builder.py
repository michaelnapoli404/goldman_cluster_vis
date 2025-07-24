"""
Unit tests for wave_visualizer.visualization_techs.alluvial_builder module.
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock, patch
from wave_visualizer.visualization_techs.alluvial_builder import AlluvialVisualizationBuilder
from wave_visualizer.exceptions import DataLoadingError, VisualizationError


class TestAlluvialVisualizationBuilder:
    """Test AlluvialVisualizationBuilder class."""
    
    def test_builder_initialization(self):
        """Test builder initialization with default values."""
        builder = AlluvialVisualizationBuilder()
        assert builder._data is None
        assert builder._variable_name == 'HFClust_labeled'
        assert builder._wave_config == 'w1_to_w2'
        assert builder._filter_column is None
        assert builder._filter_value is None
    
    def test_set_data_with_dataframe(self, sample_data):
        """Test setting data with a DataFrame."""
        builder = AlluvialVisualizationBuilder()
        result = builder.set_data(sample_data)
        
        assert result is builder  # Method chaining
        assert builder._data is sample_data
    
    def test_set_data_none_loads_default(self):
        """Test setting data to None loads default data."""
        builder = AlluvialVisualizationBuilder()
        
        with patch.object(builder, '_load_default_data') as mock_load:
            mock_load.return_value = Mock(spec=pd.DataFrame)
            result = builder.set_data(None)
            
            assert result is builder
            mock_load.assert_called_once()
    
    def test_set_variable(self):
        """Test setting variable name."""
        builder = AlluvialVisualizationBuilder()
        result = builder.set_variable('test_variable')
        
        assert result is builder
        assert builder._variable_name == 'test_variable'
    
    def test_set_wave_config(self):
        """Test setting wave configuration."""
        builder = AlluvialVisualizationBuilder()
        result = builder.set_wave_config('w2_to_w3')
        
        assert result is builder
        assert builder._wave_config == 'w2_to_w3'
    
    def test_apply_filter(self):
        """Test applying filter."""
        builder = AlluvialVisualizationBuilder()
        result = builder.apply_filter('PID1_labeled', 'Republican')
        
        assert result is builder
        assert builder._filter_column == 'PID1_labeled'
        assert builder._filter_value == 'Republican'
    
    def test_set_custom_title(self):
        """Test setting custom title."""
        builder = AlluvialVisualizationBuilder()
        result = builder.set_custom_title('Custom Test Title')
        
        assert result is builder
        assert builder._custom_title == 'Custom Test Title'
    
    def test_method_chaining(self, sample_data):
        """Test that methods can be chained together."""
        builder = AlluvialVisualizationBuilder()
        
        result = (builder
                 .set_data(sample_data)
                 .set_variable('HFClust_labeled')
                 .set_wave_config('w1_to_w2')
                 .apply_filter('PID1_labeled', 'Republican')
                 .set_custom_title('Test Title'))
        
        assert result is builder
        assert builder._data is sample_data
        assert builder._variable_name == 'HFClust_labeled'
        assert builder._wave_config == 'w1_to_w2'
        assert builder._filter_column == 'PID1_labeled'
        assert builder._filter_value == 'Republican'
        assert builder._custom_title == 'Test Title'
    
    @patch('wave_visualizer.visualization_techs.alluvial_builder.pd.read_csv')
    def test_load_default_data_success(self, mock_read_csv, sample_data):
        """Test successful loading of default data."""
        mock_read_csv.return_value = sample_data
        builder = AlluvialVisualizationBuilder()
        
        result = builder._load_default_data()
        
        assert result is sample_data
        mock_read_csv.assert_called_once_with('./wave_visualizer/settings/processed_data.csv')
    
    @patch('wave_visualizer.visualization_techs.alluvial_builder.pd.read_csv')
    def test_load_default_data_file_not_found(self, mock_read_csv):
        """Test loading default data when file not found."""
        mock_read_csv.side_effect = FileNotFoundError()
        builder = AlluvialVisualizationBuilder()
        
        with pytest.raises(DataLoadingError, match="Processed data file not found"):
            builder._load_default_data()
    
    def test_generate_automatic_title_no_filter(self):
        """Test automatic title generation without filter."""
        builder = AlluvialVisualizationBuilder()
        builder._source_wave_prefix = 'W1_'
        builder._target_wave_prefix = 'W2_'
        
        title = builder._generate_automatic_title()
        assert title == "W1 → W2 Transitions"
    
    def test_generate_automatic_title_with_filter(self):
        """Test automatic title generation with filter."""
        builder = AlluvialVisualizationBuilder()
        builder._source_wave_prefix = 'W1_'
        builder._target_wave_prefix = 'W3_'
        builder._filter_column = 'PID1_labeled'
        builder._filter_value = 'Republican'
        
        title = builder._generate_automatic_title()
        assert title == "W1 → W3 Transitions<br><sub>(Republican Subset)</sub>"
    
    @patch('wave_visualizer.visualization_techs.alluvial_builder.validate_visualization_inputs')
    def test_prepare_data_with_validation(self, mock_validate, sample_data):
        """Test data preparation with validation."""
        builder = AlluvialVisualizationBuilder()
        builder._data = sample_data
        builder._variable_name = 'HFClust_labeled'
        builder._wave_config = 'w1_to_w2'
        
        builder._prepare_data()
        
        mock_validate.assert_called_once_with(
            sample_data, 'HFClust_labeled', 'w1_to_w2', None, None
        )
    
    def test_process_transition_data(self, sample_data):
        """Test processing transition data."""
        builder = AlluvialVisualizationBuilder()
        builder._data = sample_data
        builder._variable_name = 'HFClust_labeled'
        builder._source_wave_prefix = 'W1_'
        builder._target_wave_prefix = 'W2_'
        
        with patch('wave_visualizer.visualization_techs.alluvial_builder.generate_column_names') as mock_gen:
            mock_gen.return_value = ('W1_HFClust_labeled', 'W2_HFClust_labeled')
            
            result = builder._process_transition_data()
            
            assert isinstance(result, pd.DataFrame)
            assert 'source' in result.columns
            assert 'target' in result.columns
            assert 'count' in result.columns
            assert 'percentage' in result.columns
            assert len(result) > 0
    
    def test_calculate_statistics(self, sample_transition_data):
        """Test statistics calculation."""
        builder = AlluvialVisualizationBuilder()
        builder._variable_name = 'HFClust_labeled'
        builder._wave_config = 'w1_to_w2'
        
        stats = builder._calculate_statistics(sample_transition_data)
        
        assert isinstance(stats, dict)
        assert 'total_transitions' in stats
        assert 'unique_patterns' in stats
        assert 'stability_rate' in stats
        assert 'top_patterns' in stats
        assert 'variable_analyzed' in stats
        assert 'wave_transition' in stats
        
        assert stats['variable_analyzed'] == 'HFClust_labeled'
        assert stats['wave_transition'] == 'w1_to_w2'
        assert isinstance(stats['top_patterns'], list)


@pytest.mark.integration
class TestAlluvialBuilderIntegration:
    """Integration tests for AlluvialVisualizationBuilder."""
    
    @pytest.mark.slow
    def test_full_build_process(self, sample_data, test_helpers):
        """Test complete build process from start to finish."""
        builder = AlluvialVisualizationBuilder()
        
        # This would normally require the full environment
        # For testing, we'll mock the heavy dependencies
        with patch('wave_visualizer.visualization_techs.alluvial_builder.parse_wave_config') as mock_parse, \
             patch('wave_visualizer.visualization_techs.alluvial_builder.validate_visualization_inputs'), \
             patch('wave_visualizer.visualization_techs.alluvial_builder.generate_column_names') as mock_gen, \
             patch.object(builder, '_configure_visualization'), \
             patch.object(builder, '_create_plotly_figure') as mock_create_fig:
            
            # Setup mocks
            mock_parse.return_value = ('W1_', 'W2_')
            mock_gen.return_value = ('W1_HFClust_labeled', 'W2_HFClust_labeled')
            mock_fig = Mock(spec=go.Figure)
            mock_create_fig.return_value = mock_fig
            
            # Configure and build
            fig, stats = (builder
                         .set_data(sample_data)
                         .set_variable('HFClust_labeled')
                         .set_wave_config('w1_to_w2')
                         .build())
            
            # Verify results
            assert fig is mock_fig
            test_helpers.assert_valid_statistics(stats)
    
    def test_build_with_filter(self, sample_data):
        """Test build process with filtering applied."""
        builder = AlluvialVisualizationBuilder()
        
        with patch('wave_visualizer.visualization_techs.alluvial_builder.parse_wave_config') as mock_parse, \
             patch('wave_visualizer.visualization_techs.alluvial_builder.validate_visualization_inputs'), \
             patch('wave_visualizer.visualization_techs.alluvial_builder.generate_column_names') as mock_gen, \
             patch.object(builder, '_apply_data_filter') as mock_filter, \
             patch.object(builder, '_configure_visualization'), \
             patch.object(builder, '_create_plotly_figure') as mock_create_fig:
            
            # Setup mocks
            mock_parse.return_value = ('W1_', 'W2_')
            mock_gen.return_value = ('W1_HFClust_labeled', 'W2_HFClust_labeled')
            mock_fig = Mock(spec=go.Figure)
            mock_create_fig.return_value = mock_fig
            
            # Build with filter
            fig, stats = (builder
                         .set_data(sample_data)
                         .apply_filter('PID1_labeled', 'Republican')
                         .build())
            
            # Verify filter was applied
            mock_filter.assert_called_once()
    
    def test_build_error_handling(self, sample_data):
        """Test error handling during build process."""
        builder = AlluvialVisualizationBuilder()
        
        with patch.object(builder, '_prepare_data', side_effect=Exception("Test error")):
            with pytest.raises(VisualizationError, match="Visualization build failed"):
                builder.set_data(sample_data).build()


@pytest.mark.unit 
class TestBuilderValidation:
    """Test validation aspects of the builder."""
    
    def test_build_fails_without_data(self):
        """Test that build fails appropriately when data is missing."""
        builder = AlluvialVisualizationBuilder()
        
        with patch.object(builder, '_load_default_data', side_effect=DataLoadingError("No data")):
            with pytest.raises(VisualizationError):
                builder.build()
    
    def test_build_validates_inputs(self, sample_data):
        """Test that build process validates inputs."""
        builder = AlluvialVisualizationBuilder()
        
        with patch('wave_visualizer.visualization_techs.alluvial_builder.validate_visualization_inputs') as mock_validate:
            mock_validate.side_effect = Exception("Validation failed")
            
            with pytest.raises(VisualizationError):
                builder.set_data(sample_data).build()
    
    def test_invalid_wave_config_handling(self, sample_data):
        """Test handling of invalid wave configuration."""
        builder = AlluvialVisualizationBuilder()
        
        with patch('wave_visualizer.visualization_techs.alluvial_builder.parse_wave_config') as mock_parse:
            mock_parse.side_effect = ValueError("Invalid config")
            
            with pytest.raises(VisualizationError, match="Invalid wave configuration"):
                builder.set_data(sample_data).set_wave_config('invalid').build() 