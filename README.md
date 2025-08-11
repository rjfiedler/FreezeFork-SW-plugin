# SolidWorks PDM Plugin

A Python plugin that connects SolidWorks to your PDM backend, enabling version control for CAD files similar to GitHub.

## 🚀 Quick Start

### Prerequisites
- **SolidWorks** installed and licensed
- **Python 3.7+** installed
- **Windows** operating system (required for SolidWorks COM interface)

### Installation

1. **Download the plugin files** to a folder (e.g., `C:\SolidWorksPDM\`)

2. **Install Python dependencies**:
```bash
pip install pywin32 requests
```

3. **Run the plugin**:
```bash
python main.py
```

## 🎮 How to Use

### Step 1: Start the Plugin
- Run `python main.py`
- The GUI will open with connection status

### Step 2: Connect to SolidWorks
- **Start SolidWorks** if not already running
- Click **"Connect"** in the plugin
- Status should show "Connected" in green

### Step 3: Test API Connection
- Click **"Test API"** button
- Should connect to https://freezefork.onrender.com
- Projects will load automatically

### Step 4: Prepare Assembly
- **Open an assembly** in SolidWorks
- Click **"Scan Active Assembly"** in plugin
- Review the file list and dependencies
- Click **"Create Package"** to bundle all files

### Step 5: Upload to PDM
- Select an existing project or create new one
- Enter a **commit message** (e.g., "Initial robotic arm design")
- Enter your **author name**
- Click **"Upload Assembly"**

## 📋 Features

### Current Features
✅ **SolidWorks COM Integration** - Direct connection to SolidWorks  
✅ **Assembly Scanning** - Extracts all referenced files  
✅ **File Packaging** - Bundles files with metadata  
✅ **API Integration** - Uploads to your PDM backend  
✅ **Project Management** - Create/select projects  
✅ **User-Friendly GUI** - Simple tkinter interface  

### Planned Features
🔄 **Real File Upload** - Binary file storage  
🔄 **Branch Management** - Create/switch branches  
🔄 **Conflict Resolution** - Handle file conflicts  
🔄 **Advanced Metadata** - Properties, materials, etc.  

## 🔧 Troubleshooting

### "Failed to connect to SolidWorks"
- Make sure SolidWorks is **running**
- Check if SolidWorks is **properly licensed**
- Try running as **Administrator**

### "API connection failed"
- Check **internet connection**
- Verify backend is running: https://freezefork.onrender.com/api/v1/health

### "No active document"
- **Open an assembly** in SolidWorks
- Make sure the document is **active** (clicked)
- Assembly must be **saved** (not just created)

### Import Errors
```bash
# Install missing packages
pip install pywin32 requests

# If pywin32 issues on Windows:
python -m pip install --upgrade pywin32
python Scripts/pywin32_postinstall.py -install
```

## 📁 File Structure

```
solidworks-plugin/
├── main.py                 # Entry point
├── gui.py                  # User interface
├── solidworks_connector.py # SolidWorks COM interface
├── api_client.py           # Backend API client
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🔗 Backend Integration

The plugin connects to your live backend API:
- **API Base URL**: https://freezefork.onrender.com/api/v1
- **Projects Endpoint**: `/projects`
- **Upload Endpoint**: `/projects/{id}/commits` (planned)
- **Health Check**: `/health`

## 💡 Tips

1. **Save your assembly** before scanning (unsaved files won't be detected)
2. **Keep files organized** - avoid scattered references
3. **Use descriptive commit messages** for better tracking
4. **Test with simple assemblies** first before complex ones

## 📞 Support

If you encounter issues:
1. Check the **Activity Log** in the plugin GUI
2. Ensure all **prerequisites** are met
3. Try with a **simple test assembly** first
4. Check **SolidWorks and API connections**

## 🎯 Next Steps

Once the basic plugin works:
- Add real file upload capability
- Implement branch management
- Add 3D preview generation
- Create SolidWorks add-in (instead of standalone tool)