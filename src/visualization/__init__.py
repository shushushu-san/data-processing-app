# Visualization package for SNP Data Processor
# Provides graph creation and plotting functionality

# Import visualization classes
from .s1p_plots import S1PPlotter, show_s1p_plot_dialog, create_s1p_plotter
from .dat_plots import DATPlotter, show_dat_plot_dialog, create_dat_plotter

# Import other visualization classes (will be implemented later)  
# from .plot_manager import PlotManager
# from .scatter_plot import ScatterPlot
# from .histogram import Histogram
# from .heatmap import Heatmap

# For now, placeholder to avoid import errors
PlotManager = None
ScatterPlot = None
Histogram = None
Heatmap = None

# Common plotting configuration
DEFAULT_PLOT_CONFIG = {
    'figure_size': (10, 6),
    'dpi': 100,
    'style': 'seaborn-v0_8',
    'font_size': 12,
    'title_size': 14,
    'label_size': 10
}

# Color palettes for different plot types
COLOR_PALETTES = {
    'default': 'viridis',
    'categorical': 'tab10', 
    'sequential': 'plasma',
    'diverging': 'coolwarm'
}

# Supported export formats
EXPORT_FORMATS = {
    'png': 'Portable Network Graphics',
    'pdf': 'Portable Document Format', 
    'svg': 'Scalable Vector Graphics',
    'eps': 'Encapsulated PostScript',
    'jpg': 'Joint Photographic Experts Group'
}

__all__ = [
    'S1PPlotter', 'show_s1p_plot_dialog', 'create_s1p_plotter',
    'DATPlotter', 'show_dat_plot_dialog', 'create_dat_plotter',
    'PlotManager', 'ScatterPlot', 'Histogram', 'Heatmap',
    'DEFAULT_PLOT_CONFIG', 'COLOR_PALETTES', 'EXPORT_FORMATS'
]