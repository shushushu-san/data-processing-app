"""
Configuration Manager for SNP Data Processor
Handles application settings and user preferences.
"""

import configparser
import os
from pathlib import Path


class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self, config_file='config.ini'):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Name of the configuration file
        """
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        
        # Default configuration
        self.defaults = {
            'GUI': {
                'window_size': '1200x800',
                'theme': 'default',
                'remember_geometry': 'true'
            },
            'Files': {
                'recent_files_count': '10',
                'auto_backup': 'true',
                'default_export_format': 'png'
            },
            'Analysis': {
                'default_pca_components': '2',
                'clustering_method': 'kmeans',
                'max_memory_usage': '1000'  # MB
            },
            'Visualization': {
                'default_plot_size': '10,6',
                'dpi': '100',
                'color_palette': 'viridis'
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create with defaults."""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
                # Ensure all default sections exist
                self._ensure_defaults()
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create configuration with default values."""
        self.config.clear()
        for section, options in self.defaults.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save_config()
    
    def _ensure_defaults(self):
        """Ensure all default sections and keys exist."""
        for section, options in self.defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, value)
    
    def get(self, section, key, fallback=None):
        """
        Get configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value or fallback
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback or self.defaults.get(section, {}).get(key)
    
    def getint(self, section, key, fallback=None):
        """Get integer configuration value."""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            default_val = fallback or self.defaults.get(section, {}).get(key)
            return int(default_val) if default_val else 0
    
    def getboolean(self, section, key, fallback=None):
        """Get boolean configuration value."""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            default_val = fallback or self.defaults.get(section, {}).get(key, 'false')
            return default_val.lower() == 'true'
    
    def set(self, section, key, value):
        """
        Set configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value: Value to set
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_recent_files(self):
        """Get list of recent files."""
        recent_files = []
        max_files = self.getint('Files', 'recent_files_count', 10)
        
        for i in range(max_files):
            file_path = self.get('RecentFiles', f'file_{i}')
            if file_path and Path(file_path).exists():
                recent_files.append(file_path)
        
        return recent_files
    
    def add_recent_file(self, file_path):
        """Add file to recent files list."""
        if not self.config.has_section('RecentFiles'):
            self.config.add_section('RecentFiles')
        
        # Get current recent files
        recent_files = self.get_recent_files()
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only max number
        max_files = self.getint('Files', 'recent_files_count', 10)
        recent_files = recent_files[:max_files]
        
        # Clear and update
        self.config.remove_section('RecentFiles')
        self.config.add_section('RecentFiles')
        
        for i, file_path in enumerate(recent_files):
            self.config.set('RecentFiles', f'file_{i}', file_path)
        
        self.save_config()
    
    def get_window_geometry(self):
        """Get saved window geometry."""
        if self.getboolean('GUI', 'remember_geometry'):
            width = self.getint('WindowGeometry', 'width', 1200)
            height = self.getint('WindowGeometry', 'height', 800)
            x = self.getint('WindowGeometry', 'x', 100)
            y = self.getint('WindowGeometry', 'y', 100)
            return f"{width}x{height}+{x}+{y}"
        return self.get('GUI', 'window_size', '1200x800')
    
    def save_window_geometry(self, geometry):
        """Save window geometry."""
        if self.getboolean('GUI', 'remember_geometry'):
            if not self.config.has_section('WindowGeometry'):
                self.config.add_section('WindowGeometry')
            
            # Parse geometry string (e.g., "1200x800+100+50")
            try:
                size_pos = geometry.split('+')
                size = size_pos[0].split('x')
                
                self.set('WindowGeometry', 'width', size[0])
                self.set('WindowGeometry', 'height', size[1])
                
                if len(size_pos) >= 3:
                    self.set('WindowGeometry', 'x', size_pos[1])
                    self.set('WindowGeometry', 'y', size_pos[2])
                
                self.save_config()
            except Exception as e:
                print(f"Error saving window geometry: {e}")