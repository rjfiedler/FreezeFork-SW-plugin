"""
API Client for SolidWorks PDM Backend
Handles communication with the FastAPI backend
"""

import requests
import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime

class PDMApiClient:
    def __init__(self, base_url: str = "https://freezefork.onrender.com/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SolidWorks-PDM-Plugin/1.0'
        })
    
    def test_connection(self) -> bool:
        """Test if the API is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API connection successful")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def get_projects(self) -> List[Dict]:
        """Get all projects from the API"""
        try:
            response = self.session.get(f"{self.base_url}/projects")
            response.raise_for_status()
            projects = response.json()
            print(f"📋 Found {len(projects)} projects")
            return projects
        except Exception as e:
            print(f"❌ Error fetching projects: {e}")
            return []
    
    def create_project(self, name: str, description: str = "") -> Optional[Dict]:
        """Create a new project"""
        try:
            project_data = {
                "name": name,
                "description": description
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            project = response.json()
            print(f"✅ Created project: {project['name']} (ID: {project['id']})")
            return project
            
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return None
    
    def upload_assembly(self, project_id: str, assembly_info: Dict, 
                       package_dir: str, commit_message: str, 
                       author: str = "SolidWorks User") -> Optional[Dict]:
        """Upload assembly package as a new commit with real file upload"""
        try:
            print(f"📤 Starting upload to project {project_id}")
            print(f"📁 Package directory: {package_dir}")
            
            # Prepare files for upload
            files_to_upload = []
            
            # Get all CAD files from package directory
            for filename in os.listdir(package_dir):
                file_path = os.path.join(package_dir, filename)
                
                if os.path.isfile(file_path) and not filename.endswith('.json'):
                    # Only upload CAD files
                    if self._is_cad_file(filename):
                        files_to_upload.append((filename, file_path))
                        print(f"  📄 Preparing: {filename}")
            
            if not files_to_upload:
                print("❌ No CAD files found to upload")
                return None
            
            print(f"📦 Uploading {len(files_to_upload)} files...")
            
            # Prepare multipart form data
            files = []
            form_data = {
                'message': commit_message,
                'author': author,
                'branch': 'main'
            }
            
            try:
                # Open all files for upload
                file_handles = []
                for filename, file_path in files_to_upload:
                    file_handle = open(file_path, 'rb')
                    file_handles.append(file_handle)
                    files.append(('files', (filename, file_handle, 'application/octet-stream')))
                
                # Make the upload request (don't set Content-Type for multipart)
                response = self.session.post(
                    f"{self.base_url}/projects/{project_id}/commits",
                    data=form_data,
                    files=files,
                    timeout=300  # 5 minute timeout for large files
                )
                
                # Close all file handles
                for file_handle in file_handles:
                    file_handle.close()
                
                response.raise_for_status()
                result = response.json()
                
                print(f"✅ Upload completed successfully!")
                print(f"   Commit ID: {result['commit']['id']}")
                print(f"   Files uploaded: {result['files_uploaded']}")
                
                return result
                
            except requests.exceptions.Timeout:
                print("❌ Upload timed out - files may be too large")
                return None
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None:
                    print(f"❌ Upload failed with status {e.response.status_code}")
                    try:
                        error_detail = e.response.json()
                        print(f"   Error: {error_detail.get('detail', 'Unknown error')}")
                    except:
                        print(f"   Error: {e.response.text}")
                else:
                    print(f"❌ Upload failed: {e}")
                return None
            finally:
                # Ensure all file handles are closed
                for file_handle in file_handles:
                    try:
                        file_handle.close()
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Unexpected error during upload: {e}")
            return None
    
    def _is_cad_file(self, filename: str) -> bool:
        """Check if file is a CAD file that should be uploaded"""
        ext = os.path.splitext(filename)[1].lower()
        cad_extensions = {'.sldprt', '.sldasm', '.slddrw', '.step', '.stp', '.iges', '.igs'}
        return ext in cad_extensions
    
    def get_project_commits(self, project_id: str) -> List[Dict]:
        """Get commits for a project"""
        try:
            response = self.session.get(f"{self.base_url}/projects/{project_id}/commits")
            response.raise_for_status()
            commits = response.json()
            print(f"📋 Found {len(commits)} commits")
            return commits
            
        except Exception as e:
            print(f"❌ Error fetching commits: {e}")
            return []
    
    def download_commit_files(self, project_id: str, commit_id: str, download_dir: str) -> bool:
        """Download all files from a specific commit"""
        try:
            print(f"📥 Downloading files from commit {commit_id}")
            
            # Get commit info first
            commits = self.get_project_commits(project_id)
            commit = next((c for c in commits if c['id'] == commit_id), None)
            
            if not commit:
                print("❌ Commit not found")
                return False
            
            # Create download directory
            os.makedirs(download_dir, exist_ok=True)
            
            # Download each file
            downloaded_count = 0
            for file_info in commit.get('files', []):
                filename = file_info['name']
                download_url = f"{self.base_url}/projects/{project_id}/commits/{commit_id}/files/{filename}"
                
                try:
                    response = self.session.get(download_url, stream=True)
                    response.raise_for_status()
                    
                    file_path = os.path.join(download_dir, filename)
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"  ✅ Downloaded: {filename}")
                    downloaded_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Failed to download {filename}: {e}")
            
            print(f"✅ Downloaded {downloaded_count} files to {download_dir}")
            return downloaded_count > 0
            
        except Exception as e:
            print(f"❌ Error downloading commit files: {e}")
            return False
    
    def download_commit_archive(self, project_id: str, commit_id: str, download_path: str) -> bool:
        """Download entire commit as ZIP archive"""
        try:
            print(f"📦 Downloading commit archive: {commit_id}")
            
            download_url = f"{self.base_url}/projects/{project_id}/commits/{commit_id}/archive"
            
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Archive downloaded: {download_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading archive: {e}")
            return False
    
    def get_file_download_url(self, project_id: str, commit_id: str, filename: str) -> str:
        """Get download URL for a specific file"""
        return f"{self.base_url}/projects/{project_id}/commits/{commit_id}/files/{filename}"
    
    def upload_single_file(self, file_path: str) -> Optional[Dict]:
        """Upload a single file (for testing)"""
        try:
            filename = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                
                response = self.session.post(
                    f"{self.base_url}/files/upload",
                    files=files,
                    timeout=60
                )
                
                response.raise_for_status()
                result = response.json()
                print(f"✅ File uploaded: {result['id']}")
                return result
                
        except Exception as e:
            print(f"❌ Error uploading file {file_path}: {e}")
            return None
    
    def _process_package_files(self, package_dir: str) -> List[Dict]:
        """Process all files in the package directory (legacy method)"""
        files_info = []
        
        try:
            for filename in os.listdir(package_dir):
                file_path = os.path.join(package_dir, filename)
                
                if os.path.isfile(file_path) and not filename.endswith('.json'):
                    file_info = {
                        "name": filename,
                        "size": os.path.getsize(file_path),
                        "type": self._get_file_type(filename),
                        "hash": self._calculate_file_hash(file_path),
                        "path": file_path
                    }
                    files_info.append(file_info)
                    print(f"  📄 Processed: {filename} ({file_info['size']} bytes)")
            
            return files_info
            
        except Exception as e:
            print(f"❌ Error processing package files: {e}")
            return []
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = os.path.splitext(filename)[1].lower()
        
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
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for deduplication"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"❌ Error calculating hash for {file_path}: {e}")
            return ""


# Test functions
def test_api_connection():
    """Test API connection and basic operations"""
    client = PDMApiClient()
    
    print("🔍 Testing API connection...")
    if not client.test_connection():
        return
    
    print("\n📋 Testing project operations...")
    projects = client.get_projects()
    for project in projects:
        print(f"  📁 {project['name']} - {project['description']}")
    
    print("\n✅ API client test complete")

def test_upload_workflow(assembly_info: Dict, package_dir: str):
    """Test the complete upload workflow"""
    client = PDMApiClient()
    
    if not client.test_connection():
        return
    
    # Get or create project
    projects = client.get_projects()
    if projects:
        project = projects[0]  # Use first project
        print(f"📁 Using existing project: {project['name']}")
    else:
        project = client.create_project("Test Assembly Project", "Created by SolidWorks plugin")
        if not project:
            print("❌ Could not create project")
            return
    
    # Upload assembly
    commit_result = client.upload_assembly(
        project['id'],
        assembly_info,
        package_dir,
        "Assembly uploaded from SolidWorks plugin",
        "SolidWorks User"
    )
    
    if commit_result:
        print(f"✅ Upload completed: {commit_result}")
    else:
        print("❌ Upload failed")

if __name__ == "__main__":
    test_api_connection()