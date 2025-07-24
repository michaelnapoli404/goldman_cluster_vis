# Wave Visualizer

> Python package for visualizing longitudinal survey data transitions across multiple waves

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org/)

Wave Visualizer is a Python package designed for analyzing longitudinal survey data, particularly for political science research with multiple survey waves.

## Features

- **Dynamic Wave Configuration**: Support for unlimited survey waves with automatic detection
- **Semantic Color Mapping**: Consistent, meaningful color assignments for categorical variables  
- **Interactive Visualizations**: Alluvial plots (Sankey diagrams) for transition analysis
- **Export System**: HTML and high-resolution image export with automatic organization
- **Data Cleaning Pipeline**: Comprehensive preprocessing for SPSS (.sav) files
- **Type-Safe APIs**: Full type hints and IDE support

## Quick Start

### Installation

```bash
# Clone and install
git clone https://github.com/michaelnapoli404/wave-visualizer.git
cd wave-visualizer
pip install -e ".[image-export]"
```

### Basic Usage

```python
import wave_visualizer

# Create a visualization with one line
fig, stats = wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled',
    wave_config='w1_to_w3',
    filter_column='PID1_labeled',
    filter_value='Republican'
)

# Export to multiple formats
wave_visualizer.export_figure(fig, 'republican_transition', ['html', 'png'])
```

### Configuration

```python
# Add custom color mappings
wave_visualizer.add_color_mapping('Republican', '#FF0000')
wave_visualizer.add_color_mapping('Democrat', '#0000FF')

# Define new wave transitions
wave_visualizer.add_wave_definition('W4', 'w4_to_w5')
```

## No-Code Usage

**For non-programmers:** Use the `no_code/` folder to run visualizations without writing any code.

### Setup (One-time)
1. **Install Anaconda or Miniconda** from [anaconda.com](https://www.anaconda.com/products/distribution)
2. **Add your data file:**
   - Place `Ordered UC Berkeley W1_W2_W3 COMMON FILE.sav` in the main project `data/` folder

*Note: The conda environment will be created automatically when you first run the examples.*

### Run Examples
Navigate to the `no_code/` folder and:

- **Windows:** Double-click `run_examples.bat`
- **Mac/Linux:** Double-click `run_examples.sh`

### View Results
Check `example_visualizations/exports/` for:
- `.html` files - Interactive charts (open in web browser)
- `.png` files - High-resolution images for presentations

The no-code solution automatically runs all example visualizations and exports them in multiple formats. The scripts include robust error handling and will guide you through any setup issues.

**Customization:** You can edit the Python files in `example_visualizations/` fairly intuitively to create your own visualizations - just modify the variable names, wave configurations, or filter settings to analyze different aspects of your data.

## Example Output

The package generates interactive visualizations showing how survey responses transition between waves:

```
Wave 1 → Wave 3 Transitions (Republican Subset)
├── Stable patterns: 65%
├── Changed responses: 30% 
└── Missing data: 5%
```

See `example_visualizations/simple_demo.py` for a complete working example.

## Project Structure

```
wave_visualizer/
├── data_prep/          # Data cleaning and preprocessing
├── visualization_techs/ # Visualization generation
├── settings/           # Configuration and processed data
└── utils/              # Logging and utilities
```

## Requirements

- Python 3.8+
- pandas, plotly, pyreadstat
- Optional: kaleido (for image export)

## Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev,test]"

# Run quality checks
make all-checks

# Run tests
make test
```

## Documentation

For detailed documentation including:
- Complete API reference
- Settings system explanation
- Advanced configuration options
- Package architecture details

See: [`documentation.txt`](documentation.txt)

## Data Requirements

Your SPSS data should have:
- Wave-prefixed columns (e.g., `W1_variable`, `W2_variable`)
- Labeled categorical variables
- Consistent variable naming across waves

## Support

- Issues: [GitHub Issues](https://github.com/michaelnapoli404/wave-visualizer/issues)
- Documentation: [`documentation.txt`](documentation.txt)
- Examples: [`example_visualizations/`](example_visualizations/)

## License

MIT License - see LICENSE file for details.

## Citation

```bibtex
@software{wave_visualizer,
  title = {Wave Visualizer: Longitudinal Survey Data Visualization},
  author = {michaelnapoli404},
  year = {2024},
  url = {https://github.com/michaelnapoli404/wave-visualizer}
}
``` 