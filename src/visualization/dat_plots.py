"""
DAT Data Visualization Module
Provides specialized plotting functions for DAT (frequency domain) data files.
"""

import matplotlib.pyplot as plt
import matplotlib.figure as mpl_figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class DATPlotter:
    """
    Specialized plotting class for DAT frequency domain data.
    
    Provides various plot types commonly used for frequency domain analysis:
    - Amplitude vs Frequency
    - Phase vs Frequency  
    - Combined amplitude and phase plot
    - Average data comparison plots
    """
    
    def __init__(self, parent_widget=None):
        """
        Initialize the DAT plotter.
        
        Args:
            parent_widget: Parent Tkinter widget for embedded plots
        """
        self.parent_widget = parent_widget
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.current_data = None
        
        # Default plot styling
        self.plot_style = {
            'figure_size': (10, 6),
            'dpi': 100,
            'facecolor': 'white',
            'grid': True,
            'grid_alpha': 0.3,
            'line_width': 1.5,
            'marker_size': 3
        }
        
        # Color scheme
        self.colors = {
            'amplitude': '#1f77b4',      # Blue
            'phase': '#ff7f0e',          # Orange
            'average_amp': '#2ca02c',    # Green
            'average_phase': '#d62728',  # Red
            'grid': '#cccccc',
            'text': '#333333'
        }
    
    def create_amplitude_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create an amplitude vs frequency plot.
        
        Args:
            data: DataFrame with DAT data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Plot primary amplitude
        if 'Frequency_kHz' in data.columns and 'Amplitude' in data.columns:
            freq_data = data['Frequency_kHz'].dropna()
            amp_data = data['Amplitude'].dropna()
            
            # Ensure same length
            min_len = min(len(freq_data), len(amp_data))
            freq_data = freq_data.iloc[:min_len]
            amp_data = amp_data.iloc[:min_len]
            
            ax.plot(freq_data, amp_data, 
                   color=self.colors['amplitude'], 
                   linewidth=self.plot_style['line_width'],
                   label='Amplitude')
        
        # Formatting
        ax.set_xlabel('Frequency (kHz)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        ax.set_title('Amplitude vs Frequency', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('frequency_range_khz'):
            freq_range = metadata['frequency_range_khz']
            info_text += f"\\nFreq Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} kHz"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created amplitude plot")
        return self.figure
    
    def create_phase_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a phase vs frequency plot.
        
        Args:
            data: DataFrame with DAT data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Plot primary phase
        if 'Frequency_kHz' in data.columns and 'Phase' in data.columns:
            freq_data = data['Frequency_kHz'].dropna()
            phase_data = data['Phase'].dropna()
            
            # Ensure same length
            min_len = min(len(freq_data), len(phase_data))
            freq_data = freq_data.iloc[:min_len]
            phase_data = phase_data.iloc[:min_len]
            
            ax.plot(freq_data, phase_data, 
                   color=self.colors['phase'], 
                   linewidth=self.plot_style['line_width'],
                   label='Phase')
        
        # Formatting
        ax.set_xlabel('Frequency (kHz)', fontsize=12)
        ax.set_ylabel('Phase (degrees)', fontsize=12)
        ax.set_title('Phase vs Frequency', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('frequency_range_khz'):
            freq_range = metadata['frequency_range_khz']
            info_text += f"\\nFreq Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} kHz"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created phase plot")
        return self.figure
    
    def create_combined_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a combined amplitude and phase plot with dual y-axes.
        
        Args:
            data: DataFrame with DAT data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        
        lines = []
        
        # Plot amplitude on left axis
        if 'Frequency_kHz' in data.columns and 'Amplitude' in data.columns:
            freq_data = data['Frequency_kHz'].dropna()
            amp_data = data['Amplitude'].dropna()
            
            # Ensure same length
            min_len = min(len(freq_data), len(amp_data))
            freq_data = freq_data.iloc[:min_len]
            amp_data = amp_data.iloc[:min_len]
            
            line1 = ax1.plot(freq_data, amp_data, 
                            color=self.colors['amplitude'], 
                            linewidth=self.plot_style['line_width'],
                            label='Amplitude')
            lines.extend(line1)
        
        # Plot phase on right axis  
        if 'Frequency_kHz' in data.columns and 'Phase' in data.columns:
            freq_data = data['Frequency_kHz'].dropna()
            phase_data = data['Phase'].dropna()
            
            # Ensure same length
            min_len = min(len(freq_data), len(phase_data))
            freq_data = freq_data.iloc[:min_len]
            phase_data = phase_data.iloc[:min_len]
            
            line2 = ax2.plot(freq_data, phase_data, 
                            color=self.colors['phase'], 
                            linewidth=self.plot_style['line_width'],
                            label='Phase')
            lines.extend(line2)
        
        # Formatting
        ax1.set_xlabel('Frequency (kHz)', fontsize=12)
        ax1.set_ylabel('Amplitude', fontsize=12, color=self.colors['amplitude'])
        ax2.set_ylabel('Phase (degrees)', fontsize=12, color=self.colors['phase'])
        ax1.set_title('Amplitude and Phase vs Frequency', fontsize=14, fontweight='bold')
        
        ax1.grid(True, alpha=self.plot_style['grid_alpha'])
        ax1.tick_params(axis='y', labelcolor=self.colors['amplitude'])
        ax2.tick_params(axis='y', labelcolor=self.colors['phase'])
        
        # Combined legend
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('frequency_range_khz'):
            freq_range = metadata['frequency_range_khz']
            info_text += f"\\nFreq Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} kHz"
        ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, 
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created combined amplitude and phase plot")
        return self.figure
    
    def create_custom_plot(self, data: pd.DataFrame, metadata: Dict[str, Any], x_column: str, y_column: str) -> mpl_figure.Figure:
        """
        Create a custom X-Y plot with user-selected columns.
        
        Args:
            data: DataFrame with DAT data
            metadata: Metadata dictionary
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Get data for plotting
        if x_column in data.columns and y_column in data.columns:
            x_data = data[x_column].dropna()
            y_data = data[y_column].dropna()
            
            # Ensure same length
            min_len = min(len(x_data), len(y_data))
            x_data = x_data.iloc[:min_len]
            y_data = y_data.iloc[:min_len]
            
            ax.plot(x_data, y_data, 
                   color=self.colors['amplitude'], 
                   linewidth=self.plot_style['line_width'],
                   marker='o',
                   markersize=self.plot_style['marker_size'],
                   label=f'{y_column} vs {x_column}')
        
        # Formatting
        ax.set_xlabel(self._format_axis_label(x_column), fontsize=12)
        ax.set_ylabel(self._format_axis_label(y_column), fontsize=12)
        ax.set_title(f'{y_column} vs {x_column}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add metadata info
        info_text = f"Points: {min_len}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info(f"Created custom plot: {y_column} vs {x_column}")
        return self.figure
    
    def _format_axis_label(self, column_name: str) -> str:
        """Format column name for axis label."""
        # Add units based on column name
        if 'Frequency' in column_name:
            if 'kHz' in column_name:
                return f"{column_name.replace('_', ' ')} (kHz)"
            elif 'Hz' in column_name:
                return f"{column_name.replace('_', ' ')} (Hz)"
            else:
                return column_name.replace('_', ' ')
        elif 'Phase' in column_name:
            return f"{column_name.replace('_', ' ')} (degrees)"
        elif 'Amplitude' in column_name:
            return f"{column_name.replace('_', ' ')}"
        else:
            return column_name.replace('_', ' ')
    
    def create_amplitude_overlay_plot(self, dat_files: List[Dict[str, Any]]) -> mpl_figure.Figure:
        """
        Create an overlaid amplitude plot for multiple DAT files.
        
        Args:
            dat_files: List of file info dictionaries with DAT data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(dat_files)))
        
        # Plot each file
        for i, file_info in enumerate(dat_files):
            data = file_info['data']
            label = file_info['name']
            
            if 'Frequency_kHz' in data.columns and 'Amplitude' in data.columns:
                freq_data = data['Frequency_kHz'].dropna()
                amp_data = data['Amplitude'].dropna()
                
                # Ensure same length
                min_len = min(len(freq_data), len(amp_data))
                freq_data = freq_data.iloc[:min_len]
                amp_data = amp_data.iloc[:min_len]
                
                ax.plot(freq_data, amp_data, 
                       color=colors[i], 
                       linewidth=self.plot_style['line_width'],
                       label=label)
        
        # Formatting
        ax.set_xlabel('Frequency (kHz)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        ax.set_title(f'Amplitude Comparison ({len(dat_files)} files)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created overlaid amplitude plot for {len(dat_files)} files")
        return self.figure
    
    def create_phase_overlay_plot(self, dat_files: List[Dict[str, Any]]) -> mpl_figure.Figure:
        """
        Create an overlaid phase plot for multiple DAT files.
        
        Args:
            dat_files: List of file info dictionaries with DAT data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(dat_files)))
        
        # Plot each file
        for i, file_info in enumerate(dat_files):
            data = file_info['data']
            label = file_info['name']
            
            if 'Frequency_kHz' in data.columns and 'Phase' in data.columns:
                freq_data = data['Frequency_kHz'].dropna()
                phase_data = data['Phase'].dropna()
                
                # Ensure same length
                min_len = min(len(freq_data), len(phase_data))
                freq_data = freq_data.iloc[:min_len]
                phase_data = phase_data.iloc[:min_len]
                
                ax.plot(freq_data, phase_data, 
                       color=colors[i], 
                       linewidth=self.plot_style['line_width'],
                       label=label)
        
        # Formatting
        ax.set_xlabel('Frequency (kHz)', fontsize=12)
        ax.set_ylabel('Phase (degrees)', fontsize=12)
        ax.set_title(f'Phase Comparison ({len(dat_files)} files)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created overlaid phase plot for {len(dat_files)} files")
        return self.figure
    
    def create_combined_overlay_plot(self, dat_files: List[Dict[str, Any]]) -> mpl_figure.Figure:
        """
        Create an overlaid combined plot for multiple DAT files with separate subplots.
        
        Args:
            dat_files: List of file info dictionaries with DAT data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=(12, 8), 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        # Create subplots for amplitude and phase
        ax1 = self.figure.add_subplot(211)  # Top subplot for amplitude
        ax2 = self.figure.add_subplot(212)  # Bottom subplot for phase
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(dat_files)))
        
        # Plot amplitude and phase for each file
        for i, file_info in enumerate(dat_files):
            data = file_info['data']
            label = file_info['name']
            
            # Plot amplitude
            if 'Frequency_kHz' in data.columns and 'Amplitude' in data.columns:
                freq_data = data['Frequency_kHz'].dropna()
                amp_data = data['Amplitude'].dropna()
                
                # Ensure same length
                min_len = min(len(freq_data), len(amp_data))
                freq_data = freq_data.iloc[:min_len]
                amp_data = amp_data.iloc[:min_len]
                
                ax1.plot(freq_data, amp_data, 
                        color=colors[i], linewidth=self.plot_style['line_width'], label=label)
            
            # Plot phase
            if 'Frequency_kHz' in data.columns and 'Phase' in data.columns:
                freq_data = data['Frequency_kHz'].dropna()
                phase_data = data['Phase'].dropna()
                
                # Ensure same length
                min_len = min(len(freq_data), len(phase_data))
                freq_data = freq_data.iloc[:min_len]
                phase_data = phase_data.iloc[:min_len]
                
                ax2.plot(freq_data, phase_data, 
                        color=colors[i], linewidth=self.plot_style['line_width'], label=label)
        
        # Formatting for amplitude plot
        ax1.set_ylabel('Amplitude', fontsize=12)
        ax1.set_title(f'Amplitude & Phase Comparison ({len(dat_files)} files)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=self.plot_style['grid_alpha'])
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Formatting for phase plot
        ax2.set_xlabel('Frequency (kHz)', fontsize=12)
        ax2.set_ylabel('Phase (degrees)', fontsize=12)
        ax2.grid(True, alpha=self.plot_style['grid_alpha'])
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created combined overlay plot for {len(dat_files)} files")
        return self.figure
    
    def create_custom_overlay_plot(self, dat_files: List[Dict[str, Any]], x_column: str, y_column: str) -> mpl_figure.Figure:
        """
        Create an overlaid custom plot for multiple DAT files.
        
        Args:
            dat_files: List of file info dictionaries with DAT data
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(dat_files)))
        
        # Plot each file
        for i, file_info in enumerate(dat_files):
            data = file_info['data']
            label = file_info['name']
            
            if x_column in data.columns and y_column in data.columns:
                x_data = data[x_column].dropna()
                y_data = data[y_column].dropna()
                
                # Ensure same length
                min_len = min(len(x_data), len(y_data))
                x_data = x_data.iloc[:min_len]
                y_data = y_data.iloc[:min_len]
                
                ax.plot(x_data, y_data, 
                       color=colors[i], 
                       linewidth=self.plot_style['line_width'],
                       label=label)
        
        # Formatting
        ax.set_xlabel(self._format_axis_label(x_column), fontsize=12)
        ax.set_ylabel(self._format_axis_label(y_column), fontsize=12)
        ax.set_title(f'{y_column} vs {x_column} Comparison ({len(dat_files)} files)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created custom overlay plot for {len(dat_files)} files: {y_column} vs {x_column}")
        return self.figure
    
    def embed_in_tkinter(self, parent_frame):
        """
        Embed the current figure in a Tkinter frame.
        
        Args:
            parent_frame: Tkinter frame to embed the plot
        """
        if self.figure is None:
            logger.warning("No figure to embed")
            return
        
        # Clear existing widgets (including placeholder)
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create canvas with CustomTkinter compatible styling
        self.canvas = FigureCanvasTkAgg(self.figure, parent_frame)
        self.canvas.draw()
        
        # Create toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent_frame)
        self.toolbar.update()
        
        # Pack widgets
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        logger.info("Plot embedded in Tkinter frame")
    
    def save_plot(self, filename: str, dpi: int = 300):
        """
        Save the current plot to a file.
        
        Args:
            filename: Output filename
            dpi: Resolution in DPI
        """
        if self.figure is None:
            raise ValueError("No figure to save")
        
        self.figure.savefig(filename, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
        logger.info(f"Plot saved to: {filename}")
    
    def clear_plot(self):
        """Clear the current plot."""
        if self.figure is not None:
            plt.close(self.figure)
            self.figure = None
            self.current_data = None
        
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        
        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None


class DATPlotDialog:
    """Dialog for selecting DAT plot type and parameters."""
    
    def __init__(self, parent, data: pd.DataFrame, metadata: Dict[str, Any]):
        """
        Initialize plot selection dialog.
        
        Args:
            parent: Parent window
            data: DAT DataFrame
            metadata: Metadata dictionary
        """
        self.parent = parent
        self.data = data
        self.metadata = metadata
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Create DAT Plot")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Get available columns for plotting
        self.numeric_columns = self._get_numeric_columns()
        
        self.create_widgets()
        self.center_dialog()
    
    def _get_numeric_columns(self):
        """Get list of numeric columns suitable for plotting."""
        numeric_cols = []
        for col in self.data.columns:
            if self.data[col].dtype in ['int64', 'float64'] and not self.data[col].isna().all():
                numeric_cols.append(col)
        return numeric_cols
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog, corner_radius=10)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="DAT Plot Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(20, 15))
        
        # Plot type selection
        plot_type_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        plot_type_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(plot_type_frame, text="Plot Type:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.plot_type = tk.StringVar(value="custom")
        
        plot_options = [
            ("Custom X-Y Plot", "custom"),
            ("Frequency vs Amplitude", "freq_amp"),
            ("Frequency vs Phase", "freq_phase"),
            ("Combined Freq vs Amp & Phase", "combined")
        ]
        
        for text, value in plot_options:
            radio_button = ctk.CTkRadioButton(
                plot_type_frame, 
                text=text, 
                variable=self.plot_type, 
                value=value,
                font=ctk.CTkFont(size=12),
                command=self._on_plot_type_change
            )
            radio_button.pack(anchor="w", padx=30, pady=2)
        
        # Axis selection frame
        self.axis_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        self.axis_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.axis_frame, text="Axis Configuration:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        # X-axis selection
        x_axis_frame = ctk.CTkFrame(self.axis_frame, corner_radius=6)
        x_axis_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(x_axis_frame, text="X-Axis:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=10)
        
        self.x_axis_var = tk.StringVar(value=self.numeric_columns[0] if self.numeric_columns else "")
        self.x_axis_combo = ctk.CTkComboBox(
            x_axis_frame, 
            variable=self.x_axis_var,
            values=self.numeric_columns,
            width=200,
            font=ctk.CTkFont(size=11)
        )
        self.x_axis_combo.pack(side="left", padx=10, pady=10)
        
        # Y-axis selection
        y_axis_frame = ctk.CTkFrame(self.axis_frame, corner_radius=6)
        y_axis_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(y_axis_frame, text="Y-Axis:", font=ctk.CTkFont(size=12)).pack(side="left", padx=10, pady=10)
        
        self.y_axis_var = tk.StringVar(value=self.numeric_columns[1] if len(self.numeric_columns) > 1 else (self.numeric_columns[0] if self.numeric_columns else ""))
        self.y_axis_combo = ctk.CTkComboBox(
            y_axis_frame, 
            variable=self.y_axis_var,
            values=self.numeric_columns,
            width=200,
            font=ctk.CTkFont(size=11)
        )
        self.y_axis_combo.pack(side="left", padx=10, pady=10)
        
        # Data info
        info_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_title = ctk.CTkLabel(info_frame, text="Data Information", font=ctk.CTkFont(size=14, weight="bold"))
        info_title.pack(pady=(10, 5))
        
        ctk.CTkLabel(info_frame, text=f"Data Points: {len(self.data)}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        ctk.CTkLabel(info_frame, text=f"Available Columns: {', '.join(self.numeric_columns)}", 
                    font=ctk.CTkFont(size=11), wraplength=400).pack(anchor="w", padx=10)
        
        if self.metadata.get('frequency_range_khz'):
            freq_range = self.metadata['frequency_range_khz']
            ctk.CTkLabel(info_frame, text=f"Frequency Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} kHz", 
                        font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        
        if self.metadata.get('has_average_data'):
            ctk.CTkLabel(info_frame, text="Average Data: Available", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0, 10))
        else:
            ctk.CTkLabel(info_frame, text="Average Data: Not Available", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, 
                                  height=35, corner_radius=8, fg_color=("gray70", "gray30"))
        cancel_btn.pack(side="right", padx=(5, 15), pady=15)
        
        create_btn = ctk.CTkButton(button_frame, text="Create Plot", command=self.create_plot, 
                                  height=35, corner_radius=8)
        create_btn.pack(side="right", padx=5, pady=15)
        
        # Initialize with default values
        self._on_plot_type_change()
    
    def _on_plot_type_change(self):
        """Handle plot type change to set appropriate default axis values."""
        plot_type = self.plot_type.get()
        
        if plot_type == "freq_amp":
            # Set frequency and amplitude as defaults
            if "Frequency_kHz" in self.numeric_columns:
                self.x_axis_var.set("Frequency_kHz")
            elif "Frequency_Hz" in self.numeric_columns:
                self.x_axis_var.set("Frequency_Hz")
            
            if "Amplitude" in self.numeric_columns:
                self.y_axis_var.set("Amplitude")
            elif "aveAmplitude" in self.numeric_columns:
                self.y_axis_var.set("aveAmplitude")
                
        elif plot_type == "freq_phase":
            # Set frequency and phase as defaults
            if "Frequency_kHz" in self.numeric_columns:
                self.x_axis_var.set("Frequency_kHz")
            elif "Frequency_Hz" in self.numeric_columns:
                self.x_axis_var.set("Frequency_Hz")
            
            if "Phase" in self.numeric_columns:
                self.y_axis_var.set("Phase")
            elif "avePhase" in self.numeric_columns:
                self.y_axis_var.set("avePhase")
        
        # Enable/disable axis selection based on plot type
        if plot_type == "custom":
            self.x_axis_combo.configure(state="normal")
            self.y_axis_combo.configure(state="normal")
        else:
            self.x_axis_combo.configure(state="readonly")
            self.y_axis_combo.configure(state="readonly")
    
    def center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_plot(self):
        """Create the selected plot type."""
        plot_type = self.plot_type.get()
        x_column = self.x_axis_var.get()
        y_column = self.y_axis_var.get()
        
        # Validate selections
        if not x_column or not y_column:
            messagebox.showerror("Error", "Please select both X and Y axis columns.")
            return
        
        if x_column not in self.data.columns or y_column not in self.data.columns:
            messagebox.showerror("Error", "Selected columns are not available in the data.")
            return
        
        # Store the result as a dictionary
        self.result = {
            'plot_type': plot_type,
            'x_axis': x_column,
            'y_axis': y_column
        }
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel plot creation."""
        self.result = None
        self.dialog.destroy()


# Factory functions
def create_dat_plotter(parent_widget=None) -> DATPlotter:
    """Create and return a DAT plotter instance."""
    return DATPlotter(parent_widget)


def show_dat_plot_dialog(parent, data: pd.DataFrame, metadata: Dict[str, Any]) -> Optional[str]:
    """
    Show DAT plot selection dialog.
    
    Returns:
        Selected plot type or None if cancelled
    """
    dialog = DATPlotDialog(parent, data, metadata)
    parent.wait_window(dialog.dialog)
    return dialog.result