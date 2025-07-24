"""
Political Party Analysis: W1 to W3 Transitions

This script generates 9 comprehensive visualizations analyzing how different 
political party affiliations (Democrat, Republican, Independent) transition 
across psychological well-being categories from Wave 1 to Wave 3.

Generated visualizations:
- 3 Alluvial plots (one per party)
- 3 Heatmaps (one per party) 
- 3 Transition pattern analyses (one per party)
"""

import wave_visualizer

print("Starting Political Party Analysis: W1 to W3 Transitions")
print("=" * 60)

# =============================================================================
# DEMOCRATIC VOTERS ANALYSIS
# =============================================================================
print("\nDEMOCRATIC VOTERS - W1 to W3 Analysis")
print("-" * 40)

# Democrat Alluvial Plot
print("Creating Democratic voters alluvial plot...")
dem_alluvial, dem_alluvial_stats = wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3', 
    filter_column='PID1_labeled', filter_value='Democrat', show_plot=False
)
wave_visualizer.export_figure(dem_alluvial, 'democrat_alluvial_w1_w3')

# Democrat Heatmap
print("Creating Democratic voters heatmap...")
dem_heatmap, dem_heatmap_stats = wave_visualizer.create_heatmap_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Democrat', show_plot=False
)
wave_visualizer.export_figure(dem_heatmap, 'democrat_heatmap_w1_w3')

# Democrat Transition Pattern Analysis
print("Creating Democratic voters transition pattern analysis...")
dem_patterns, dem_pattern_stats = wave_visualizer.create_pattern_analysis_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Democrat', show_plot=False
)
wave_visualizer.export_figure(dem_patterns, 'democrat_patterns_w1_w3')

# =============================================================================
# REPUBLICAN VOTERS ANALYSIS  
# =============================================================================
print("\nREPUBLICAN VOTERS - W1 to W3 Analysis")
print("-" * 40)

# Republican Alluvial Plot
print("Creating Republican voters alluvial plot...")
rep_alluvial, rep_alluvial_stats = wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Republican', show_plot=False
)
wave_visualizer.export_figure(rep_alluvial, 'republican_alluvial_w1_w3')

# Republican Heatmap
print("Creating Republican voters heatmap...")
rep_heatmap, rep_heatmap_stats = wave_visualizer.create_heatmap_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Republican', show_plot=False
)
wave_visualizer.export_figure(rep_heatmap, 'republican_heatmap_w1_w3')

# Republican Transition Pattern Analysis
print("Creating Republican voters transition pattern analysis...")
rep_patterns, rep_pattern_stats = wave_visualizer.create_pattern_analysis_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Republican', show_plot=False
)
wave_visualizer.export_figure(rep_patterns, 'republican_patterns_w1_w3')

# =============================================================================
# INDEPENDENT VOTERS ANALYSIS
# =============================================================================
print("\nINDEPENDENT VOTERS - W1 to W3 Analysis")
print("-" * 40)

# Independent Alluvial Plot
print("Creating Independent voters alluvial plot...")
ind_alluvial, ind_alluvial_stats = wave_visualizer.create_alluvial_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Independent', show_plot=False
)
wave_visualizer.export_figure(ind_alluvial, 'independent_alluvial_w1_w3')

# Independent Heatmap
print("Creating Independent voters heatmap...")
ind_heatmap, ind_heatmap_stats = wave_visualizer.create_heatmap_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Independent', show_plot=False
)
wave_visualizer.export_figure(ind_heatmap, 'independent_heatmap_w1_w3')

# Independent Transition Pattern Analysis
print("Creating Independent voters transition pattern analysis...")
ind_patterns, ind_pattern_stats = wave_visualizer.create_pattern_analysis_visualization(
    variable_name='HFClust_labeled', wave_config='w1_to_w3',
    filter_column='PID1_labeled', filter_value='Independent', show_plot=False
)
wave_visualizer.export_figure(ind_patterns, 'independent_patterns_w1_w3')

print("\n" + "=" * 60)
print("COMPLETE! All 9 political visualizations have been generated.")
print("Check the 'exports' folder for HTML and PNG files.")
print("=" * 60)