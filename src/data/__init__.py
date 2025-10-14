# Data processing package for SNP Data Processor
# Handles file loading, validation, and data preprocessing

# Import data processing classes (will be implemented later)
# from .snp_loader import SNPLoader
# from .data_processor import DataProcessor
# from .validator import FileValidator

# For now, placeholder to avoid import errors
SNPLoader = None
DataProcessor = None
FileValidator = None

# Supported file formats
SUPPORTED_FORMATS = {
    '.vcf': 'Variant Call Format',
    '.bed': 'Browser Extensible Data',
    '.ped': 'PLINK PED format', 
    '.csv': 'Comma Separated Values',
    '.txt': 'Tab-delimited text'
}

__all__ = ['SNPLoader', 'DataProcessor', 'FileValidator', 'SUPPORTED_FORMATS']