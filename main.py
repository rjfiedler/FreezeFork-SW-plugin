# app/main.py - Ultra Simple Version
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime

app = FastAPI(title="SolidWorks PDM API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data storage
projects_data = [
    {
        "id": "proj-1",
        "name": "Robotic Arm Assembly",
        "description": "6-DOF robotic arm for manufacturing automation",
        "lastModified": "2025-08-10T14:30:00Z",
        "branches": [
            {"id": "main", "name": "main", "commitCount": 8, "color": "#3b82f6"},
            {"id": "lightweight", "name": "lightweight", "commitCount": 2, "color": "#10b981"},
            {"id": "extended", "name": "extended", "commitCount": 2, "color": "#f59e0b"}
        ],
        "totalCommits": 12,
        "contributors": ["John Smith", "Sarah Johnson", "Mike Chen"]
    },
    {
        "id": "proj-2",
        "name": "Conveyor Belt System", 
        "description": "Automated conveyor system for warehouse operations",
        "lastModified": "2025-08-08T16:20:00Z",
        "branches": [
            {"id": "main", "name": "main", "commitCount": 15, "color": "#3b82f6"},
            {"id": "speed-optimization", "name": "speed-optimization", "commitCount": 4, "color": "#8b5cf6"}
        ],
        "totalCommits": 19,
        "contributors": ["Alice Brown", "Bob Wilson"]
    },
    {
        "id": "proj-3",
        "name": "Hydraulic Press Design",
        "description": "Industrial hydraulic press for metal forming", 
        "lastModified": "2025-08-05T11:45:00Z",
        "branches": [
            {"id": "main", "name": "main", "commitCount": 22, "color": "#3b82f6"}
        ],
        "totalCommits": 22,
        "contributors": ["Carol Davis", "David Lee", "Eva Martinez", "Frank Taylor"]
    }
]

commits_data = {
    "proj-1": [
        {
            "id": "commit-1",
            "message": "Initial robotic arm concept",
            "timestamp": "2025-08-01T09:00:00Z",
            "author": "John Smith",
            "branch": "main",
            "x": 50,
            "y": 50,
            "parents": []
        },
        {
            "id": "commit-2", 
            "message": "Added base plate design",
            "timestamp": "2025-08-02T11:30:00Z",
            "author": "Sarah Johnson", 
            "branch": "main",
            "x": 150,
            "y": 50,
            "parents": ["commit-1"]
        },
        {
            "id": "commit-3",
            "message": "Integrated motor mount system",
            "timestamp": "2025-08-03T14:15:00Z",
            "author": "Mike Chen",
            "branch": "main", 
            "x": 250,
            "y": 50,
            "parents": ["commit-2"]
        },
        {
            "id": "commit-4",
            "message": "Added arm segments with joints",
            "timestamp": "2025-08-04T16:45:00Z",
            "author": "John Smith",
            "branch": "main",
            "x": 350,
            "y": 50,
            "parents": ["commit-3"]
        },
        {
            "id": "commit-5",
            "message": "Lightweight materials exploration",
            "timestamp": "2025-08-05T10:20:00Z", 
            "author": "Sarah Johnson",
            "branch": "lightweight",
            "x": 450,
            "y": 120,
            "parents": ["commit-4"]
        },
        {
            "id": "commit-6",
            "message": "Extended reach prototype", 
            "timestamp": "2025-08-05T15:30:00Z",
            "author": "Mike Chen",
            "branch": "extended",
            "x": 450,
            "y": 180,
            "parents": ["commit-4"]
        },
        {
            "id": "commit-7",
            "message": "Optimized joint bearings",
            "timestamp": "2025-08-09T10:15:00Z",
            "author": "Sarah Johnson",
            "branch": "main",
            "x": 450,
            "y": 50,
            "parents": ["commit-4"]
        },
        {
            "id": "commit-8",
            "message": "Added gripper mechanism",
            "timestamp": "2025-08-10T14:30:00Z",
            "author": "John Smith", 
            "branch": "main",
            "x": 550,
            "y": 50,
            "parents": ["commit-7"]
        },
        {
            "id": "commit-9",
            "message": "Carbon fiber arm segments",
            "timestamp": "2025-08-11T09:00:00Z",
            "author": "Sarah Johnson", 
            "branch": "lightweight",
            "x": 550,
            "y": 120,
            "parents": ["commit-5"]
        },
        {
            "id": "commit-10",
            "message": "Extended base for stability",
            "timestamp": "2025-08-11T14:00:00Z",
            "author": "Mike Chen", 
            "branch": "extended",
            "x": 550,
            "y": 180,
            "parents": ["commit-6"]
        }
    ]
}

@app.get("/")
def root():
    return {"message": "SolidWorks PDM API", "status": "running"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "projects": len(projects_data)}

@app.get("/api/v1/projects")
def get_projects():
    return projects_data

@app.get("/api/v1/projects/{project_id}/commits")
def get_commits(project_id: str):
    return commits_data.get(project_id, [])

@app.post("/api/v1/projects")
def create_project(project: dict):
    new_project = {
        "id": f"proj-{len(projects_data) + 1}",
        "name": project.get("name", "New Project"),
        "description": project.get("description", ""),
        "lastModified": datetime.utcnow().isoformat(),
        "branches": [{"id": "main", "name": "main", "commitCount": 0, "color": "#3b82f6"}],
        "totalCommits": 0,
        "contributors": []
    }
    projects_data.append(new_project)
    return new_project