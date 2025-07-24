"""
Pytest configuration and shared fixtures for wave_visualizer tests.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any
import os


@pytest.fixture
def sample_data():
    """Create sample survey data for testing."""
    np.random.seed(42)  # For reproducible tests
    
    n_observations = 1000
    
    # Create sample wave data
    data = {
        'ID': range(1, n_observations + 1),
        
        # Wave 1 data
        'W1_HFClust_labeled': np.random.choice(
            ['Thriving', 'Struggling', 'Suffering'], 
            size=n_observations, 
            p=[0.4, 0.4, 0.2]
        ),
        'W1_PID1_labeled': np.random.choice(
            ['Republican', 'Democrat', 'Independent'], 
            size=n_observations, 
            p=[0.35, 0.35, 0.3]
        ),
        
        # Wave 2 data (with some transitions)
        'W2_HFClust_labeled': np.random.choice(
            ['Thriving', 'Struggling', 'Suffering'], 
            size=n_observations, 
            p=[0.38, 0.42, 0.2]
        ),
        'W2_PID1_labeled': np.random.choice(
            ['Republican', 'Democrat', 'Independent'], 
            size=n_observations, 
            p=[0.36, 0.34, 0.3]
        ),
        
        # Wave 3 data
        'W3_HFClust_labeled': np.random.choice(
            ['Thriving', 'Struggling', 'Suffering'], 
            size=n_observations, 
            p=[0.39, 0.41, 0.2]
        ),
        'W3_PID1_labeled': np.random.choice(
            ['Republican', 'Democrat', 'Independent'], 
            size=n_observations, 
            p=[0.37, 0.33, 0.3]
        )
    }
    
    df = pd.DataFrame(data)
    
    # Add some missing values to make it realistic
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices, 'W2_HFClust_labeled'] = np.nan
    
    missing_indices = np.random.choice(df.index, size=30, replace=False)
    df.loc[missing_indices, 'W3_PID1_labeled'] = np.nan
    
    return df


@pytest.fixture
def sample_config():
    """Create sample configuration for testing."""
    return {
        'plot_params': {
            'figure_width': 800,
            'figure_height': 400,
            'title_size': 16,
            'label_size': 10,
            'node_thickness': 15,
            'node_padding': 10,
            'margin_left': 40,
            'margin_right': 40,
            'margin_top': 60,
            'margin_bottom': 40
        },
        'title': 'Test Visualization',
        'source_column': 'W1_HFClust_labeled',
        'target_column': 'W2_HFClust_labeled',
        'source_wave': 'W1',
        'target_wave': 'W2'
    }


@pytest.fixture
def temp_settings_dir():
    """Create temporary settings directory for testing."""
    temp_dir = tempfile.mkdtemp()
    settings_dir = Path(temp_dir) / "settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (settings_dir / "cleaning_settings").mkdir(exist_ok=True)
    (settings_dir / "visualization_settings").mkdir(exist_ok=True)
    (settings_dir / "metadata_output").mkdir(exist_ok=True)
    
    yield settings_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_color_mappings():
    """Create mock color mappings for testing."""
    return {
        'HFClust_labeled': {
            'Thriving': '#2E8B57',
            'Struggling': '#FF8C00',
            'Suffering': '#DC143C'
        },
        'PID1_labeled': {
            'Republican': '#D62728',
            'Democrat': '#1F77B4',
            'Independent': '#2CA02C'
        }
    }


@pytest.fixture
def mock_wave_definitions():
    """Create mock wave definitions for testing."""
    return {
        1: ('Wave1', 'W1_'),
        2: ('Wave2', 'W2_'),
        3: ('Wave3', 'W3_')
    }


@pytest.fixture
def sample_transition_data():
    """Create sample transition data for testing."""
    return pd.DataFrame({
        'source': ['Thriving', 'Thriving', 'Struggling', 'Struggling', 'Suffering'],
        'target': ['Thriving', 'Struggling', 'Struggling', 'Thriving', 'Suffering'],
        'count': [400, 50, 300, 80, 170],
        'percentage': [40.0, 5.0, 30.0, 8.0, 17.0]
    })


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up environment variables before and after each test."""
    # Store original values
    original_env = {}
    test_env_vars = ['WAVE_VISUALIZER_LOG_LEVEL', 'WAVE_VISUALIZER_CONFIG']
    
    for var in test_env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]
        if var in original_env:
            os.environ[var] = original_env[var]


@pytest.fixture
def mock_processed_data_file(tmp_path, sample_data):
    """Create a mock processed data file for testing."""
    data_file = tmp_path / "processed_data.csv"
    sample_data.to_csv(data_file, index=False)
    return data_file


# Test markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests that take more than a few seconds")
    config.addinivalue_line("markers", "requires_data: Tests that require sample data files")


# Custom assertion helpers
class TestHelpers:
    """Helper methods for testing."""
    
    @staticmethod
    def assert_valid_plotly_figure(fig):
        """Assert that a figure is a valid Plotly figure."""
        import plotly.graph_objects as go
        assert isinstance(fig, go.Figure)
        assert fig.data is not None
        assert len(fig.data) > 0
    
    @staticmethod
    def assert_valid_statistics(stats: Dict[str, Any]):
        """Assert that statistics dictionary has required fields."""
        required_fields = ['total_transitions', 'unique_patterns', 'stability_rate']
        for field in required_fields:
            assert field in stats
            assert isinstance(stats[field], (int, float))
        
        # Validate ranges
        assert stats['total_transitions'] >= 0
        assert stats['unique_patterns'] >= 0
        assert 0 <= stats['stability_rate'] <= 100
    
    @staticmethod
    def assert_valid_color_list(colors, expected_length=None):
        """Assert that colors list is valid."""
        assert isinstance(colors, list)
        if expected_length:
            assert len(colors) == expected_length
        
        for color in colors:
            assert isinstance(color, str)
            # Check if it's a hex color or named color
            assert (color.startswith('#') and len(color) in [4, 7]) or color.isalpha()


@pytest.fixture
def test_helpers():
    """Provide test helper methods."""
    return TestHelpers() 