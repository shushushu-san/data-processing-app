"""
Logging utilities for SNP Data Processor
Provides centralized logging configuration and management.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logger(
    name=None,
    log_level=logging.INFO,
    log_file='snp_processor.log',
    max_file_size=10*1024*1024,  # 10MB
    backup_count=5,
    console_output=True
):
    """
    Setup application logging with file rotation and console output.
    
    Args:
        name (str): Logger name (default: root logger)
        log_level (int): Logging level
        log_file (str): Log file name
        max_file_size (int): Maximum log file size before rotation
        backup_count (int): Number of backup files to keep
        console_output (bool): Enable console output
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Full path to log file
    log_path = log_dir / log_file
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file logger: {e}")
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Log the setup
    logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_path}")
    
    return logger


def get_logger(name):
    """
    Get a logger instance with the given name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_exception(logger, exception, context=""):
    """
    Log an exception with full traceback.
    
    Args:
        logger (logging.Logger): Logger instance
        exception (Exception): Exception to log
        context (str): Additional context information
    """
    import traceback
    
    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {str(exception)}"
    
    logger.error(error_msg)
    logger.error("Traceback:")
    
    # Log full traceback
    for line in traceback.format_tb(exception.__traceback__):
        logger.error(line.rstrip())


def log_performance(logger, operation_name, start_time, end_time=None):
    """
    Log performance metrics for an operation.
    
    Args:
        logger (logging.Logger): Logger instance
        operation_name (str): Name of the operation
        start_time (float): Start time (from time.time())
        end_time (float): End time (from time.time(), default: current time)
    """
    import time
    
    if end_time is None:
        end_time = time.time()
    
    duration = end_time - start_time
    logger.info(f"Performance - {operation_name}: {duration:.3f} seconds")


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, logger, operation_name):
        """
        Initialize performance timer.
        
        Args:
            logger (logging.Logger): Logger instance
            operation_name (str): Name of the operation being timed
        """
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log results."""
        import time
        end_time = time.time()
        
        if exc_type is not None:
            self.logger.error(f"Operation failed: {self.operation_name}")
            log_exception(self.logger, exc_val, self.operation_name)
        else:
            log_performance(self.logger, self.operation_name, self.start_time, end_time)


def setup_debug_logging():
    """Setup debug-level logging for development."""
    return setup_logger(
        name='snp_debug',
        log_level=logging.DEBUG,
        log_file='snp_debug.log',
        console_output=True
    )


def log_system_info(logger):
    """Log system information for debugging."""
    import sys
    import platform
    
    logger.info("=== System Information ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 30)


# Default logger setup for the application
def initialize_app_logging():
    """Initialize default application logging."""
    logger = setup_logger('snp_app')
    log_system_info(logger)
    return logger