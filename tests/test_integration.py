"""
Integration tests for wave_visualizer package.

Tests the full workflow from data loading to visualization creation.
"""

import pytest
import pandas as pd
from unittest.mock import patch, Mock
import wave_visualizer


@pytest.mark.integration
class TestFullVisualizationWorkflow:
    """Test complete visualization workflow."""
    
    @patch('wave_visualizer.visualization_techs.alluvial_plots.pd.read_csv')
    def test_create_alluvial_visualization_basic(self, mock_read_csv, sample_data, test_helpers):
        """Test basic alluvial visualization creation."""
        mock_read_csv.return_value = sample_data
        
        # This tests the main API function
        fig, stats = wave_visualizer.create_alluvial_visualization(
            variable_name='HFClust_labeled',
            wave_config='w1_to_w2'
        )
        
        # Verify output structure
        test_helpers.assert_valid_plotly_figure(fig)
        test_helpers.assert_valid_statistics(stats)
        
        # Verify statistics content
        assert stats['variable_analyzed'] == 'HFClust_labeled'
        assert stats['wave_transition'] == 'w1_to_w2'
    
    @patch('wave_visualizer.visualization_techs.alluvial_plots.pd.read_csv')
    def test_create_alluvial_visualization_with_filter(self, mock_read_csv, sample_data, test_helpers):
        """Test alluvial visualization with filtering."""
        mock_read_csv.return_value = sample_data
        
        fig, stats = wave_visualizer.create_alluvial_visualization(
            variable_name='HFClust_labeled',
            wave_config='w1_to_w3',
            filter_column='PID1_labeled',
            filter_value='Republican'
        )
        
        test_helpers.assert_valid_plotly_figure(fig)
        test_helpers.assert_valid_statistics(stats)
        
        # Statistics should reflect the filtering
        assert stats['total_transitions'] > 0
        assert stats['total_transitions'] < len(sample_data)  # Should be filtered
    
    def test_create_alluvial_visualization_with_data(self, sample_data, test_helpers):
        """Test alluvial visualization with provided data."""
        fig, stats = wave_visualizer.create_alluvial_visualization(
            data=sample_data,
            variable_name='HFClust_labeled',
            wave_config='w1_to_w2'
        )
        
        test_helpers.assert_valid_plotly_figure(fig)
        test_helpers.assert_valid_statistics(stats)


@pytest.mark.integration
class TestExportWorkflow:
    """Test export functionality integration."""
    
    def test_export_figure_basic(self, tmp_path):
        """Test basic figure export functionality."""
        # Create a simple mock figure
        mock_fig = Mock()
        mock_fig.write_html = Mock()
        mock_fig.write_image = Mock()
        
        with patch('wave_visualizer.data_prep.export_handler._export_handler._get_caller_directory') as mock_caller:
            mock_caller.return_value = str(tmp_path)
            
            result = wave_visualizer.export_figure(mock_fig, 'test_export')
            
            # Verify exports directory was created
            exports_dir = tmp_path / 'exports'
            assert exports_dir.exists()
            
            # Verify result structure
            assert isinstance(result, dict)
            assert 'html' in result or 'png' in result
    
    def test_export_figure_custom_formats(self, tmp_path):
        """Test figure export with custom formats."""
        mock_fig = Mock()
        mock_fig.write_html = Mock()
        mock_fig.write_image = Mock()
        
        with patch('wave_visualizer.data_prep.export_handler._export_handler._get_caller_directory') as mock_caller:
            mock_caller.return_value = str(tmp_path)
            
            result = wave_visualizer.export_figure(
                mock_fig, 'test_export', formats=['html', 'png', 'svg']
            )
            
            # Should attempt to create all requested formats
            assert mock_fig.write_html.called
            assert mock_fig.write_image.called


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    def test_configure_package_logging(self):
        """Test package logging configuration."""
        # Should not raise exception
        wave_visualizer.configure_package_logging(level='INFO')
        
        # Test that logger can be retrieved
        logger = wave_visualizer.get_logger('test')
        assert logger is not None
    
    def test_add_color_mapping_integration(self, temp_settings_dir):
        """Test color mapping addition."""
        with patch('wave_visualizer.data_prep.color_mapping.VISUALIZATION_DIR', temp_settings_dir):
            # Should not raise exception
            result = wave_visualizer.add_color_mapping(
                'test_variable', 'test_value', '#FF0000', 'Test color'
            )
            assert isinstance(result, bool)
    
    def test_wave_definition_integration(self, temp_settings_dir):
        """Test wave definition functionality."""
        with patch('wave_visualizer.data_prep.wave_parser.VISUALIZATION_DIR', temp_settings_dir):
            # Get initial waves
            initial_waves = wave_visualizer.get_available_waves()
            
            # Add new wave
            result = wave_visualizer.add_wave_definition('Wave4', 'W4_', 'Test wave')
            assert isinstance(result, bool)


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @patch('wave_visualizer.visualization_techs.alluvial_plots.pd.read_csv')
    def test_complete_visualization_and_export_workflow(self, mock_read_csv, sample_data, tmp_path):
        """Test complete workflow from visualization to export."""
        mock_read_csv.return_value = sample_data
        
        with patch('wave_visualizer.data_prep.export_handler._export_handler._get_caller_directory') as mock_caller:
            mock_caller.return_value = str(tmp_path)
            
            # Step 1: Create visualization
            fig, stats = wave_visualizer.create_alluvial_visualization(
                variable_name='HFClust_labeled',
                wave_config='w1_to_w2',
                filter_column='PID1_labeled',
                filter_value='Republican'
            )
            
            # Step 2: Export visualization
            with patch.object(fig, 'write_html'), patch.object(fig, 'write_image'):
                export_result = wave_visualizer.export_figure(fig, 'republican_analysis')
            
            # Verify complete workflow
            assert stats['total_transitions'] > 0
            assert isinstance(export_result, dict)
    
    def test_error_propagation_through_workflow(self):
        """Test that errors propagate properly through the workflow."""
        # Test with invalid data
        with pytest.raises(Exception):  # Should raise some validation error
            wave_visualizer.create_alluvial_visualization(
                data=pd.DataFrame(),  # Empty DataFrame should fail validation
                variable_name='nonexistent_column'
            )


@pytest.mark.integration
class TestPackageAPIConsistency:
    """Test that package API remains consistent."""
    
    def test_main_functions_exist(self):
        """Test that main API functions are available."""
        # Visualization functions
        assert hasattr(wave_visualizer, 'create_alluvial_visualization')
        assert callable(wave_visualizer.create_alluvial_visualization)
        
        # Export functions
        assert hasattr(wave_visualizer, 'export_figure')
        assert callable(wave_visualizer.export_figure)
        
        # Configuration functions
        assert hasattr(wave_visualizer, 'configure_package_logging')
        assert callable(wave_visualizer.configure_package_logging)
        
        # Color mapping functions
        assert hasattr(wave_visualizer, 'add_color_mapping')
        assert callable(wave_visualizer.add_color_mapping)
        
        # Wave configuration functions
        assert hasattr(wave_visualizer, 'get_available_waves')
        assert callable(wave_visualizer.get_available_waves)
    
    def test_function_signatures_unchanged(self):
        """Test that critical function signatures haven't changed."""
        import inspect
        
        # Test create_alluvial_visualization signature
        sig = inspect.signature(wave_visualizer.create_alluvial_visualization)
        expected_params = ['data', 'variable_name', 'wave_config', 'filter_column', 'filter_value']
        
        for param in expected_params:
            assert param in sig.parameters
    
    def test_package_metadata(self):
        """Test package metadata consistency."""
        assert hasattr(wave_visualizer, '__version__')
        assert hasattr(wave_visualizer, '__author__')
        
        # Version should be a string
        assert isinstance(wave_visualizer.__version__, str)
        assert wave_visualizer.__version__ != "" 