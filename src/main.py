#!/usr/bin/env python3
"""
SNP Data Processing Application
Main entry point for the SNP file processing and graph creation application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
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
        self.root = tk.Tk()
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
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create the main application interface."""
        # Main container with paned window for resizable sections
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for file list and properties
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel for graph display and results
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        # Create left panel components
        self.create_file_panel(left_frame)
        
        # Create right panel components
        self.create_display_panel(right_frame)
    
    def create_file_panel(self, parent):
        """Create the file list and properties panel."""
        # File list section
        file_label = ttk.Label(parent, text="Loaded Files", font=('Arial', 12, 'bold'))
        file_label.pack(pady=(0, 5))
        
        # File listbox with scrollbar
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.SINGLE)
        file_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Properties section
        props_label = ttk.Label(parent, text="Properties", font=('Arial', 12, 'bold'))
        props_label.pack(pady=(10, 5))
        
        self.properties_text = tk.Text(parent, height=8, state=tk.DISABLED)
        props_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.properties_text.yview)
        self.properties_text.config(yscrollcommand=props_scrollbar.set)
        
        self.properties_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        props_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_display_panel(self, parent):
        """Create the graph display and results panel."""
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Graph display tab
        graph_frame = ttk.Frame(notebook)
        notebook.add(graph_frame, text="Graph Display")
        
        graph_label = ttk.Label(graph_frame, text="Graph visualization will appear here", 
                               font=('Arial', 14), foreground='gray')
        graph_label.pack(expand=True)
        
        # Analysis results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Analysis Results")
        
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, state=tk.DISABLED)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_event_handlers(self):
        """Setup event handlers for the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
    
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
        
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
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
                'loader': loader
            })
            
            self.logger.info(f"Loaded S1P file: {file_path.name}")
            
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def update_file_list(self):
        """Update the file listbox with loaded files."""
        self.file_listbox.delete(0, tk.END)
        
        for file_info in self.loaded_files:
            display_name = f"{file_info['name']} ({file_info['type']})"
            self.file_listbox.insert(tk.END, display_name)
    
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
        # Check if we have S1P data loaded
        s1p_files = [f for f in self.loaded_files if f['type'] == 'S1P']
        
        if s1p_files:
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
        
        # Get selected file or first S1P file
        selected_file = self.get_selected_file()
        if selected_file is None or selected_file['type'] != 'S1P':
            s1p_files = [f for f in self.loaded_files if f['type'] == 'S1P']
            if not s1p_files:
                messagebox.showwarning("No S1P Data", "No S1P files are currently loaded.")
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
        """Get the currently selected file from the listbox."""
        selection = self.file_listbox.curselection()
        if not selection:
            return None
        
        selected_index = selection[0]
        if selected_index < len(self.loaded_files):
            return self.loaded_files[selected_index]
        return None
    
    def find_graph_display_frame(self):
        """Find the graph display frame in the GUI."""
        # Navigate through the widget hierarchy to find the graph display area
        # This is a bit of a hack, but works for our current GUI structure
        def find_frame_with_text(widget, text):
            try:
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            for tab_id in child.tabs():
                                tab_text = child.tab(tab_id, 'text')
                                if tab_text == text:
                                    return child.nametowidget(tab_id)
                        result = find_frame_with_text(child, text)
                        if result:
                            return result
            except:
                pass
            return None
        
        return find_frame_with_text(self.root, "Graph Display")
    
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
