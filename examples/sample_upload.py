"""
SolidWorks COM Interface
Connects to SolidWorks and extracts assembly information
"""

import win32com.client
import os
import time
from typing import Dict, List, Optional, Tuple

class SolidWorksConnector:
    def __init__(self):
        self.sw_app = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to SolidWorks application"""
        try:
            # Try to connect to existing SolidWorks instance
            self.sw_app = win32com.client.Dispatch("SldWorks.Application")
            self.connected = True
            print("✅ Connected to SolidWorks")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to SolidWorks: {e}")
            print("💡 Make sure SolidWorks is running")
            return False
    
    def get_active_document(self) -> Optional[object]:
        """Get the currently active document"""
        if not self.connected:
            return None
            
        try:
            active_doc = self.sw_app.ActiveDoc
            if active_doc is None:
                print("⚠️  No active document in SolidWorks")
                return None
                
            doc_type = active_doc.GetType()
            type_names = {1: "Part", 2: "Assembly", 3: "Drawing"}
            print(f"📄 Active document type: {type_names.get(doc_type, 'Unknown')}")
            
            return active_doc
            
        except Exception as e:
            print(f"❌ Error getting active document: {e}")
            return None
    
    def get_assembly_info(self, doc) -> Dict:
        """Extract assembly information and file tree"""
        if doc is None:
            return {}
            
        try:
            # Get basic document info
            doc_path = doc.GetPathName()
            doc_title = doc.GetTitle()
            
            print(f"📂 Assembly: {doc_title}")
            print(f"📍 Path: {doc_path}")
            
            assembly_info = {
                "name": doc_title,
                "path": doc_path,
                "type": "assembly",
                "files": [],
                "dependencies": []
            }
            
            # Get all referenced documents
            dependencies = self.get_assembly_dependencies(doc)
            assembly_info["dependencies"] = dependencies
            
            # Build file tree
            file_tree = self.build_file_tree(doc, dependencies)
            assembly_info["files"] = file_tree
            
            return assembly_info
            
        except Exception as e:
            print(f"❌ Error extracting assembly info: {e}")
            return {}
    
    def get_assembly_dependencies(self, doc) -> List[Dict]:
        """Get all files referenced by the assembly"""
        dependencies = []
        
        try:
            # Get document dependencies
            dep_names = doc.GetDependencies2(True, True, False)
            
            if dep_names:
                for dep_path in dep_names:
                    if dep_path and os.path.exists(dep_path):
                        file_info = {
                            "path": dep_path,
                            "name": os.path.basename(dep_path),
                            "size": os.path.getsize(dep_path),
                            "type": self.get_file_type(dep_path),
                            "exists": True
                        }
                        dependencies.append(file_info)
                        print(f"  📎 Dependency: {file_info['name']}")
                    else:
                        # Handle missing files
                        file_info = {
                            "path": dep_path,
                            "name": os.path.basename(dep_path) if dep_path else "Unknown",
                            "size": 0,
                            "type": "missing",
                            "exists": False
                        }
                        dependencies.append(file_info)
                        print(f"  ❌ Missing: {file_info['name']}")
            
            print(f"📊 Found {len(dependencies)} dependencies")
            return dependencies
            
        except Exception as e:
            print(f"❌ Error getting dependencies: {e}")
            return []
    
    def build_file_tree(self, doc, dependencies: List[Dict]) -> List[Dict]:
        """Build hierarchical file tree structure"""
        try:
            # Start with main assembly
            main_path = doc.GetPathName()
            main_name = doc.GetTitle()
            
            file_tree = [{
                "name": main_name,
                "path": main_path,
                "type": "assembly",
                "size": os.path.getsize(main_path) if os.path.exists(main_path) else 0,
                "children": []
            }]
            
            # Add dependencies as children (simplified structure for now)
            for dep in dependencies:
                if dep["exists"]:
                    child = {
                        "name": dep["name"],
                        "path": dep["path"],
                        "type": dep["type"],
                        "size": dep["size"]
                    }
                    file_tree[0]["children"].append(child)
            
            return file_tree
            
        except Exception as e:
            print(f"❌ Error building file tree: {e}")
            return []
    
    def get_file_type(self, file_path: str) -> str:
        """Determine SolidWorks file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        type_map = {
            '.sldprt': 'part',
            '.sldasm': 'assembly', 
            '.slddrw': 'drawing',
            '.step': 'step',
            '.stp': 'step',
            '.iges': 'iges',
            '.igs': 'iges'
        }
        
        return type_map.get(ext, 'unknown')
    
    def save_assembly_package(self, assembly_info: Dict, output_dir: str) -> str:
        """Save assembly and all dependencies to a package directory"""
        try:
            # Create output directory
            package_name = f"package_{int(time.time())}"
            package_dir = os.path.join(output_dir, package_name)
            os.makedirs(package_dir, exist_ok=True)
            
            print(f"📦 Creating package: {package_dir}")
            
            # Copy main assembly
            main_path = assembly_info["path"]
            if main_path and os.path.exists(main_path):
                main_dest = os.path.join(package_dir, os.path.basename(main_path))
                self._copy_file(main_path, main_dest)
            
            # Copy all dependencies
            for dep in assembly_info["dependencies"]:
                if dep["exists"]:
                    src_path = dep["path"]
                    dest_path = os.path.join(package_dir, dep["name"])
                    self._copy_file(src_path, dest_path)
            
            # Save metadata
            import json
            metadata_path = os.path.join(package_dir, "assembly_info.json")
            with open(metadata_path, 'w') as f:
                json.dump(assembly_info, f, indent=2)
            
            print(f"✅ Package created successfully: {package_dir}")
            return package_dir
            
        except Exception as e:
            print(f"❌ Error creating package: {e}")
            return ""
    
    def _copy_file(self, src: str, dest: str):
        """Copy file with error handling"""
        try:
            import shutil
            shutil.copy2(src, dest)
            print(f"  📄 Copied: {os.path.basename(src)}")
        except Exception as e:
            print(f"  ❌ Failed to copy {src}: {e}")
    
    def disconnect(self):
        """Clean up connection"""
        self.sw_app = None
        self.connected = False
        print("🔌 Disconnected from SolidWorks")


# Test function
def test_connection():
    """Test the SolidWorks connection"""
    connector = SolidWorksConnector()
    
    if connector.connect():
        active_doc = connector.get_active_document()
        
        if active_doc:
            assembly_info = connector.get_assembly_info(active_doc)
            print("\n📋 Assembly Information:")
            print(f"Name: {assembly_info.get('name', 'N/A')}")
            print(f"Files: {len(assembly_info.get('dependencies', []))}")
            
            # Save package for testing
            if assembly_info:
                package_dir = connector.save_assembly_package(assembly_info, "C:\\temp")
                print(f"\n📦 Package saved to: {package_dir}")
        
        connector.disconnect()
    else:
        print("❌ Could not connect to SolidWorks")

if __name__ == "__main__":
    test_connection()