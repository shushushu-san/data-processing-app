# Data processing package for SNP Data Processor
# Handles file loading, validation, and data preprocessing

# Import data processing classes
from .s1p_loader import S1PLoader, load_s1p_file
# from .data_processor import DataProcessor
# from .validator import FileValidator

# For now, placeholder to avoid import errors for unimplemented modules
DataProcessor = None
FileValidator = None

# Supported file formats
SUPPORTED_FORMATS = {
    '.s1p': 'S1P Network Analyzer Data',
    '.s2p': 'S2P Network Analyzer Data', 
    '.vcf': 'Variant Call Format',
    '.bed': 'Browser Extensible Data',
    '.ped': 'PLINK PED format', 
    '.csv': 'Comma Separated Values',
    '.txt': 'Tab-delimited text'
}

__all__ = ['S1PLoader', 'load_s1p_file', 'DataProcessor', 'FileValidator', 'SUPPORTED_FORMATS']