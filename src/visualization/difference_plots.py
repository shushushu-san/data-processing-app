"""
Difference Plot Module
Provides functionality for calculating and plotting differences between datasets.
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
from scipy.interpolate import interp1d

logger = logging.getLogger(__name__)


class DifferencePlotter:
    """
    Specialized plotting class for calculating and plotting differences between datasets.
    
    Supports:
    - S1P file differences (magnitude and phase)
    - DAT file differences (custom X-Y data)
    - Interpolation for different frequency/X-axis ranges
    """
    
    def __init__(self, parent_widget=None):
        """
        Initialize the difference plotter.
        
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
            'figure_size': (12, 8),
            'dpi': 100,
            'facecolor': 'white',
            'grid': True,
            'grid_alpha': 0.3,
            'line_width': 2.0,
            'marker_size': 4
        }
        
        # Color scheme
        self.colors = {
            'difference': '#e74c3c',     # Red
            'original1': '#3498db',      # Blue
            'original2': '#2ecc71',      # Green
            'grid': '#cccccc',
            'text': '#333333'
        }
    
    def calculate_s1p_difference(self, file1_data: pd.DataFrame, file2_data: pd.DataFrame, 
                                file1_meta: Dict, file2_meta: Dict, 
                                difference_type: str = "magnitude") -> Tuple[pd.DataFrame, Dict]:
        """
        Calculate difference between two S1P datasets.
        
        Args:
            file1_data: First S1P dataset
            file2_data: Second S1P dataset
            file1_meta: Metadata for first file
            file2_meta: Metadata for second file
            difference_type: Type of difference ("magnitude", "phase", "both")
            
        Returns:
            Tuple of (difference_data, metadata)
        """
        # Get common frequency range
        freq1 = file1_data['Frequency_GHz'].values
        freq2 = file2_data['Frequency_GHz'].values
        
        # Define common frequency range (intersection)
        freq_min = max(freq1.min(), freq2.min())
        freq_max = min(freq1.max(), freq2.max())
        
        # Create common frequency array
        common_freq = np.linspace(freq_min, freq_max, 1001)
        
        # Interpolate both datasets to common frequency
        if difference_type in ["magnitude", "both"]:
            # Interpolate magnitude data
            interp1_mag = interp1d(freq1, file1_data['S11_Magnitude_dB'].values, 
                                 kind='linear', bounds_error=False, fill_value='extrapolate')
            interp2_mag = interp1d(freq2, file2_data['S11_Magnitude_dB'].values, 
                                 kind='linear', bounds_error=False, fill_value='extrapolate')
            
            mag1_interp = interp1_mag(common_freq)
            mag2_interp = interp2_mag(common_freq)
            mag_diff = mag1_interp - mag2_interp
        
        if difference_type in ["phase", "both"]:
            # Interpolate phase data
            interp1_phase = interp1d(freq1, file1_data['S11_Phase_deg'].values, 
                                   kind='linear', bounds_error=False, fill_value='extrapolate')
            interp2_phase = interp1d(freq2, file2_data['S11_Phase_deg'].values, 
                                   kind='linear', bounds_error=False, fill_value='extrapolate')
            
            phase1_interp = interp1_phase(common_freq)
            phase2_interp = interp2_phase(common_freq)
            phase_diff = phase1_interp - phase2_interp
            
            # Handle phase wrapping (normalize to -180 to +180)
            phase_diff = np.mod(phase_diff + 180, 360) - 180
        
        # Create result DataFrame
        result_data = pd.DataFrame({'Frequency_GHz': common_freq})
        
        if difference_type == "magnitude":
            result_data['Magnitude_Difference_dB'] = mag_diff
        elif difference_type == "phase":
            result_data['Phase_Difference_deg'] = phase_diff
        elif difference_type == "both":
            result_data['Magnitude_Difference_dB'] = mag_diff
            result_data['Phase_Difference_deg'] = phase_diff
        
        # Create metadata
        result_meta = {
            'difference_type': difference_type,
            'file1_name': file1_meta.get('filename', 'File 1'),
            'file2_name': file2_meta.get('filename', 'File 2'),
            'frequency_range': f"{freq_min:.3f} - {freq_max:.3f} GHz",
            'points': len(common_freq)
        }
        
        return result_data, result_meta
    
    def calculate_dat_difference(self, file1_data: pd.DataFrame, file2_data: pd.DataFrame,
                               file1_meta: Dict, file2_meta: Dict,
                               x_column: str, y_column: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Calculate difference between two DAT datasets.
        
        Args:
            file1_data: First DAT dataset
            file2_data: Second DAT dataset
            file1_meta: Metadata for first file
            file2_meta: Metadata for second file
            x_column: X-axis column name
            y_column: Y-axis column name
            
        Returns:
            Tuple of (difference_data, metadata)
        """
        # Get X-axis data
        x1 = file1_data[x_column].dropna().values
        x2 = file2_data[x_column].dropna().values
        y1 = file1_data[y_column].dropna().values
        y2 = file2_data[y_column].dropna().values
        
        # Define common X range (intersection)
        x_min = max(x1.min(), x2.min())
        x_max = min(x1.max(), x2.max())
        
        # Create common X array
        common_x = np.linspace(x_min, x_max, 1001)
        
        # Interpolate both datasets to common X
        interp1 = interp1d(x1, y1, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp2 = interp1d(x2, y2, kind='linear', bounds_error=False, fill_value='extrapolate')
        
        y1_interp = interp1(common_x)
        y2_interp = interp2(common_x)
        y_diff = y1_interp - y2_interp
        
        # Create result DataFrame
        result_data = pd.DataFrame({
            x_column: common_x,
            f'{y_column}_difference': y_diff
        })
        
        # Create metadata
        result_meta = {
            'x_column': x_column,
            'y_column': y_column,
            'file1_name': file1_meta.get('filename', 'File 1'),
            'file2_name': file2_meta.get('filename', 'File 2'),
            'x_range': f"{x_min:.3f} - {x_max:.3f}",
            'points': len(common_x)
        }
        
        return result_data, result_meta
    
    def create_s1p_difference_plot(self, file1_data: pd.DataFrame, file2_data: pd.DataFrame,
                                 file1_meta: Dict, file2_meta: Dict,
                                 difference_type: str = "magnitude") -> mpl_figure.Figure:
        """
        Create difference plot for S1P data.
        
        Args:
            file1_data: First S1P dataset
            file2_data: Second S1P dataset
            file1_meta: Metadata for first file
            file2_meta: Metadata for second file
            difference_type: Type of difference plot
            
        Returns:
            matplotlib Figure object
        """
        # Calculate difference
        diff_data, diff_meta = self.calculate_s1p_difference(
            file1_data, file2_data, file1_meta, file2_meta, difference_type
        )
        
        # Create figure
        if difference_type == "both":
            self.figure = plt.figure(figsize=(12, 10), dpi=self.plot_style['dpi'],
                                   facecolor=self.plot_style['facecolor'])
            
            # Magnitude difference subplot
            ax1 = self.figure.add_subplot(211)
            ax1.plot(diff_data['Frequency_GHz'], diff_data['Magnitude_Difference_dB'],
                    color=self.colors['difference'], linewidth=self.plot_style['line_width'],
                    label='Magnitude Difference')
            ax1.set_ylabel('Magnitude Difference (dB)', fontsize=12)
            ax1.set_title(f'S11 Difference: {file1_meta.get("filename", "File 1")} - {file2_meta.get("filename", "File 2")}',
                         fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=self.plot_style['grid_alpha'])
            ax1.legend()
            
            # Phase difference subplot
            ax2 = self.figure.add_subplot(212)
            ax2.plot(diff_data['Frequency_GHz'], diff_data['Phase_Difference_deg'],
                    color=self.colors['difference'], linewidth=self.plot_style['line_width'],
                    label='Phase Difference')
            ax2.set_xlabel('Frequency (GHz)', fontsize=12)
            ax2.set_ylabel('Phase Difference (degrees)', fontsize=12)
            ax2.grid(True, alpha=self.plot_style['grid_alpha'])
            ax2.legend()
            
        else:
            self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                                   dpi=self.plot_style['dpi'],
                                   facecolor=self.plot_style['facecolor'])
            
            ax = self.figure.add_subplot(111)
            
            if difference_type == "magnitude":
                ax.plot(diff_data['Frequency_GHz'], diff_data['Magnitude_Difference_dB'],
                       color=self.colors['difference'], linewidth=self.plot_style['line_width'],
                       label='Magnitude Difference')
                ax.set_ylabel('Magnitude Difference (dB)', fontsize=12)
                ax.set_title(f'S11 Magnitude Difference: {file1_meta.get("filename", "File 1")} - {file2_meta.get("filename", "File 2")}',
                           fontsize=14, fontweight='bold')
            
            elif difference_type == "phase":
                ax.plot(diff_data['Frequency_GHz'], diff_data['Phase_Difference_deg'],
                       color=self.colors['difference'], linewidth=self.plot_style['line_width'],
                       label='Phase Difference')
                ax.set_ylabel('Phase Difference (degrees)', fontsize=12)
                ax.set_title(f'S11 Phase Difference: {file1_meta.get("filename", "File 1")} - {file2_meta.get("filename", "File 2")}',
                           fontsize=14, fontweight='bold')
            
            ax.set_xlabel('Frequency (GHz)', fontsize=12)
            ax.grid(True, alpha=self.plot_style['grid_alpha'])
            ax.legend()
        
        # Add info text
        info_text = f"Points: {diff_meta['points']}\nRange: {diff_meta['frequency_range']}"
        ax_info = ax1 if difference_type == "both" else ax
        ax_info.text(0.02, 0.98, info_text, transform=ax_info.transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = diff_data
        
        logger.info(f"Created S1P {difference_type} difference plot")
        return self.figure
    
    def create_dat_difference_plot(self, file1_data: pd.DataFrame, file2_data: pd.DataFrame,
                                 file1_meta: Dict, file2_meta: Dict,
                                 x_column: str, y_column: str) -> mpl_figure.Figure:
        """
        Create difference plot for DAT data.
        
        Args:
            file1_data: First DAT dataset
            file2_data: Second DAT dataset
            file1_meta: Metadata for first file
            file2_meta: Metadata for second file
            x_column: X-axis column name
            y_column: Y-axis column name
            
        Returns:
            matplotlib Figure object
        """
        # Calculate difference
        diff_data, diff_meta = self.calculate_dat_difference(
            file1_data, file2_data, file1_meta, file2_meta, x_column, y_column
        )
        
        # Create figure
        self.figure = plt.figure(figsize=self.plot_style['figure_size'], 
                               dpi=self.plot_style['dpi'],
                               facecolor=self.plot_style['facecolor'])
        
        ax = self.figure.add_subplot(111)
        
        # Plot difference
        ax.plot(diff_data[x_column], diff_data[f'{y_column}_difference'],
               color=self.colors['difference'], linewidth=self.plot_style['line_width'],
               marker='o', markersize=self.plot_style['marker_size'],
               label=f'{y_column} Difference')
        
        # Formatting
        ax.set_xlabel(self._format_axis_label(x_column), fontsize=12)
        ax.set_ylabel(f'{self._format_axis_label(y_column)} Difference', fontsize=12)
        ax.set_title(f'{y_column} Difference: {file1_meta.get("filename", "File 1")} - {file2_meta.get("filename", "File 2")}',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=self.plot_style['grid_alpha'])
        ax.legend()
        
        # Add info text
        info_text = f"Points: {diff_meta['points']}\nRange: {diff_meta['x_range']}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.current_data = diff_data
        
        logger.info(f"Created DAT {y_column} difference plot")
        return self.figure
    
    def _format_axis_label(self, column_name: str) -> str:
        """Format column name for axis label."""
        # Common column name mappings
        label_mapping = {
            'Frequency_kHz': 'Frequency (kHz)',
            'Frequency_GHz': 'Frequency (GHz)',
            'Amplitude': 'Amplitude',
            'Phase': 'Phase (degrees)',
            'S11_Magnitude_dB': 'S11 Magnitude (dB)',
            'S11_Phase_deg': 'S11 Phase (degrees)'
        }
        
        return label_mapping.get(column_name, column_name.replace('_', ' ').title())
    
    def embed_in_tkinter(self, parent_frame):
        """Embed the plot in a Tkinter frame."""
        if self.figure is None:
            raise ValueError("No figure to embed")
        
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent_frame)
        self.toolbar.update()
        
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
        logger.info(f"Difference plot saved to: {filename}")
    
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


class DifferenceSelectionDialog:
    """Dialog for selecting files and parameters for difference calculation."""
    
    def __init__(self, parent, loaded_files: List[Dict]):
        """
        Initialize dialog.
        
        Args:
            parent: Parent window
            loaded_files: List of loaded file dictionaries
        """
        self.parent = parent
        self.loaded_files = loaded_files
        self.result = None
        
        # Filter files by type (case insensitive)
        self.s1p_files = [f for f in loaded_files if f.get('type', '').upper() == 'S1P']
        self.dat_files = [f for f in loaded_files if f.get('type', '').upper() == 'DAT']
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the dialog window."""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Calculate Difference Between Graphs")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create a scrollable area using Canvas + vertical Scrollbar
        container = ctk.CTkFrame(self.dialog, corner_radius=10)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas and scrollbar
        canvas = tk.Canvas(container, highlightthickness=0)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Inner frame that will contain all widgets
        inner_frame = ctk.CTkFrame(canvas, corner_radius=8)

        # Put the inner frame into the canvas
        inner_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Make sure the canvas scrollregion is updated when inner_frame size changes
        def _on_frame_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", _on_frame_config)

        # Allow mousewheel scrolling on the canvas (Windows/Mac/Linux handling)
        def _on_mousewheel(event):
            # For Windows and Mac delta values differ
            delta = 0
            if event.num == 5 or event.delta < 0:
                delta = 1
            elif event.num == 4 or event.delta > 0:
                delta = -1
            canvas.yview_scroll(delta, "units")

        # Bind both wheel types
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        # Title
        title_label = ctk.CTkLabel(inner_frame, text="Graph Difference Calculator", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(10, 8))

        # File type selection
        type_frame = ctk.CTkFrame(inner_frame, corner_radius=8)
        type_frame.pack(fill="x", padx=10, pady=(6, 12))

        ctk.CTkLabel(type_frame, text="File Type:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))

        self.file_type = ctk.StringVar(value="s1p")
        s1p_radio = ctk.CTkRadioButton(type_frame, text="S1P Files", variable=self.file_type, value="s1p", command=self.on_file_type_change)
        s1p_radio.pack(anchor="w", padx=12, pady=4)

        dat_radio = ctk.CTkRadioButton(type_frame, text="DAT Files", variable=self.file_type, value="dat", command=self.on_file_type_change)
        dat_radio.pack(anchor="w", padx=12, pady=4)

        # File selection frame
        self.file_selection_frame = ctk.CTkFrame(inner_frame, corner_radius=8)
        self.file_selection_frame.pack(fill="x", padx=10, pady=(4, 12))

        # Parameters frame
        self.params_frame = ctk.CTkFrame(inner_frame, corner_radius=8)
        self.params_frame.pack(fill="x", padx=10, pady=(4, 12))

        # Buttons frame (placed at bottom of inner frame)
        button_frame = ctk.CTkFrame(inner_frame, corner_radius=8)
        button_frame.pack(fill="x", padx=10, pady=(8, 12))

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, 
                                  height=35, corner_radius=8, fg_color=("gray70", "gray30"))
        cancel_btn.pack(side="right", padx=(5, 8), pady=8)

        create_btn = ctk.CTkButton(button_frame, text="Calculate Difference", command=self.calculate_difference, 
                                  height=35, corner_radius=8)
        create_btn.pack(side="right", padx=5, pady=8)

        # Initialize with default type
        self.on_file_type_change()
    
    def on_file_type_change(self):
        """Handle file type change."""
        # Clear existing widgets
        for widget in self.file_selection_frame.winfo_children():
            widget.destroy()
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        file_type = self.file_type.get()
        
        if file_type == "s1p":
            self.create_s1p_selection()
        else:
            self.create_dat_selection()
    
    def create_s1p_selection(self):
        """Create S1P file selection widgets."""
        ctk.CTkLabel(self.file_selection_frame, text="Select Files:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        if len(self.s1p_files) < 2:
            # Debug information
            debug_info = f"Found {len(self.s1p_files)} S1P files out of {len(self.loaded_files)} total files"
            for i, f in enumerate(self.loaded_files):
                debug_info += f"\nFile {i+1}: {f.get('name', 'Unknown')} - Type: {f.get('type', 'Unknown')}"
            
            ctk.CTkLabel(self.file_selection_frame, text=f"⚠️ Need at least 2 S1P files loaded\n\nDebug Info:\n{debug_info}", 
                        text_color="red", justify="left").pack(anchor="w", padx=20, pady=5)
            return
        
        # File 1 selection
        ctk.CTkLabel(self.file_selection_frame, text="File 1 (minuend):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.file1_var = ctk.StringVar(value=self.s1p_files[0]['name'])
        file1_combo = ctk.CTkComboBox(self.file_selection_frame, variable=self.file1_var,
                                     values=[f['name'] for f in self.s1p_files], width=400)
        file1_combo.pack(anchor="w", padx=20, pady=(0, 10))
        
        # File 2 selection
        ctk.CTkLabel(self.file_selection_frame, text="File 2 (subtrahend):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(5, 5))
        self.file2_var = ctk.StringVar(value=self.s1p_files[1]['name'] if len(self.s1p_files) > 1 else "")
        file2_combo = ctk.CTkComboBox(self.file_selection_frame, variable=self.file2_var,
                                     values=[f['name'] for f in self.s1p_files], width=400)
        file2_combo.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Difference type selection
        ctk.CTkLabel(self.params_frame, text="Difference Type:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.diff_type = ctk.StringVar(value="magnitude")
        
        mag_radio = ctk.CTkRadioButton(self.params_frame, text="Magnitude Only", 
                                      variable=self.diff_type, value="magnitude")
        mag_radio.pack(anchor="w", padx=20, pady=5)
        
        phase_radio = ctk.CTkRadioButton(self.params_frame, text="Phase Only", 
                                        variable=self.diff_type, value="phase")
        phase_radio.pack(anchor="w", padx=20, pady=5)
        
        both_radio = ctk.CTkRadioButton(self.params_frame, text="Both (Magnitude and Phase)", 
                                       variable=self.diff_type, value="both")
        both_radio.pack(anchor="w", padx=20, pady=(5, 15))
    
    def create_dat_selection(self):
        """Create DAT file selection widgets."""
        ctk.CTkLabel(self.file_selection_frame, text="Select Files:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        if len(self.dat_files) < 2:
            # Debug information
            debug_info = f"Found {len(self.dat_files)} DAT files out of {len(self.loaded_files)} total files"
            for i, f in enumerate(self.loaded_files):
                debug_info += f"\nFile {i+1}: {f.get('name', 'Unknown')} - Type: {f.get('type', 'Unknown')}"
            
            ctk.CTkLabel(self.file_selection_frame, text=f"⚠️ Need at least 2 DAT files loaded\n\nDebug Info:\n{debug_info}", 
                        text_color="red", justify="left").pack(anchor="w", padx=20, pady=5)
            return
        
        # File 1 selection
        ctk.CTkLabel(self.file_selection_frame, text="File 1 (minuend):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.file1_var = ctk.StringVar(value=self.dat_files[0]['name'])
        file1_combo = ctk.CTkComboBox(self.file_selection_frame, variable=self.file1_var,
                                     values=[f['name'] for f in self.dat_files], width=400)
        file1_combo.pack(anchor="w", padx=20, pady=(0, 10))
        
        # File 2 selection
        ctk.CTkLabel(self.file_selection_frame, text="File 2 (subtrahend):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(5, 5))
        self.file2_var = ctk.StringVar(value=self.dat_files[1]['name'] if len(self.dat_files) > 1 else "")
        file2_combo = ctk.CTkComboBox(self.file_selection_frame, variable=self.file2_var,
                                     values=[f['name'] for f in self.dat_files], width=400)
        file2_combo.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Axis selection
        if self.dat_files:
            sample_data = self.dat_files[0]['data']
            available_columns = [col for col in sample_data.columns if sample_data[col].dtype in ['float64', 'int64']]
            
            ctk.CTkLabel(self.params_frame, text="Axis Selection:", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
            
            # X-axis selection
            ctk.CTkLabel(self.params_frame, text="X-axis:", 
                        font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(10, 5))
            self.x_axis_var = ctk.StringVar(value=available_columns[0] if available_columns else "")
            x_combo = ctk.CTkComboBox(self.params_frame, variable=self.x_axis_var,
                                     values=available_columns, width=350)
            x_combo.pack(anchor="w", padx=20, pady=(0, 10))
            
            # Y-axis selection
            ctk.CTkLabel(self.params_frame, text="Y-axis:", 
                        font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(5, 5))
            self.y_axis_var = ctk.StringVar(value=available_columns[1] if len(available_columns) > 1 else "")
            y_combo = ctk.CTkComboBox(self.params_frame, variable=self.y_axis_var,
                                     values=available_columns, width=350)
            y_combo.pack(anchor="w", padx=20, pady=(0, 15))
    
    def calculate_difference(self):
        """Calculate the difference and close dialog."""
        file_type = self.file_type.get()
        
        # Validate selections
        if not hasattr(self, 'file1_var') or not self.file1_var.get():
            messagebox.showerror("Error", "Please select File 1.")
            return
        
        if not hasattr(self, 'file2_var') or not self.file2_var.get():
            messagebox.showerror("Error", "Please select File 2.")
            return
        
        if self.file1_var.get() == self.file2_var.get():
            messagebox.showerror("Error", "Please select different files.")
            return
        
        # Find selected files
        files = self.s1p_files if file_type == "s1p" else self.dat_files
        file1 = next((f for f in files if f['name'] == self.file1_var.get()), None)
        file2 = next((f for f in files if f['name'] == self.file2_var.get()), None)
        
        if not file1 or not file2:
            messagebox.showerror("Error", "Selected files not found.")
            return
        
        # Prepare result
        self.result = {
            'file_type': file_type,
            'file1': file1,
            'file2': file2
        }
        
        if file_type == "s1p":
            self.result['difference_type'] = self.diff_type.get()
        else:
            if not hasattr(self, 'x_axis_var') or not self.x_axis_var.get():
                messagebox.showerror("Error", "Please select X-axis.")
                return
            if not hasattr(self, 'y_axis_var') or not self.y_axis_var.get():
                messagebox.showerror("Error", "Please select Y-axis.")
                return
            
            self.result['x_column'] = self.x_axis_var.get()
            self.result['y_column'] = self.y_axis_var.get()
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel difference calculation."""
        self.result = None
        self.dialog.destroy()


# Factory function
def show_difference_dialog(parent, loaded_files: List[Dict]) -> Optional[Dict]:
    """
    Show difference calculation dialog.
    
    Args:
        parent: Parent window
        loaded_files: List of loaded file dictionaries
        
    Returns:
        Difference configuration or None if cancelled
    """
    dialog = DifferenceSelectionDialog(parent, loaded_files)
    parent.wait_window(dialog.dialog)
    return dialog.result