#!/usr/bin/env python3
"""
SNP Data Processing Application
Main entry point for the SNP file processing and graph creation application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import logging
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import application modules (will be created later)
try:
    from utils.config import ConfigManager
    from utils.logger import setup_logger
except ImportError:
    # Fallback for initial development
    ConfigManager = None
    setup_logger = None

class SNPProcessorApp:
    """
    Main application class for SNP file processing and visualization.
    """
    
    def __init__(self):
        """Initialize the main application."""
        # Application metadata
        self.app_name = "SNP Data Processor"
        self.version = "1.0.0"
        self.supported_formats = ['.s1p', '.s2p', '.vcf', '.bed', '.ped', '.csv', '.txt']
        
        # Initialize CustomTkinter theme
        self.setup_customtkinter()
        
        # Initialize logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starting {self.app_name} v{self.version}")
        
        # Initialize configuration
        self.config = self.load_config()
        
        # Initialize GUI
        self.root = None
        self.main_window = None
        
        # Data storage
        self.loaded_files = []
        self.current_data = None
        self.analysis_results = {}
        
    def setup_customtkinter(self):
        """Setup CustomTkinter theme and appearance."""
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("system")  # Modes: "system" (standard), "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Custom color scheme (modern blue palette)
        self.colors = {
            'primary': '#1f538d',      # Deep blue
            'secondary': '#14b8a6',    # Teal
            'accent': '#8b5cf6',       # Purple
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Amber
            'error': '#ef4444',        # Red
            'text_primary': '#1f2937', # Dark gray
            'text_secondary': '#6b7280' # Medium gray
        }
    
    def setup_logging(self):
        """Setup application logging."""
        if setup_logger:
            setup_logger()
        else:
            # Basic logging setup
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('snp_processor.log'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
    
    def load_config(self):
        """Load application configuration."""
        if ConfigManager:
            return ConfigManager()
        else:
            # Default configuration
            return {
                'window_size': '1200x800',
                'theme': 'default',
                'recent_files': [],
                'export_format': 'png'
            }
    
    def create_main_window(self):
        """Create and configure the main application window."""
        self.root = ctk.CTk()
        self.root.title(f"{self.app_name} v{self.version}")
        
        # Set window size and position
        window_size = self.config.get('window_size', '1200x800') if isinstance(self.config, dict) else '1200x800'
        self.root.geometry(window_size)
        self.root.minsize(800, 600)
        
        # Center the window
        self.center_window()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main interface
        self.create_main_interface()
        
        # Set up event handlers
        self.setup_event_handlers()
        
        self.logger.info("Main window created successfully")
    
    def center_window(self):
        """Center the application window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import SNP Files...", command=self.import_files)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Load Project", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Basic Statistics", command=self.show_statistics)
        analysis_menu.add_command(label="PCA Analysis", command=self.run_pca)
        analysis_menu.add_command(label="Clustering", command=self.run_clustering)
        
        # Graph menu
        graph_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Graph", menu=graph_menu)
        graph_menu.add_command(label="Scatter Plot", command=self.create_scatter_plot)
        graph_menu.add_command(label="Histogram", command=self.create_histogram)
        graph_menu.add_command(label="Heatmap", command=self.create_heatmap)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light Mode", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Dark Mode", command=lambda: self.set_theme("dark"))
        theme_menu.add_command(label="System", command=lambda: self.set_theme("system"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create the main application interface."""
        # Main container with grid layout
        self.root.grid_columnconfigure(1, weight=3)  # Right panel gets more space
        self.root.grid_columnconfigure(0, weight=1)  # Left panel
        self.root.grid_rowconfigure(0, weight=1)
        
        # Left panel for file list and properties
        left_frame = ctk.CTkFrame(self.root, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Right panel for graph display and results
        right_frame = ctk.CTkFrame(self.root, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Create left panel components
        self.create_file_panel(left_frame)
        
        # Create right panel components
        self.create_display_panel(right_frame)
    
    def create_file_panel(self, parent):
        """Create the file list and properties panel."""
        # Configure grid for the parent frame
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)  # File list area
        parent.grid_rowconfigure(3, weight=1)  # Properties area
        
        # File list section
        file_label = ctk.CTkLabel(parent, text="Loaded Files", font=ctk.CTkFont(size=14, weight="bold"))
        file_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # File listbox (using CTkScrollableFrame as a container)
        self.file_frame = ctk.CTkScrollableFrame(parent, height=200)
        self.file_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        # Import button
        import_button = ctk.CTkButton(
            buttons_frame, 
            text="Import Files", 
            command=self.import_files,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        import_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            buttons_frame,
            text="🌙 Dark",
            command=self.toggle_theme,
            height=30,
            width=80,
            corner_radius=8,
            font=ctk.CTkFont(size=10),
            fg_color=("gray70", "gray30")
        )
        self.theme_button.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Properties section
        props_label = ctk.CTkLabel(parent, text="Properties", font=ctk.CTkFont(size=14, weight="bold"))
        props_label.grid(row=3, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # Properties text area
        self.properties_text = ctk.CTkTextbox(parent, height=200, state="disabled")
        self.properties_text.grid(row=4, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Store file list for management
        self.loaded_files_widgets = []
    
    def create_display_panel(self, parent):
        """Create the graph display and results panel."""
        # Configure grid for the parent frame
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Create tabview for tabbed interface
        self.tabview = ctk.CTkTabview(parent, corner_radius=10)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Graph display tab
        self.tabview.add("Graph Display")
        graph_tab = self.tabview.tab("Graph Display")
        graph_tab.grid_columnconfigure(0, weight=1)
        graph_tab.grid_rowconfigure(0, weight=1)
        
        # Placeholder for graph display
        self.graph_frame = ctk.CTkFrame(graph_tab, corner_radius=8)
        self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.graph_placeholder = ctk.CTkLabel(
            self.graph_frame, 
            text="Graph visualization will appear here", 
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        self.graph_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        # Analysis results tab
        self.tabview.add("Analysis Results")
        results_tab = self.tabview.tab("Analysis Results")
        results_tab.grid_columnconfigure(0, weight=1)
        results_tab.grid_rowconfigure(0, weight=1)
        
        # Results text area
        self.results_text = ctk.CTkTextbox(results_tab, state="disabled")
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def setup_event_handlers(self):
        """Setup event handlers for the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # Event handler methods (placeholder implementations)
    def import_files(self):
        """Import S1P and other data files into the application."""
        from tkinter import filedialog
        from data import S1PLoader, SUPPORTED_FORMATS
        
        # Create file type filters
        filetypes = []
        filetypes.append(('S1P Files', '*.s1p'))
        filetypes.append(('All Supported', ';'.join([f'*{ext}' for ext in SUPPORTED_FORMATS.keys()])))
        filetypes.append(('All Files', '*.*'))
        
        # Open file dialog
        file_paths = filedialog.askopenfilenames(
            title="Import Data Files",
            filetypes=filetypes,
            initialdir=str(Path.cwd() / 'data')  # Default to data directory
        )
        
        if not file_paths:
            return
        
        # Process selected files
        success_count = 0
        for file_path in file_paths:
            try:
                self.load_data_file(file_path)
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to load file {file_path}: {e}")
                messagebox.showerror("Import Error", f"Failed to load {Path(file_path).name}:\n{str(e)}")
        
        if success_count > 0:
            messagebox.showinfo("Import Complete", f"Successfully imported {success_count} file(s).")
            self.update_file_list()
        
        self.logger.info(f"Import completed: {success_count}/{len(file_paths)} files loaded")
    
    def load_data_file(self, file_path):
        """Load a single data file based on its extension."""
        from data import S1PLoader
        import os
        from datetime import datetime
        
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Get file stats
        file_stats = file_path.stat()
        file_size = f"{file_stats.st_size / 1024:.1f} KB" if file_stats.st_size < 1024*1024 else f"{file_stats.st_size / (1024*1024):.1f} MB"
        modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        if extension == '.s1p':
            loader = S1PLoader()
            data_dict = loader.load_file(str(file_path))
            
            # Store loaded data
            self.loaded_files.append({
                'path': str(file_path),
                'name': file_path.name,
                'type': 'S1P',
                'data': data_dict['data'],
                'metadata': data_dict['metadata'],
                'loader': loader,
                'size': file_size,
                'modified': modified_time
            })
            
            self.logger.info(f"Loaded S1P file: {file_path.name}")
            
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def update_file_list(self):
        """Update the file list with loaded files."""
        # Clear existing file widgets
        for widget in self.loaded_files_widgets:
            widget.destroy()
        self.loaded_files_widgets.clear()
        
        # Add new file widgets
        for i, file_info in enumerate(self.loaded_files):
            # Create file item frame
            file_item = ctk.CTkFrame(self.file_frame, corner_radius=8)
            file_item.pack(fill="x", padx=5, pady=2)
            
            # File name and type
            display_name = f"{file_info['name']} ({file_info['type']})"
            file_label = ctk.CTkLabel(
                file_item, 
                text=display_name, 
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            file_label.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            # Select button
            select_btn = ctk.CTkButton(
                file_item,
                text="Select",
                width=60,
                height=24,
                font=ctk.CTkFont(size=10),
                command=lambda idx=i: self.select_file(idx)
            )
            select_btn.pack(side="right", padx=(5, 10), pady=4)
            
            self.loaded_files_widgets.append(file_item)
    
    def select_file(self, index):
        """Select a file and update properties display."""
        if 0 <= index < len(self.loaded_files):
            file_info = self.loaded_files[index]
            
            # Update properties display
            self.properties_text.configure(state="normal")
            self.properties_text.delete("1.0", "end")
            
            # Build detailed properties text
            if file_info['type'] == 'S1P':
                properties_text = self._build_s1p_properties(file_info)
            else:
                properties_text = f"""File: {file_info['name']}
Type: {file_info['type']}
Path: {file_info['path']}
Size: {file_info.get('size', 'Unknown')}
Modified: {file_info.get('modified', 'Unknown')}

Data Info:
{file_info.get('info', 'No additional information available')}"""
            
            self.properties_text.insert("1.0", properties_text)
            self.properties_text.configure(state="disabled")
            
            # Store current selection
            self.current_data = file_info.get('data')
            
            self.logger.info(f"Selected file: {file_info['name']}")
    
    def _build_s1p_properties(self, file_info):
        """Build detailed properties text for S1P files."""
        properties_lines = []
        properties_lines.append(f"File: {file_info['name']}")
        properties_lines.append(f"Type: {file_info['type']}")
        properties_lines.append(f"Path: {file_info['path']}")
        properties_lines.append(f"Size: {file_info.get('size', 'Unknown')}")
        properties_lines.append(f"Modified: {file_info.get('modified', 'Unknown')}")
        properties_lines.append("")
        
        # S1P specific metadata
        metadata = file_info.get('metadata', {})
        properties_lines.append("=== S1P File Properties ===")
        properties_lines.append(f"Instrument: {metadata.get('instrument', 'Unknown')}")
        properties_lines.append(f"Frequency Unit: {metadata.get('frequency_unit', 'Hz')}")
        properties_lines.append(f"Parameter Format: {metadata.get('parameter_format', 'DB')}")
        properties_lines.append(f"Reference Impedance: {metadata.get('reference_impedance', 50)} Ω")
        properties_lines.append("")
        
        # Data summary
        data = file_info.get('data')
        if data is not None and not data.empty:
            properties_lines.append("=== Data Summary ===")
            properties_lines.append(f"Data Points: {len(data)}")
            
            if 'Frequency_GHz' in data.columns:
                freq_min, freq_max = data['Frequency_GHz'].min(), data['Frequency_GHz'].max()
                properties_lines.append(f"Frequency Range: {freq_min:.3f} - {freq_max:.3f} GHz")
            
            if 'S11_Magnitude_dB' in data.columns:
                mag_min, mag_max = data['S11_Magnitude_dB'].min(), data['S11_Magnitude_dB'].max()
                properties_lines.append(f"Magnitude Range: {mag_min:.2f} - {mag_max:.2f} dB")
            
            if 'S11_Phase_deg' in data.columns:
                phase_min, phase_max = data['S11_Phase_deg'].min(), data['S11_Phase_deg'].max()
                properties_lines.append(f"Phase Range: {phase_min:.1f} - {phase_max:.1f} °")
            
            # Frequency step calculation
            if 'Frequency_GHz' in data.columns and len(data) > 1:
                freq_step_ghz = (data['Frequency_GHz'].iloc[1] - data['Frequency_GHz'].iloc[0])
                freq_step_mhz = freq_step_ghz * 1000
                properties_lines.append(f"Frequency Step: {freq_step_mhz:.2f} MHz")
        else:
            properties_lines.append("=== Data Summary ===")
            properties_lines.append("No data available or data is empty")
        
        return "\n".join(properties_lines)
    
    def save_project(self):
        """Save current project state."""
        messagebox.showinfo("Save Project", "Save functionality will be implemented here.")
        self.logger.info("Save project requested")
    
    def load_project(self):
        """Load a saved project."""
        messagebox.showinfo("Load Project", "Load functionality will be implemented here.")
        self.logger.info("Load project requested")
    
    def show_statistics(self):
        """Show basic statistics for loaded data."""
        messagebox.showinfo("Statistics", "Statistics functionality will be implemented here.")
        self.logger.info("Statistics requested")
    
    def run_pca(self):
        """Run PCA analysis."""
        messagebox.showinfo("PCA Analysis", "PCA functionality will be implemented here.")
        self.logger.info("PCA analysis requested")
    
    def run_clustering(self):
        """Run clustering analysis."""
        messagebox.showinfo("Clustering", "Clustering functionality will be implemented here.")
        self.logger.info("Clustering analysis requested")
    
    def create_scatter_plot(self):
        """Create a scatter plot or S1P-specific plot."""
        self.logger.info("Scatter plot creation requested")
        
        # Check if we have S1P data loaded
        s1p_files = [f for f in self.loaded_files if f['type'] == 'S1P']
        self.logger.info(f"Found {len(s1p_files)} S1P files out of {len(self.loaded_files)} total files")
        
        if s1p_files:
            self.logger.info("Creating S1P plot")
            self.create_s1p_plot()
        else:
            messagebox.showinfo("Scatter Plot", "Generic scatter plot functionality will be implemented here.")
            self.logger.info("Generic scatter plot requested")
    
    def create_histogram(self):
        """Create a histogram."""
        messagebox.showinfo("Histogram", "Histogram functionality will be implemented here.")
        self.logger.info("Histogram requested")
    
    def create_heatmap(self):
        """Create a heatmap."""
        messagebox.showinfo("Heatmap", "Heatmap functionality will be implemented here.")
        self.logger.info("Heatmap requested")
    
    def on_file_select(self, event):
        """Handle file selection in the listbox."""
        selection = event.widget.curselection()
        if selection:
            filename = event.widget.get(selection[0])
            self.logger.info(f"File selected: {filename}")
            # Update properties panel (placeholder)
            self.update_properties_panel(filename)
    
    def update_properties_panel(self, display_name):
        """Update the properties panel with file information."""
        self.properties_text.config(state=tk.NORMAL)
        self.properties_text.delete(1.0, tk.END)
        
        # Find the corresponding file data
        selected_file = None
        for file_info in self.loaded_files:
            if f"{file_info['name']} ({file_info['type']})" == display_name:
                selected_file = file_info
                break
        
        if selected_file is None:
            self.properties_text.insert(tk.END, f"Selected: {display_name}\n")
            self.properties_text.insert(tk.END, "No data available.")
            self.properties_text.config(state=tk.DISABLED)
            return
        
        # Display file properties
        self.properties_text.insert(tk.END, f"File: {selected_file['name']}\n")
        self.properties_text.insert(tk.END, f"Type: {selected_file['type']}\n")
        self.properties_text.insert(tk.END, f"Path: {selected_file['path']}\n\n")
        
        # Display metadata
        metadata = selected_file['metadata']
        data = selected_file['data']
        
        if selected_file['type'] == 'S1P':
            self.properties_text.insert(tk.END, "=== S1P File Properties ===\n")
            self.properties_text.insert(tk.END, f"Instrument: {metadata.get('instrument', 'Unknown')}\n")
            self.properties_text.insert(tk.END, f"Frequency Unit: {metadata.get('frequency_unit', 'Hz')}\n")
            self.properties_text.insert(tk.END, f"Parameter Format: {metadata.get('parameter_format', 'DB')}\n")
            self.properties_text.insert(tk.END, f"Reference Impedance: {metadata.get('reference_impedance', 50)} Ω\n\n")
            
            if data is not None:
                summary = selected_file['loader'].get_summary_statistics()
                self.properties_text.insert(tk.END, "=== Data Summary ===\n")
                self.properties_text.insert(tk.END, f"Data Points: {summary.get('num_points', 0)}\n")
                
                freq_range = summary.get('frequency_range_ghz', (0, 0))
                self.properties_text.insert(tk.END, f"Frequency Range: {freq_range[0]:.3f} - {freq_range[1]:.3f} GHz\n")
                
                mag_range = summary.get('magnitude_range_db', (0, 0))
                self.properties_text.insert(tk.END, f"Magnitude Range: {mag_range[0]:.2f} - {mag_range[1]:.2f} dB\n")
                
                phase_range = summary.get('phase_range_deg', (0, 0))
                self.properties_text.insert(tk.END, f"Phase Range: {phase_range[0]:.1f} - {phase_range[1]:.1f} °\n")
                
                freq_step = summary.get('frequency_step_hz')
                if freq_step:
                    self.properties_text.insert(tk.END, f"Frequency Step: {freq_step/1e6:.2f} MHz\n")
        
        self.properties_text.config(state=tk.DISABLED)
    
    def create_s1p_plot(self):
        """Create S1P-specific plots."""
        from visualization import S1PPlotter, show_s1p_plot_dialog
        
        # Check if any files are loaded
        if not self.loaded_files:
            messagebox.showwarning("No Data", "Please import some files first.")
            return
        
        # Get selected file or first S1P file
        selected_file = self.get_selected_file()
        if selected_file is None or selected_file.get('type') != 'S1P':
            s1p_files = [f for f in self.loaded_files if f.get('type') == 'S1P']
            if not s1p_files:
                messagebox.showwarning("No S1P Data", "No S1P files are currently loaded. Please import S1P files first.")
                return
            selected_file = s1p_files[0]
        
        # Show plot selection dialog
        plot_type = show_s1p_plot_dialog(self.root, selected_file['data'], selected_file['metadata'])
        
        if plot_type is None:
            return  # User cancelled
        
        try:
            # Create plotter
            plotter = S1PPlotter()
            
            # Create the requested plot
            if plot_type == "magnitude":
                figure = plotter.create_magnitude_plot(selected_file['data'], selected_file['metadata'])
            elif plot_type == "phase":
                figure = plotter.create_phase_plot(selected_file['data'], selected_file['metadata'])
            elif plot_type == "combined":
                figure = plotter.create_combined_plot(selected_file['data'], selected_file['metadata'])
            elif plot_type == "smith":
                figure = plotter.create_smith_chart(selected_file['data'], selected_file['metadata'])
            else:
                messagebox.showerror("Error", f"Unknown plot type: {plot_type}")
                return
            
            # Embed in GUI (find the graph display area)
            graph_frame = self.find_graph_display_frame()
            if graph_frame:
                plotter.embed_in_tkinter(graph_frame)
            
            self.logger.info(f"Created S1P {plot_type} plot for {selected_file['name']}")
            
        except Exception as e:
            self.logger.error(f"Error creating S1P plot: {e}")
            messagebox.showerror("Plot Error", f"Failed to create plot:\n{str(e)}")
    
    def get_selected_file(self):
        """Get the currently selected file."""
        # Return the current data if available
        if hasattr(self, 'current_data') and self.current_data is not None:
            # Find the file info that matches the current data
            for file_info in self.loaded_files:
                if file_info.get('data') is self.current_data:
                    return file_info
        
        # If no current selection, return the first file if available
        if self.loaded_files:
            return self.loaded_files[0]
        
        return None
    
    def find_graph_display_frame(self):
        """Find the graph display frame in the GUI."""
        # For CustomTkinter, we can directly access the graph_frame
        if hasattr(self, 'graph_frame'):
            # Switch to Graph Display tab first
            if hasattr(self, 'tabview'):
                try:
                    self.tabview.set("Graph Display")
                except:
                    pass
            return self.graph_frame
        
        # Fallback: look for the tabview and get the graph display tab
        if hasattr(self, 'tabview'):
            try:
                # Switch to Graph Display tab and return its content frame
                self.tabview.set("Graph Display")
                return self.tabview.tab("Graph Display")
            except Exception as e:
                self.logger.error(f"Error accessing graph display tab: {e}")
        
        self.logger.warning("Could not find graph display frame")
        return None
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        {self.app_name}
        Version {self.version}
        
        A Windows application for processing SNP files 
        and creating visualizations for genomic data analysis.
        
        Supported formats: {', '.join(self.supported_formats)}
        """
        messagebox.showinfo("About", about_text)
    
    def set_theme(self, theme_mode):
        """Set the application theme."""
        try:
            ctk.set_appearance_mode(theme_mode)
            self.logger.info(f"Theme changed to: {theme_mode}")
            
            # Update theme button text
            if hasattr(self, 'theme_button'):
                if theme_mode == "dark":
                    self.theme_button.configure(text="☀️ Light")
                elif theme_mode == "light":
                    self.theme_button.configure(text="🌙 Dark")
                else:
                    self.theme_button.configure(text="🖥️ System")
            
        except Exception as e:
            self.logger.error(f"Error changing theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            self.set_theme("light")
        else:
            self.set_theme("dark")
    
    def on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.logger.info("Application closing")
            self.root.destroy()
    
    def run(self):
        """Start the application."""
        try:
            self.create_main_window()
            self.logger.info("Application started successfully")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error starting application: {e}")
            messagebox.showerror("Error", f"Failed to start application: {e}")
            sys.exit(1)


def main():
    """Main function to start the application."""
    try:
        app = SNPProcessorApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
