# Utils package for SNP Data Processor
# Provides configuration management and logging utilities

from .config import ConfigManager
from .logger import setup_logger

# Application constants
APP_NAME = "SNP Data Processor"
APP_VERSION = "1.0.0"
SUPPORTED_FORMATS = ['.vcf', '.bed', '.ped', '.csv', '.txt']

__all__ = ['ConfigManager', 'setup_logger']