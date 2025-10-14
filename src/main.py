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
        self.supported_formats = ['.vcf', '.bed', '.ped', '.csv', '.txt']
        
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
        """Import SNP files into the application."""
        messagebox.showinfo("Import Files", "File import functionality will be implemented here.")
        self.logger.info("Import files requested")
    
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
        """Create a scatter plot."""
        messagebox.showinfo("Scatter Plot", "Scatter plot functionality will be implemented here.")
        self.logger.info("Scatter plot requested")
    
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
    
    def update_properties_panel(self, filename):
        """Update the properties panel with file information."""
        self.properties_text.config(state=tk.NORMAL)
        self.properties_text.delete(1.0, tk.END)
        self.properties_text.insert(tk.END, f"Selected File: {filename}\n")
        self.properties_text.insert(tk.END, "Properties will be displayed here once data loading is implemented.")
        self.properties_text.config(state=tk.DISABLED)
    
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
