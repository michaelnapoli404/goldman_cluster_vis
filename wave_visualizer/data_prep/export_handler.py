"""
Export Handler for Wave Visualizer

Handles exporting visualizations to both HTML and image formats
in an 'exports' folder relative to the calling script.
"""

import os
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Union
import plotly.io as pio
import plotly.graph_objects as go
from ..utils.logger import get_logger
from ..exceptions import ExportError, handle_exception
from ..validators import ParameterValidator, sanitize_filename

logger = get_logger(__name__)


class ExportHandler:
    """Handles exporting visualizations in multiple formats."""
    
    def __init__(self) -> None:
        """Initialize the export handler."""
        # Set up plotly image export settings with proper error handling
        try:
            if pio.kaleido and pio.kaleido.scope:
                pio.kaleido.scope.mathjax = None  # Faster image export
        except (AttributeError, ImportError):
            # Kaleido not properly installed or configured, continue without it
            # This will still allow HTML exports to work
            pass
        
    def export_visualization(self, 
                           fig: go.Figure, 
                           filename: str, 
                           formats: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Export a plotly figure to multiple formats in an exports folder.
        
        Args:
            fig: Plotly figure object
            filename: Base filename (without extension)
            formats: List of formats to export ['html', 'png', 'svg', 'pdf']
        
        Returns:
            dict: Paths to exported files
        """
        if formats is None:
            formats = ['html', 'png']
        
        # Validate inputs
        filename = sanitize_filename(filename)
        formats = ParameterValidator.validate_list_parameter(formats, "formats", min_length=1, element_type=str)
        
        # Validate format types
        valid_formats = ['html', 'png', 'svg', 'pdf']
        for fmt in formats:
            if fmt not in valid_formats:
                raise ExportError(filename, fmt, ValueError(f"Unsupported format. Valid formats: {valid_formats}"))
            
        # Get the directory of the calling script
        caller_dir = self._get_caller_directory()
        
        # Create exports folder in caller's directory
        exports_dir = os.path.join(caller_dir, 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        exported_files = {}
        
        for format_type in formats:
            try:
                if format_type == 'html':
                    filepath = os.path.join(exports_dir, f"{filename}.html")
                    fig.write_html(filepath)
                    exported_files['html'] = filepath
                    logger.info(f"HTML exported: {filepath}")
                    
                elif format_type == 'png':
                    filepath = os.path.join(exports_dir, f"{filename}.png")
                    fig.write_image(filepath, width=1200, height=800, scale=2)
                    exported_files['png'] = filepath
                    logger.info(f"PNG exported: {filepath}")
                    
                elif format_type == 'svg':
                    filepath = os.path.join(exports_dir, f"{filename}.svg")
                    fig.write_image(filepath)
                    exported_files['svg'] = filepath
                    logger.info(f"SVG exported: {filepath}")
                    
                elif format_type == 'pdf':
                    filepath = os.path.join(exports_dir, f"{filename}.pdf")
                    fig.write_image(filepath)
                    exported_files['pdf'] = filepath
                    logger.info(f"PDF exported: {filepath}")
                    
            except Exception as e:
                raise ExportError(filepath, format_type, e)
                
        return exported_files
    
    def _get_caller_directory(self) -> str:
        """Get the directory of the script that's calling the export function."""
        # Walk up the call stack to find the first non-package file
        for frame_info in inspect.stack():
            filepath = frame_info.filename
            # Skip files that are part of our package
            if 'wave_visualizer' not in filepath and filepath.endswith('.py'):
                script_dir = os.path.dirname(os.path.abspath(filepath))
                
                # Special handling for example_visualizations scripts
                # If the script is in example_visualizations folder, use that directory
                if os.path.basename(script_dir) == 'example_visualizations':
                    return script_dir
                
                # If the script is in the project root but named something in example_visualizations
                script_name = os.path.basename(filepath)
                example_viz_path = os.path.join(script_dir, 'example_visualizations', script_name)
                if os.path.exists(example_viz_path):
                    return os.path.join(script_dir, 'example_visualizations')
                
                return script_dir
        
        # Fallback to current working directory
        return os.getcwd()


# Global export handler instance
_export_handler = ExportHandler()


def export_figure(fig: go.Figure, 
                  filename: str, 
                  formats: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Convenience function to export a figure.
    
    Args:
        fig: Plotly figure object
        filename: Base filename (without extension)
        formats: List of formats to export
        
    Returns:
        dict: Paths to exported files
    """
    return _export_handler.export_visualization(fig, filename, formats)


def create_exports_folder() -> str:
    """Create an exports folder in the caller's directory."""
    caller_dir = _export_handler._get_caller_directory()
    exports_dir = os.path.join(caller_dir, 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    return exports_dir 