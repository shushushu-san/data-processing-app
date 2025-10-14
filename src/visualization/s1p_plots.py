"""
S1P Data Visualization Module
Provides specialized plotting functions for S1P (single-port S-parameter) data.
"""

import matplotlib.pyplot as plt
import matplotlib.figure as mpl_figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class S1PPlotter:
    """
    Specialized plotting class for S1P network analyzer data.
    
    Provides various plot types commonly used for S-parameter analysis:
    - Magnitude vs Frequency
    - Phase vs Frequency  
    - Smith Chart
    - Polar Plot
    - Combined magnitude and phase plot
    """
    
    def __init__(self, parent_widget=None):
        """
        Initialize the S1P plotter.
        
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
            'magnitude': '#1f77b4',  # Blue
            'phase': '#ff7f0e',      # Orange
            'grid': '#cccccc',
            'text': '#333333'
        }
    
    def create_magnitude_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a magnitude vs frequency plot.
        
        Args:
            data: DataFrame with S1P data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Plot magnitude
        ax.plot(data['Frequency_GHz'], data['S11_Magnitude_dB'], 
               color=self.colors['magnitude'], 
               linewidth=self.plot_style['line_width'],
               label='S11 Magnitude')
        
        # Formatting
        ax.set_xlabel('Frequency (GHz)', fontsize=12)
        ax.set_ylabel('Magnitude (dB)', fontsize=12)
        ax.set_title('S11 Magnitude vs Frequency', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('instrument'):
            info_text += f"\nInstrument: {metadata['instrument']}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created S11 magnitude plot")
        return self.figure
    
    def create_phase_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a phase vs frequency plot.
        
        Args:
            data: DataFrame with S1P data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Plot phase
        ax.plot(data['Frequency_GHz'], data['S11_Phase_deg'], 
               color=self.colors['phase'], 
               linewidth=self.plot_style['line_width'],
               label='S11 Phase')
        
        # Formatting
        ax.set_xlabel('Frequency (GHz)', fontsize=12)
        ax.set_ylabel('Phase (degrees)', fontsize=12)
        ax.set_title('S11 Phase vs Frequency', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('instrument'):
            info_text += f"\nInstrument: {metadata['instrument']}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created S11 phase plot")
        return self.figure
    
    def create_combined_plot(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a combined magnitude and phase plot with dual y-axes.
        
        Args:
            data: DataFrame with S1P data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        
        # Plot magnitude on left axis
        line1 = ax1.plot(data['Frequency_GHz'], data['S11_Magnitude_dB'], 
                        color=self.colors['magnitude'], 
                        linewidth=self.plot_style['line_width'],
                        label='S11 Magnitude (dB)')
        
        # Plot phase on right axis  
        line2 = ax2.plot(data['Frequency_GHz'], data['S11_Phase_deg'], 
                        color=self.colors['phase'], 
                        linewidth=self.plot_style['line_width'],
                        label='S11 Phase (°)')
        
        # Formatting
        ax1.set_xlabel('Frequency (GHz)', fontsize=12)
        ax1.set_ylabel('Magnitude (dB)', fontsize=12, color=self.colors['magnitude'])
        ax2.set_ylabel('Phase (degrees)', fontsize=12, color=self.colors['phase'])
        ax1.set_title('S11 Magnitude and Phase vs Frequency', fontsize=14, fontweight='bold')
        
        ax1.grid(True, alpha=self.plot_style['grid_alpha'])
        ax1.tick_params(axis='y', labelcolor=self.colors['magnitude'])
        ax2.tick_params(axis='y', labelcolor=self.colors['phase'])
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right')
        
        # Add metadata info
        info_text = f"Points: {len(data)}"
        if metadata.get('instrument'):
            info_text += f"\nInstrument: {metadata['instrument']}"
        ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, 
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created combined S11 magnitude and phase plot")
        return self.figure
    
    def create_smith_chart(self, data: pd.DataFrame, metadata: Dict[str, Any]) -> mpl_figure.Figure:
        """
        Create a Smith chart representation of the S1P data.
        
        Args:
            data: DataFrame with S1P data
            metadata: Metadata dictionary
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=(8, 8), 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111, projection='polar')
        
        # Convert S11 to complex reflection coefficient
        mag_linear = data['S11_Magnitude_Linear']
        phase_rad = data['S11_Phase_rad']
        
        # Convert to real and imaginary parts
        real_part = mag_linear * np.cos(phase_rad)
        imag_part = mag_linear * np.sin(phase_rad)
        
        # Plot on Smith chart (simplified - actual Smith chart requires more complex transformation)
        ax.plot(phase_rad, mag_linear, 'b-', linewidth=self.plot_style['line_width'])
        ax.scatter(phase_rad[::len(data)//20], mag_linear[::len(data)//20], 
                  c=data['Frequency_GHz'][::len(data)//20], s=30, cmap='viridis')
        
        ax.set_title('S11 Polar Plot (Simplified Smith Chart)', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.grid(True)
        
        # Add colorbar for frequency
        cbar = plt.colorbar(ax.collections[0], ax=ax, pad=0.1, shrink=0.8)
        cbar.set_label('Frequency (GHz)', fontsize=10)
        
        self.figure.tight_layout()
        self.current_data = data
        
        logger.info("Created S11 polar/Smith chart plot")
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
        
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create canvas
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


class S1PPlotDialog:
    """Dialog for selecting S1P plot type and parameters."""
    
    def __init__(self, parent, data: pd.DataFrame, metadata: Dict[str, Any]):
        """
        Initialize plot selection dialog.
        
        Args:
            parent: Parent window
            data: S1P DataFrame
            metadata: Metadata dictionary
        """
        self.parent = parent
        self.data = data
        self.metadata = metadata
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create S1P Plot")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_dialog()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Plot type selection
        ttk.Label(main_frame, text="Select Plot Type:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        self.plot_type = tk.StringVar(value="magnitude")
        
        plot_options = [
            ("Magnitude vs Frequency", "magnitude"),
            ("Phase vs Frequency", "phase"), 
            ("Combined Mag & Phase", "combined"),
            ("Polar Plot (Smith Chart)", "smith")
        ]
        
        for text, value in plot_options:
            ttk.Radiobutton(main_frame, text=text, variable=self.plot_type, 
                           value=value).pack(anchor=tk.W, pady=2)
        
        # Data info
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        info_frame = ttk.LabelFrame(main_frame, text="Data Information")
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Data Points: {len(self.data)}").pack(anchor=tk.W, padx=5)
        
        freq_range = (self.data['Frequency_GHz'].min(), self.data['Frequency_GHz'].max())
        ttk.Label(info_frame, text=f"Frequency Range: {freq_range[0]:.3f} - {freq_range[1]:.3f} GHz").pack(anchor=tk.W, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Create Plot", command=self.create_plot).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
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
        self.result = self.plot_type.get()
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel plot creation."""
        self.result = None
        self.dialog.destroy()


# Factory functions
def create_s1p_plotter(parent_widget=None) -> S1PPlotter:
    """Create and return an S1P plotter instance."""
    return S1PPlotter(parent_widget)


def show_s1p_plot_dialog(parent, data: pd.DataFrame, metadata: Dict[str, Any]) -> Optional[str]:
    """
    Show S1P plot selection dialog.
    
    Returns:
        Selected plot type or None if cancelled
    """
    dialog = S1PPlotDialog(parent, data, metadata)
    parent.wait_window(dialog.dialog)
    return dialog.result