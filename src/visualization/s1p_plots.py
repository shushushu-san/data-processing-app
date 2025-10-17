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
from tkinter import ttk, messagebox
import customtkinter as ctk
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
    
    def create_magnitude_overlay_plot(self, s1p_files: list) -> mpl_figure.Figure:
        """
        Create an overlaid magnitude plot for multiple S1P files.
        
        Args:
            s1p_files: List of file info dictionaries with S1P data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(s1p_files)))
        
        # Plot each file
        for i, file_info in enumerate(s1p_files):
            data = file_info['data']
            label = file_info['name']
            
            ax.plot(data['Frequency_GHz'], data['S11_Magnitude_dB'], 
                   color=colors[i], 
                   linewidth=self.plot_style['line_width'],
                   label=label)
        
        # Formatting
        ax.set_xlabel('Frequency (GHz)', fontsize=12)
        ax.set_ylabel('Magnitude (dB)', fontsize=12)
        ax.set_title(f'S11 Magnitude Comparison ({len(s1p_files)} files)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created overlaid S11 magnitude plot for {len(s1p_files)} files")
        return self.figure
    
    def create_phase_overlay_plot(self, s1p_files: list) -> mpl_figure.Figure:
        """
        Create an overlaid phase plot for multiple S1P files.
        
        Args:
            s1p_files: List of file info dictionaries with S1P data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(s1p_files)))
        
        # Plot each file
        for i, file_info in enumerate(s1p_files):
            data = file_info['data']
            label = file_info['name']
            
            ax.plot(data['Frequency_GHz'], data['S11_Phase_deg'], 
                   color=colors[i], 
                   linewidth=self.plot_style['line_width'],
                   label=label)
        
        # Formatting
        ax.set_xlabel('Frequency (GHz)', fontsize=12)
        ax.set_ylabel('Phase (degrees)', fontsize=12)
        ax.set_title(f'S11 Phase Comparison ({len(s1p_files)} files)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created overlaid S11 phase plot for {len(s1p_files)} files")
        return self.figure
    
    def create_combined_overlay_plot(self, s1p_files: list) -> mpl_figure.Figure:
        """
        Create an overlaid combined plot for multiple S1P files with dual y-axes.
        
        Args:
            s1p_files: List of file info dictionaries with S1P data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=(12, 8), 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        # Create subplots for magnitude and phase
        ax1 = self.figure.add_subplot(211)  # Top subplot for magnitude
        ax2 = self.figure.add_subplot(212)  # Bottom subplot for phase
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(s1p_files)))
        
        # Plot magnitude for each file
        for i, file_info in enumerate(s1p_files):
            data = file_info['data']
            label = file_info['name']
            
            ax1.plot(data['Frequency_GHz'], data['S11_Magnitude_dB'], 
                    color=colors[i], linewidth=self.plot_style['line_width'], label=label)
            
            ax2.plot(data['Frequency_GHz'], data['S11_Phase_deg'], 
                    color=colors[i], linewidth=self.plot_style['line_width'], label=label)
        
        # Formatting for magnitude plot
        ax1.set_ylabel('Magnitude (dB)', fontsize=12)
        ax1.set_title(f'S11 Magnitude & Phase Comparison ({len(s1p_files)} files)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=self.plot_style['grid_alpha'])
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Formatting for phase plot
        ax2.set_xlabel('Frequency (GHz)', fontsize=12)
        ax2.set_ylabel('Phase (degrees)', fontsize=12)
        ax2.grid(True, alpha=self.plot_style['grid_alpha'])
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created combined overlay plot for {len(s1p_files)} files")
        return self.figure
    
    def create_smith_chart_overlay(self, s1p_files: list) -> mpl_figure.Figure:
        """
        Create an overlaid Smith chart for multiple S1P files.
        
        Args:
            s1p_files: List of file info dictionaries with S1P data
            
        Returns:
            matplotlib Figure object
        """
        self.figure = plt.figure(figsize=(10, 10), 
                                dpi=self.plot_style['dpi'],
                                facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111, projection='polar')
        
        # Color palette for multiple files
        colors = plt.cm.tab10(np.linspace(0, 1, len(s1p_files)))
        
        # Plot each file
        for i, file_info in enumerate(s1p_files):
            data = file_info['data']
            label = file_info['name']
            
            # Convert S11 to complex reflection coefficient
            mag_linear = data['S11_Magnitude_Linear']
            phase_rad = data['S11_Phase_rad']
            
            ax.plot(phase_rad, mag_linear, color=colors[i], 
                   linewidth=self.plot_style['line_width'], label=label)
            
            # Add some marker points for each file
            marker_indices = np.linspace(0, len(data)-1, min(10, len(data)), dtype=int)
            ax.scatter(phase_rad.iloc[marker_indices], mag_linear.iloc[marker_indices], 
                      c=[colors[i]], s=20, alpha=0.7)
        
        ax.set_title(f'S11 Polar Plot Comparison ({len(s1p_files)} files)', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.grid(True)
        ax.legend(bbox_to_anchor=(1.1, 1), loc='upper left')
        
        self.figure.tight_layout()
        
        logger.info(f"Created Smith chart overlay for {len(s1p_files)} files")
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
        
        # Add custom control buttons
        self._create_control_buttons(parent_frame)
        
        logger.info("Plot embedded in Tkinter frame")
    
    def _create_control_buttons(self, parent_frame):
        """Create custom control buttons below the plot."""
        button_frame = ctk.CTkFrame(parent_frame, corner_radius=8)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)
        
        # Graph size button
        size_button = ctk.CTkButton(
            button_frame, 
            text="グラフサイズ", 
            command=self._show_axis_range_dialog,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        size_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Graph info edit button
        info_button = ctk.CTkButton(
            button_frame, 
            text="グラフ情報編集", 
            command=self._show_graph_info_dialog,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        info_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _show_axis_range_dialog(self):
        """Show axis range setting dialog."""
        if self.figure is None:
            return
        
        dialog = AxisRangeDialog(self.canvas.get_tk_widget().winfo_toplevel(), self.figure)
        self.canvas.get_tk_widget().winfo_toplevel().wait_window(dialog.dialog)
        
        if dialog.result:
            self.canvas.draw()
    
    def _show_graph_info_dialog(self):
        """Show graph information editing dialog."""
        if self.figure is None:
            return
        
        dialog = GraphInfoDialog(self.canvas.get_tk_widget().winfo_toplevel(), self.figure)
        self.canvas.get_tk_widget().winfo_toplevel().wait_window(dialog.dialog)
        
        if dialog.result:
            self.canvas.draw()
    
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


class AxisRangeDialog:
    """Dialog for setting axis ranges."""
    
    def __init__(self, parent, figure):
        """
        Initialize axis range dialog.
        
        Args:
            parent: Parent window
            figure: Matplotlib figure object
        """
        self.parent = parent
        self.figure = figure
        self.result = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("グラフサイズ設定")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Get current axis limits
        self.axes = self.figure.get_axes()
        self.current_limits = {}
        for i, ax in enumerate(self.axes):
            self.current_limits[i] = {
                'xlim': ax.get_xlim(),
                'ylim': ax.get_ylim()
            }
        
        self.create_widgets()
        self.center_dialog()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="軸範囲設定", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(0, 15))
        
        # Create entry fields for each axis
        self.entries = {}
        
        for i, ax in enumerate(self.axes):
            if len(self.axes) > 1:
                frame_title = f"軸 {i+1}"
            else:
                frame_title = "軸設定"
            
            # Axis frame
            axis_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            axis_frame.pack(fill="x", pady=10, padx=10)
            
            # Frame title
            ctk.CTkLabel(axis_frame, text=frame_title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
            
            # X-axis range
            x_frame = ctk.CTkFrame(axis_frame, corner_radius=8)
            x_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(x_frame, text="X軸範囲:", width=80, anchor="w").pack(side="left", padx=(10, 5), pady=10)
            
            x_min_var = tk.StringVar(value=f"{self.current_limits[i]['xlim'][0]:.6f}")
            x_max_var = tk.StringVar(value=f"{self.current_limits[i]['xlim'][1]:.6f}")
            
            x_min_entry = ctk.CTkEntry(x_frame, textvariable=x_min_var, width=100)
            x_min_entry.pack(side="left", padx=2, pady=10)
            
            ctk.CTkLabel(x_frame, text="～", width=20).pack(side="left")
            
            x_max_entry = ctk.CTkEntry(x_frame, textvariable=x_max_var, width=100)
            x_max_entry.pack(side="left", padx=2, pady=10)
            
            # Y-axis range
            y_frame = ctk.CTkFrame(axis_frame, corner_radius=8)
            y_frame.pack(fill="x", padx=15, pady=(5, 15))
            
            ctk.CTkLabel(y_frame, text="Y軸範囲:", width=80, anchor="w").pack(side="left", padx=(10, 5), pady=10)
            
            y_min_var = tk.StringVar(value=f"{self.current_limits[i]['ylim'][0]:.6f}")
            y_max_var = tk.StringVar(value=f"{self.current_limits[i]['ylim'][1]:.6f}")
            
            y_min_entry = ctk.CTkEntry(y_frame, textvariable=y_min_var, width=100)
            y_min_entry.pack(side="left", padx=2, pady=10)
            
            ctk.CTkLabel(y_frame, text="～", width=20).pack(side="left")
            
            y_max_entry = ctk.CTkEntry(y_frame, textvariable=y_max_var, width=100)
            y_max_entry.pack(side="left", padx=2, pady=10)
            
            self.entries[i] = {
                'x_min': x_min_var,
                'x_max': x_max_var,
                'y_min': y_min_var,
                'y_max': y_max_var
            }
        
        # Auto-scale button
        auto_button = ctk.CTkButton(main_frame, text="自動調整", command=self.auto_scale, height=35, corner_radius=8)
        auto_button.pack(pady=15)
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        button_frame.pack(fill="x", pady=(10, 0), padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="キャンセル", command=self.cancel, 
                                  height=35, corner_radius=8, fg_color=("gray70", "gray30"))
        cancel_btn.pack(side="right", padx=(5, 15), pady=15)
        
        apply_btn = ctk.CTkButton(button_frame, text="適用", command=self.apply_changes, 
                                 height=35, corner_radius=8)
        apply_btn.pack(side="right", padx=5, pady=15)
    
    def center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def auto_scale(self):
        """Auto-scale all axes."""
        for ax in self.axes:
            ax.relim()
            ax.autoscale()
        
        # Update entry fields with new limits
        for i, ax in enumerate(self.axes):
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            
            self.entries[i]['x_min'].set(f"{xlim[0]:.6f}")
            self.entries[i]['x_max'].set(f"{xlim[1]:.6f}")
            self.entries[i]['y_min'].set(f"{ylim[0]:.6f}")
            self.entries[i]['y_max'].set(f"{ylim[1]:.6f}")
    
    def apply_changes(self):
        """Apply the axis range changes."""
        try:
            for i, ax in enumerate(self.axes):
                x_min = float(self.entries[i]['x_min'].get())
                x_max = float(self.entries[i]['x_max'].get())
                y_min = float(self.entries[i]['y_min'].get())
                y_max = float(self.entries[i]['y_max'].get())
                
                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError as e:
            tk.messagebox.showerror("エラー", f"無効な数値が入力されました: {e}")
    
    def cancel(self):
        """Cancel changes."""
        self.result = False
        self.dialog.destroy()


class GraphInfoDialog:
    """Dialog for editing graph information."""
    
    def __init__(self, parent, figure):
        """
        Initialize graph info dialog.
        
        Args:
            parent: Parent window
            figure: Matplotlib figure object
        """
        self.parent = parent
        self.figure = figure
        self.result = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("グラフ情報編集")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Get current graph information
        self.axes = self.figure.get_axes()
        self.current_info = {}
        for i, ax in enumerate(self.axes):
            self.current_info[i] = {
                'title': ax.get_title(),
                'xlabel': ax.get_xlabel(),
                'ylabel': ax.get_ylabel()
            }
        
        self.create_widgets()
        self.center_dialog()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=1)
        
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="グラフ情報編集", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(0, 15))
        
        # Create entry fields for each axis
        self.entries = {}
        
        for i, ax in enumerate(self.axes):
            if len(self.axes) > 1:
                frame_title = f"グラフ {i+1}"
            else:
                frame_title = "グラフ設定"
            
            # Axis frame
            axis_frame = ctk.CTkFrame(main_frame, corner_radius=10)
            axis_frame.pack(fill="x", pady=10, padx=10)
            
            # Frame title
            ctk.CTkLabel(axis_frame, text=frame_title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 10))
            
            # Title
            title_frame = ctk.CTkFrame(axis_frame, corner_radius=8)
            title_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(title_frame, text="タイトル:", width=90, anchor="w").pack(side="left", padx=(10, 5), pady=10)
            
            title_var = tk.StringVar(value=self.current_info[i]['title'])
            title_entry = ctk.CTkEntry(title_frame, textvariable=title_var, width=300)
            title_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)
            
            # X-axis label
            xlabel_frame = ctk.CTkFrame(axis_frame, corner_radius=8)
            xlabel_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(xlabel_frame, text="X軸ラベル:", width=90, anchor="w").pack(side="left", padx=(10, 5), pady=10)
            
            xlabel_var = tk.StringVar(value=self.current_info[i]['xlabel'])
            xlabel_entry = ctk.CTkEntry(xlabel_frame, textvariable=xlabel_var, width=300)
            xlabel_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)
            
            # Y-axis label
            ylabel_frame = ctk.CTkFrame(axis_frame, corner_radius=8)
            ylabel_frame.pack(fill="x", padx=15, pady=(5, 15))
            
            ctk.CTkLabel(ylabel_frame, text="Y軸ラベル:", width=90, anchor="w").pack(side="left", padx=(10, 5), pady=10)
            
            ylabel_var = tk.StringVar(value=self.current_info[i]['ylabel'])
            ylabel_entry = ctk.CTkEntry(ylabel_frame, textvariable=ylabel_var, width=300)
            ylabel_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)
            
            self.entries[i] = {
                'title': title_var,
                'xlabel': xlabel_var,
                'ylabel': ylabel_var
            }
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        button_frame.pack(fill="x", pady=(10, 0), padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="キャンセル", command=self.cancel, 
                                  height=35, corner_radius=8, fg_color=("gray70", "gray30"))
        cancel_btn.pack(side="right", padx=(5, 15), pady=15)
        
        apply_btn = ctk.CTkButton(button_frame, text="適用", command=self.apply_changes, 
                                 height=35, corner_radius=8)
        apply_btn.pack(side="right", padx=5, pady=15)
    
    def center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (width // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def apply_changes(self):
        """Apply the graph information changes."""
        try:
            for i, ax in enumerate(self.axes):
                title = self.entries[i]['title'].get()
                xlabel = self.entries[i]['xlabel'].get()
                ylabel = self.entries[i]['ylabel'].get()
                
                ax.set_title(title, fontsize=14, fontweight='bold')
                ax.set_xlabel(xlabel, fontsize=12)
                ax.set_ylabel(ylabel, fontsize=12)
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            tk.messagebox.showerror("エラー", f"設定の適用中にエラーが発生しました: {e}")
    
    def cancel(self):
        """Cancel changes."""
        self.result = False
        self.dialog.destroy()


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