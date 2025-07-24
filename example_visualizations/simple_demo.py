"""
Simple demonstration of the wave_visualizer package
"""

import wave_visualizer

# Create W1→W3 visualization for Republicans only
fig, stats = wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled', 
    wave_config='w1_to_w3',
    filter_column='PID1_labeled',
    filter_value='Republican'
)

# Export to both HTML and PNG in local exports folder
wave_visualizer.export_figure(fig, 'republican_w1_to_w3')