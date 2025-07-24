# Wave Visualizer

> Python package for visualizing longitudinal survey data transitions across multiple waves

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org/)


## No-Code Usage

**Want to create visualizations without coding?** Use our simple launcher scripts!

### Quick Start - No Coding Required

1. **Download this project** (green "Code" button -> "Download ZIP")
2. **Extract the ZIP file** to your computer
3. Copy `Ordered UC Berkeley W1_W2_W3 COMMON FILE.sav` into the `data/` folder
4. **Double-click the launcher** for your operating system:
   - **Windows**: Double-click `no_code/run_examples.bat`
   - **Mac/Linux**: Double-click `no_code/run_examples.sh`

**That's it!** The script will:
- **Automatically find or guide you to install conda** (if needed)
- **Set up the complete environment** automatically
- **Run all example visualizations** and save them as interactive HTML files
- **Generate 9 political analysis visualizations** (Democrat, Republican, Independent)

### What You Get

The launcher creates these professional visualizations in the `example_visualizations/exports/` folder:

**For Each Political Party (Democrat, Republican, Independent):**
- **Alluvial Plots**: Flow diagrams showing how people transition between psychological categories
- **Heatmaps**: Percentage-based transition matrices with color intensity  
- **Pattern Analysis**: Ranked bar charts showing the most common transitions

**File Formats:**
- Interactive HTML files (open in any web browser)
- High-resolution PNG images (perfect for presentations)

### Customizing Your Analysis

Want to analyze different groups or variables? Simply edit the Python files in `example_visualizations/`:

```python
# Example: Change from 'Republican' to 'Independent'
wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled', 
    wave_config='w1_to_w3', 
    filter_column='PID1_labeled', 
    filter_value='Independent'  # <-- Change this
)
```

Just change the values in quotes and run the launcher again.

---

## Basic Usage

### Installation

1. **Clone or download** this repository
2. **Place your data file**: Copy `Ordered UC Berkeley W1_W2_W3 COMMON FILE.sav` into the `data/` folder
3. **Install conda** (if not already installed): [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html)
4. **Create the environment**:
   ```bash
   conda env create -f environment.yml
   ```
5. **Activate the environment**:
   ```bash
   conda activate goldman_env
   ```
6. **Install the package**:
   ```bash
   pip install -e .
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

## Features

- **Dynamic Wave Configuration**: Support for unlimited survey waves with automatic detection
- **Semantic Color Mapping**: Consistent, meaningful color assignments for categorical variables  
- **Interactive Visualizations**: 
  - Alluvial plots (Sankey diagrams) with separate wave nodes
  - Percentage-based heatmaps with red colorscale
  - Horizontal bar pattern analysis with stability color coding
- **Export System**: HTML and high-resolution image export with automatic organization
- **Data Cleaning Pipeline**: Comprehensive preprocessing for SPSS (.sav) files
- **Type-Safe APIs**: Full type hints and IDE support
- **No-Code Solution**: Simple launcher scripts for non-technical users 

## Configuration

```python
# Example: Custom analysis configuration
wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled',    # Variable to analyze
    wave_config='w1_to_w3',             # Wave transition
    filter_column='PID1_labeled',       # Filter by column  
    filter_value='Independent',         # Filter value
    show_plot=True                      # Display immediately
)
```

## Example Output

See `example_visualizations/political_w1_w3.py` for a complete working example generating 9 visualizations.

## Project Structure

```
wave_visualizer/
├── data_prep/               # Data cleaning and preprocessing
│   ├── cleaning/           # Cleaning pipeline components
│   ├── customization.py    # Color and style configuration
│   └── export_handler.py   # Export functionality
├── visualization_techs/     # Visualization generation
│   ├── alluvial_plots.py   # Alluvial/Sankey diagrams
│   ├── heatmaps.py         # Transition heatmaps
│   └── transition_pattern_analysis.py  # Pattern bar charts
├── settings/               # Configuration and processed data
├── utils/                  # Logging and utilities
├── example_visualizations/ # Ready-to-run examples
└── no_code/               # No-code launcher scripts
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

## Documentation and Advanced Usage

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