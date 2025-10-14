# Analysis package for SNP Data Processor  
# Provides statistical analysis and machine learning functionality

# Import analysis classes (will be implemented later)
# from .statistics import BasicStats
# from .clustering import KMeansAnalysis, HierarchicalClustering
# from .pca import PCAAnalysis

# For now, placeholder to avoid import errors
BasicStats = None
KMeansAnalysis = None
HierarchicalClustering = None
PCAAnalysis = None

# Analysis result format definition
ANALYSIS_RESULT_FORMAT = {
    'data': None,
    'metadata': {
        'analysis_type': '',
        'timestamp': '',
        'parameters': {}
    },
    'plot_config': {
        'title': '',
        'xlabel': '',
        'ylabel': '',
        'legend': True
    }
}

# Default analysis parameters
DEFAULT_PARAMETERS = {
    'pca': {
        'n_components': 2,
        'standardize': True
    },
    'kmeans': {
        'n_clusters': 3,
        'random_state': 42
    },
    'hierarchical': {
        'linkage': 'ward',
        'n_clusters': 3
    }
}

__all__ = [
    'BasicStats', 'KMeansAnalysis', 'HierarchicalClustering', 'PCAAnalysis',
    'ANALYSIS_RESULT_FORMAT', 'DEFAULT_PARAMETERS'
]