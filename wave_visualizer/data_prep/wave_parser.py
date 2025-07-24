"""
Wave Parser module for wave_visualizer package.

Reads wave definitions from CSV file to support unlimited waves dynamically.
Users can add new waves by simply adding rows to the wave_definitions.csv file.
"""

import pandas as pd
import re
from typing import Tuple, Optional, Dict, List
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

class WaveConfigParser:
    """
    Parses wave configuration strings using CSV-defined wave definitions.
    """
    
    def __init__(self, settings_dir: Optional[str] = None):
        """Initialize the wave parser."""
        if settings_dir is None:
            from wave_visualizer.settings import VISUALIZATION_DIR
            self.settings_dir = VISUALIZATION_DIR
        else:
            self.settings_dir = Path(settings_dir)
        
        self.wave_definitions_file = self.settings_dir / "wave_definitions.csv"
        
        # Storage for wave definitions
        self.wave_definitions = {}  # {wave_name: column_prefix}
        self.wave_numbers = {}      # {wave_number: (wave_name, column_prefix)}
        
        # Load wave definitions
        self._load_wave_definitions()
        
        # Regex pattern to match wave configurations like 'w1_to_w2', 'w4_to_w7', etc.
        self.wave_pattern = re.compile(r'^w(\d+)_to_w(\d+)$', re.IGNORECASE)
        
    def _load_wave_definitions(self) -> bool:
        """Load wave definitions from CSV file."""
        try:
            if not self.wave_definitions_file.exists():
                print(f"Warning: Wave definitions file not found: {self.wave_definitions_file}")
                print("Using default wave definitions: W1_, W2_, W3_")
                # Create default definitions
                self.wave_definitions = {
                    'Wave1': 'W1_',
                    'Wave2': 'W2_', 
                    'Wave3': 'W3_'
                }
                self.wave_numbers = {
                    1: ('Wave1', 'W1_'),
                    2: ('Wave2', 'W2_'),
                    3: ('Wave3', 'W3_')
                }
                return True
            
            wave_df = pd.read_csv(self.wave_definitions_file)
            
            # Validate required columns
            required_cols = ['wave_name', 'column_prefix']
            missing_cols = [col for col in required_cols if col not in wave_df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in wave definitions: {missing_cols}")
            
            # Load wave definitions
            for _, row in wave_df.iterrows():
                wave_name = row['wave_name']
                column_prefix = row['column_prefix']
                
                self.wave_definitions[wave_name] = column_prefix
                
                # Extract wave number from wave_name (assumes format like 'Wave1', 'Wave2')
                wave_num_match = re.search(r'(\d+)', wave_name)
                if wave_num_match:
                    wave_num = int(wave_num_match.group(1))
                    self.wave_numbers[wave_num] = (wave_name, column_prefix)
            
            print(f"Loaded {len(self.wave_definitions)} wave definitions")
            return True
            
        except Exception as e:
            print(f"Error loading wave definitions: {str(e)}")
            print("Using default wave definitions: W1_, W2_, W3_")
            # Fallback to defaults
            self.wave_definitions = {
                'Wave1': 'W1_',
                'Wave2': 'W2_', 
                'Wave3': 'W3_'
            }
            self.wave_numbers = {
                1: ('Wave1', 'W1_'),
                2: ('Wave2', 'W2_'),
                3: ('Wave3', 'W3_')
            }
            return False
        
    def parse_wave_config(self, wave_config: str) -> Tuple[str, str]:
        """
        Parse a wave configuration string using CSV-defined wave definitions.
        
        Args:
            wave_config: Wave configuration string (e.g., 'w1_to_w2', 'w4_to_w7')
            
        Returns:
            Tuple of (source_wave_prefix, target_wave_prefix) as strings (e.g., ('W1_', 'W2_'))
            
        Examples:
            'w1_to_w2' → ('W1_', 'W2_')
            'w2_to_w3' → ('W2_', 'W3_') 
            'w1_to_w5' → ('W1_', 'W5_') (if Wave5 is defined in CSV)
        """
        # Handle special cases first
        if wave_config.lower() == 'all_waves':
            # For all_waves, use first and last available waves
            available_waves = sorted(self.wave_numbers.keys())
            if len(available_waves) >= 2:
                first_wave = available_waves[0]
                last_wave = available_waves[-1]
                source_prefix = self.wave_numbers[first_wave][1]
                target_prefix = self.wave_numbers[last_wave][1]
                return source_prefix, target_prefix
            else:
                # Fallback to W1→W3
                return 'W1_', 'W3_'
        
        # Try to parse using regex
        match = self.wave_pattern.match(wave_config.strip())
        
        if match:
            source_num = int(match.group(1))
            target_num = int(match.group(2))
            
            # Validate wave numbers
            if source_num < 1 or target_num < 1:
                raise ValueError(f"Wave numbers must be positive integers, got: {wave_config}")
            
            if source_num == target_num:
                raise ValueError(f"Source and target waves must be different, got: {wave_config}")
            
            # Check if waves are defined in CSV
            if source_num not in self.wave_numbers:
                raise ValueError(f"Wave {source_num} not found in wave definitions. Available waves: {list(self.wave_numbers.keys())}")
            
            if target_num not in self.wave_numbers:
                raise ValueError(f"Wave {target_num} not found in wave definitions. Available waves: {list(self.wave_numbers.keys())}")
            
            # Get prefixes from CSV definitions
            source_prefix = self.wave_numbers[source_num][1]
            target_prefix = self.wave_numbers[target_num][1]
            
            print(f"  → Parsed wave config: {wave_config} → {source_prefix.rstrip('_')} to {target_prefix.rstrip('_')}")
            return source_prefix, target_prefix
        
        else:
            # Invalid format - provide helpful error message
            available_waves = list(self.wave_numbers.keys())
            raise ValueError(
                f"Invalid wave configuration: '{wave_config}'\n"
                f"Expected format: 'w<number>_to_w<number>' (e.g., 'w1_to_w2', 'w2_to_w3')\n"
                f"Available waves: {available_waves}\n"
                f"Or use 'all_waves' for multi-wave analysis"
            )
    
    def generate_column_names(self, source_wave_prefix: str, target_wave_prefix: str, variable_name: str) -> Tuple[str, str]:
        """
        Generate source and target column names based on wave prefixes from CSV.
        
        Args:
            source_wave_prefix: Source wave prefix (e.g., 'W1_', 'W4_')
            target_wave_prefix: Target wave prefix (e.g., 'W2_', 'W7_') 
            variable_name: Base variable name (e.g., 'HFClust_labeled')
            
        Returns:
            Tuple of (source_column, target_column) names
            
        Examples:
            ('W1_', 'W2_', 'HFClust_labeled') → ('W1_HFClust_labeled', 'W2_HFClust_labeled')
            ('W4_', 'W7_', 'PID1_labeled') → ('W4_PID1_labeled', 'W7_PID1_labeled')
        """
        source_column = f"{source_wave_prefix}{variable_name}"
        target_column = f"{target_wave_prefix}{variable_name}"
        
        return source_column, target_column
    
    def validate_wave_config(self, wave_config: str) -> bool:
        """
        Validate if a wave configuration string is properly formatted.
        
        Args:
            wave_config: Wave configuration string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.parse_wave_config(wave_config)
            return True
        except ValueError:
            return False
    
    def get_supported_formats(self) -> str:
        """
        Get a description of supported wave configuration formats.
        
        Returns:
            String describing supported formats
        """
        return (
            "Supported wave configuration formats:\n"
            "  - 'w1_to_w2': Wave 1 to Wave 2 transition\n"
            "  - 'w2_to_w3': Wave 2 to Wave 3 transition\n"
            "  - 'w1_to_w5': Wave 1 to Wave 5 transition (long-term)\n"
            "  - 'w4_to_w7': Wave 4 to Wave 7 transition\n"
            "  - 'all_waves': Multi-wave analysis (defaults to W1→W3)\n"
            "  - Any 'w<N>_to_w<M>' where N and M are positive integers"
        )

# Create a global parser instance for easy access (initialized later to avoid import issues)
wave_parser = None

def _get_wave_parser():
    """Get or create the global wave parser instance."""
    global wave_parser
    if wave_parser is None:
        wave_parser = WaveConfigParser()
    return wave_parser

def parse_wave_config(wave_config: str) -> Tuple[str, str]:
    """
    Convenience function to parse wave configuration.
    
    Args:
        wave_config: Wave configuration string
        
    Returns:
        Tuple of (source_wave_prefix, target_wave_prefix)
    """
    parser = _get_wave_parser()
    return parser.parse_wave_config(wave_config)

def generate_column_names(source_wave_prefix: str, target_wave_prefix: str, variable_name: str) -> Tuple[str, str]:
    """
    Convenience function to generate column names.
    
    Args:
        source_wave_prefix: Source wave prefix (e.g., 'W1_')
        target_wave_prefix: Target wave prefix (e.g., 'W2_')
        variable_name: Variable name (e.g., 'HFClust_labeled')
        
    Returns:
        Tuple of (source_column, target_column)
    """
    parser = _get_wave_parser()
    return parser.generate_column_names(source_wave_prefix, target_wave_prefix, variable_name)

def get_available_waves() -> List[int]:
    """
    Get list of available wave numbers from the CSV definitions.
    
    Returns:
        List of wave numbers
    """
    parser = _get_wave_parser()
    return list(parser.wave_numbers.keys())

def add_wave_definition(wave_name: str, column_prefix: str, description: str = "") -> bool:
    """
    Add a new wave definition to the CSV file.
    
    Args:
        wave_name: Wave name (e.g., 'Wave4')
        column_prefix: Column prefix (e.g., 'W4_')
        description: Optional description
        
    Returns:
        bool: True if added successfully
    """
    try:
        from wave_visualizer.settings import VISUALIZATION_DIR
        wave_file = VISUALIZATION_DIR / "wave_definitions.csv"
        
        # Read existing data
        if wave_file.exists():
            wave_df = pd.read_csv(wave_file)
        else:
            wave_df = pd.DataFrame(columns=['wave_name', 'column_prefix', 'description'])
        
        # Add new row
        new_row = pd.DataFrame({
            'wave_name': [wave_name],
            'column_prefix': [column_prefix], 
            'description': [description]
        })
        wave_df = pd.concat([wave_df, new_row], ignore_index=True)
        
        # Save back to CSV
        wave_df.to_csv(wave_file, index=False)
        
        # Reload the global parser
        global wave_parser
        wave_parser = None  # Force reload on next access
        
        print(f"Added wave definition: {wave_name} → {column_prefix}")
        return True
        
    except Exception as e:
        print(f"Error adding wave definition: {str(e)}")
        return False 