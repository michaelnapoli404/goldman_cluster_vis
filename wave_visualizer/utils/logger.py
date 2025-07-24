"""
Centralized logging system for wave_visualizer package.

Provides a clean, professional logging interface that can be configured
for different verbosity levels and output formats.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union
import os


class WaveVisualizerFormatter(logging.Formatter):
    """Custom formatter for wave_visualizer logs."""
    
    def __init__(self):
        # Different formats for different log levels
        self.formats = {
            logging.DEBUG: "DEBUG | %(name)s.%(funcName)s:%(lineno)d | %(message)s",
            logging.INFO: "INFO | %(message)s",
            logging.WARNING: "WARNING | %(name)s | %(message)s",
            logging.ERROR: "ERROR | %(name)s.%(funcName)s:%(lineno)d | %(message)s",
            logging.CRITICAL: "CRITICAL | %(name)s | %(message)s"
        }
        super().__init__()
    
    def format(self, record):
        log_format = self.formats.get(record.levelno, self.formats[logging.INFO])
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


def setup_logger(name: str = "wave_visualizer", 
                 level: Union[int, str] = logging.INFO,
                 log_file: Optional[Union[str, Path]] = None,
                 console_output: bool = True) -> logging.Logger:
    """
    Set up a logger with consistent formatting and configuration.
    
    Args:
        name: Logger name (typically module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        console_output: Whether to output logs to console
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Set level
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # Create formatter
    formatter = WaveVisualizerFormatter()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with wave_visualizer configuration.
    
    Args:
        name: Logger name (if None, uses calling module's name)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if name is None:
        # Get the calling module's name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'wave_visualizer')
    
    # Use existing logger if it exists, otherwise create new one
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Configure with default settings
        return setup_logger(name)
    return logger


def configure_package_logging(level: Union[int, str] = logging.INFO,
                             log_file: Optional[str] = None,
                             quiet: bool = False) -> None:
    """
    Configure logging for the entire wave_visualizer package.
    
    Args:
        level: Logging level for all package loggers
        log_file: Optional file to write all package logs to
        quiet: If True, suppress console output
    """
    # Configure the root wave_visualizer logger
    setup_logger(
        name="wave_visualizer",
        level=level,
        log_file=log_file,
        console_output=not quiet
    )
    
    # Set environment variable for child loggers
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    os.environ['WAVE_VISUALIZER_LOG_LEVEL'] = str(level)


def get_verbosity_level() -> int:
    """Get the current verbosity level from environment or default."""
    try:
        return int(os.environ.get('WAVE_VISUALIZER_LOG_LEVEL', logging.INFO))
    except (ValueError, TypeError):
        return logging.INFO


# Convenience functions for common log patterns
def log_step(logger: logging.Logger, step_num: int, step_name: str, detail: str = ""):
    """Log a processing step with consistent formatting."""
    separator = "=" * 50
    logger.info(f"\n{separator}")
    logger.info(f"STEP {step_num}: {step_name.upper()}")
    logger.info(separator)
    if detail:
        logger.info(detail)


def log_success(logger: logging.Logger, message: str):
    """Log a success message."""
    logger.info(f"SUCCESS: {message}")


def log_completion(logger: logging.Logger, process_name: str):
    """Log process completion with standard formatting."""
    separator = "=" * 60
    logger.info(f"\n{separator}")
    logger.info(f"{process_name.upper()} COMPLETED SUCCESSFULLY!")
    logger.info(separator) 