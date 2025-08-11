"""
SolidWorks PDM Plugin GUI
Simple tkinter interface for the plugin
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from datetime import datetime

from solidworks_connector import SolidWorksConnector
from api_client import PDMApiClient

class SolidWorksPDMGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SolidWorks PDM Plugin")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.sw_connector = SolidWorksConnector()
        self.api_client = PDMApiClient()
        
        # Variables
        self.projects = []
        self.assembly_info = None
        self.package_dir = ""
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Success.TButton', foreground='white', background='#10b981')
        style.configure('Warning.TButton', foreground='white', background='#f59e0b')
        style.configure('Danger.TButton', foreground='white', background='#ef4444')
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="SolidWorks PDM Plugin", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Connection Section
        self.create_connection_section(main_frame, 1)
        
        # Assembly Section
        self.create_assembly_section(main_frame, 2)
        
        # Project Section
        self.create_project_section(main_frame, 3)
        
        # Upload Section
        self.create_upload_section(main_frame, 4)
        
        # Log Section
        self.create_log_section(main_frame, 5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def create_connection_section(self, parent, row):
        """Create connection status section"""
        frame = ttk.LabelFrame(parent, text="Connection Status", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # SolidWorks connection
        ttk.Label(frame, text="SolidWorks:").grid(row=0, column=0, sticky=tk.W)
        self.sw_status_label = ttk.Label(frame, text="Not Connected", foreground="red")
        self.sw_status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        self.sw_connect_btn = ttk.Button(frame, text="Connect", command=self.connect_solidworks)
        self.sw_connect_btn.grid(row=0, column=2, padx=(10, 0))
        
        # API connection
        ttk.Label(frame, text="API:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.api_status_label = ttk.Label(frame, text="Not Connected", foreground="red")
        self.api_status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        self.api_connect_btn = ttk.Button(frame, text="Test API", command=self.test_api)
        self.api_connect_btn.grid(row=1, column=2, padx=(10, 0), pady=(5, 0))
    
    def create_assembly_section(self, parent, row):
        """Create assembly information section"""
        frame = ttk.LabelFrame(parent, text="Current Assembly", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.assembly_info_text = scrolledtext.ScrolledText(frame, height=8, width=70)
        self.assembly_info_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.scan_btn = ttk.Button(frame, text="Scan Active Assembly", 
                                  command=self.scan_assembly, style='Success.TButton')
        self.scan_btn.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)
        
        self.package_btn = ttk.Button(frame, text="Create Package", 
                                     command=self.create_package, state='disabled')
        self.package_btn.grid(row=1, column=1, pady=(10, 0), sticky=tk.E)
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
    def create_project_section(self, parent, row):
        """Create project selection section"""
        frame = ttk.LabelFrame(parent, text="Project Selection", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Project dropdown
        ttk.Label(frame, text="Select Project:").grid(row=0, column=0, sticky=tk.W)
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(frame, textvariable=self.project_var, 
                                         state="readonly", width=40)
        self.project_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        self.refresh_projects_btn = ttk.Button(frame, text="Refresh", 
                                              command=self.load_projects)
        self.refresh_projects_btn.grid(row=0, column=2, padx=(10, 0))
        
        # New project option
        ttk.Label(frame, text="Or create new:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.new_project_entry = ttk.Entry(frame, width=40)
        self.new_project_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        self.create_project_btn = ttk.Button(frame, text="Create", 
                                            command=self.create_new_project)
        self.create_project_btn.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        frame.columnconfigure(1, weight=1)
    
    def create_upload_section(self, parent, row):
        """Create upload section"""
        frame = ttk.LabelFrame(parent, text="Upload to PDM", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Commit message
        ttk.Label(frame, text="Commit Message:").grid(row=0, column=0, sticky=tk.W)
        self.commit_entry = ttk.Entry(frame, width=50)
        self.commit_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Author
        ttk.Label(frame, text="Author:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.author_entry = ttk.Entry(frame, width=50)
        self.author_entry.insert(0, os.getenv('USERNAME', 'SolidWorks User'))
        self.author_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        # Upload button
        self.upload_btn = ttk.Button(frame, text="Upload Assembly", 
                                    command=self.upload_assembly, 
                                    style='Success.TButton', state='disabled')
        self.upload_btn.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        frame.columnconfigure(1, weight=1)
    
    def create_log_section(self, parent, row):
        """Create log output section"""
        frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        clear_btn = ttk.Button(frame, text="Clear Log", command=self.clear_log)
        clear_btn.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
    
    def connect_solidworks(self):
        """Connect to SolidWorks"""
        def connect_thread():
            self.log_message("Attempting to connect to SolidWorks...")
            
            if self.sw_connector.connect():
                self.sw_status_label.config(text="Connected", foreground="green")
                self.sw_connect_btn.config(text="Disconnect", command=self.disconnect_solidworks)
                self.scan_btn.config(state='normal')
                self.log_message("✅ Connected to SolidWorks successfully")
            else:
                self.sw_status_label.config(text="Failed", foreground="red")
                self.log_message("❌ Failed to connect to SolidWorks")
                messagebox.showerror("Connection Error", 
                                   "Could not connect to SolidWorks.\nMake sure SolidWorks is running.")
        
        # Run in separate thread to prevent GUI freezing
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_solidworks(self):
        """Disconnect from SolidWorks"""
        self.sw_connector.disconnect()
        self.sw_status_label.config(text="Not Connected", foreground="red")
        self.sw_connect_btn.config(text="Connect", command=self.connect_solidworks)
        self.scan_btn.config(state='disabled')
        self.package_btn.config(state='disabled')
        self.log_message("🔌 Disconnected from SolidWorks")
    
    def test_api(self):
        """Test API connection"""
        def test_thread():
            self.log_message("Testing API connection...")
            
            if self.api_client.test_connection():
                self.api_status_label.config(text="Connected", foreground="green")
                self.log_message("✅ API connection successful")
                self.load_projects()
            else:
                self.api_status_label.config(text="Failed", foreground="red")
                self.log_message("❌ API connection failed")
                messagebox.showerror("API Error", 
                                   "Could not connect to PDM API.\nCheck your internet connection.")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def scan_assembly(self):
        """Scan the active SolidWorks assembly"""
        def scan_thread():
            self.log_message("Scanning active assembly...")
            
            if not self.sw_connector.connected:
                messagebox.showerror("Error", "Not connected to SolidWorks")
                return
            
            active_doc = self.sw_connector.get_active_document()
            if not active_doc:
                messagebox.showerror("Error", "No active document in SolidWorks")
                return
            
            # Check if it's an assembly
            doc_type = active_doc.GetType()
            if doc_type != 2:  # 2 = Assembly
                messagebox.showwarning("Warning", "Active document is not an assembly")
                return
            
            self.assembly_info = self.sw_connector.get_assembly_info(active_doc)
            
            if self.assembly_info:
                self.display_assembly_info()
                self.package_btn.config(state='normal')
                self.log_message(f"✅ Assembly scanned: {self.assembly_info['name']}")
            else:
                self.log_message("❌ Failed to scan assembly")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def display_assembly_info(self):
        """Display assembly information in the text widget"""
        if not self.assembly_info:
            return
        
        info_text = f"Assembly: {self.assembly_info['name']}\n"
        info_text += f"Path: {self.assembly_info['path']}\n"
        info_text += f"Dependencies: {len(self.assembly_info['dependencies'])}\n\n"
        
        info_text += "Files:\n"
        for dep in self.assembly_info['dependencies']:
            status = "✅" if dep['exists'] else "❌"
            info_text += f"  {status} {dep['name']} ({dep['size']} bytes)\n"
        
        self.assembly_info_text.delete(1.0, tk.END)
        self.assembly_info_text.insert(1.0, info_text)
    
    def create_package(self):
        """Create assembly package"""
        def package_thread():
            if not self.assembly_info:
                messagebox.showerror("Error", "No assembly information available")
                return
            
            self.log_message("Creating assembly package...")
            
            # Create package in temp directory
            temp_dir = os.path.join(os.path.expanduser("~"), "SolidWorksPDM", "packages")
            os.makedirs(temp_dir, exist_ok=True)
            
            self.package_dir = self.sw_connector.save_assembly_package(self.assembly_info, temp_dir)
            
            if self.package_dir:
                self.log_message(f"✅ Package created: {self.package_dir}")
                self.upload_btn.config(state='normal')
            else:
                self.log_message("❌ Failed to create package")
        
        threading.Thread(target=package_thread, daemon=True).start()
    
    def load_projects(self):
        """Load projects from API"""
        def load_thread():
            self.log_message("Loading projects...")
            
            self.projects = self.api_client.get_projects()
            
            if self.projects:
                project_names = [f"{p['name']} (ID: {p['id']})" for p in self.projects]
                self.project_combo['values'] = project_names
                
                if project_names:
                    self.project_combo.current(0)
                
                self.log_message(f"✅ Loaded {len(self.projects)} projects")
            else:
                self.project_combo['values'] = []
                self.log_message("No projects found")
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def create_new_project(self):
        """Create a new project"""
        def create_thread():
            project_name = self.new_project_entry.get().strip()
            if not project_name:
                messagebox.showerror("Error", "Please enter a project name")
                return
            
            self.log_message(f"Creating project: {project_name}")
            
            project = self.api_client.create_project(project_name, "Created from SolidWorks plugin")
            
            if project:
                self.new_project_entry.delete(0, tk.END)
                self.load_projects()  # Refresh project list
                self.log_message(f"✅ Project created: {project['name']}")
            else:
                self.log_message("❌ Failed to create project")
        
        threading.Thread(target=create_thread, daemon=True).start()
    
    def get_selected_project_id(self):
        """Get the ID of the selected project"""
        selection = self.project_var.get()
        if not selection:
            return None
        
        # Extract ID from the selection string
        try:
            # Format is "Name (ID: proj-1)"
            start = selection.rfind("ID: ") + 4
            end = selection.rfind(")")
            return selection[start:end]
        except:
            return None
    
    def upload_assembly(self):
        """Upload assembly to PDM"""
        def upload_thread():
            # Validate inputs
            project_id = self.get_selected_project_id()
            if not project_id:
                messagebox.showerror("Error", "Please select a project")
                return
            
            commit_message = self.commit_entry.get().strip()
            if not commit_message:
                messagebox.showerror("Error", "Please enter a commit message")
                return
            
            author = self.author_entry.get().strip()
            if not author:
                author = "SolidWorks User"
            
            if not self.package_dir or not os.path.exists(self.package_dir):
                messagebox.showerror("Error", "No package available. Please create package first.")
                return
            
            self.log_message(f"Uploading to project {project_id}...")
            self.upload_btn.config(state='disabled', text='Uploading...')
            
            try:
                result = self.api_client.upload_assembly(
                    project_id, 
                    self.assembly_info, 
                    self.package_dir, 
                    commit_message, 
                    author
                )
                
                if result:
                    self.log_message(f"✅ Upload successful: {result.get('id', 'Unknown')}")
                    messagebox.showinfo("Success", "Assembly uploaded successfully!")
                    
                    # Clear form
                    self.commit_entry.delete(0, tk.END)
                    self.assembly_info_text.delete(1.0, tk.END)
                    self.assembly_info = None
                    self.package_dir = ""
                    self.package_btn.config(state='disabled')
                else:
                    self.log_message("❌ Upload failed")
                    messagebox.showerror("Error", "Upload failed. Check the log for details.")
            
            finally:
                self.upload_btn.config(state='normal', text='Upload Assembly')
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def run(self):
        """Start the GUI application"""
        self.log_message("🚀 SolidWorks PDM Plugin started")
        self.log_message("1. Connect to SolidWorks")
        self.log_message("2. Test API connection")
        self.log_message("3. Open an assembly in SolidWorks")
        self.log_message("4. Scan assembly and create package")
        self.log_message("5. Select/create project and upload")
        
        # Auto-test API connection on startup
        self.test_api()
        
        self.root.mainloop()


# Main entry point
def main():
    """Main entry point for the plugin"""
    try:
        app = SolidWorksPDMGUI()
        app.run()
    except Exception as e:
        print(f"Error starting plugin: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()