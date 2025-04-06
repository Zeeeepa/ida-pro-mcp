"""Project database for the projector application."""

import os
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any


class ProjectDatabase:
    """Project database for the projector application."""
    
    def __init__(self, db_file: str = "projects_db.json"):
        """
        Initialize the project database.
        
        Args:
            db_file: Path to the database file
        """
        self.db_file = db_file
        self.logger = logging.getLogger(__name__)
        self.projects = {}
        
        # Load existing projects if the database file exists
        if os.path.exists(db_file):
            try:
                with open(db_file, "r", encoding="utf-8") as f:
                    self.projects = json.load(f)
                self.logger.info(f"Loaded {len(self.projects)} projects from {db_file}")
            except Exception as e:
                self.logger.error(f"Error loading projects from {db_file}: {e}")
    
    def save(self) -> bool:
        """
        Save the projects to the database file.
        
        Returns:
            True if the save was successful, False otherwise
        """
        try:
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(self.projects, f, indent=2)
            self.logger.info(f"Saved {len(self.projects)} projects to {self.db_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving projects to {self.db_file}: {e}")
            return False
    
    def add_project(self, project_data: Dict[str, Any]) -> str:
        """
        Add a project to the database.
        
        Args:
            project_data: Project data
            
        Returns:
            Project ID
        """
        project_id = str(uuid.uuid4())
        project_data["id"] = project_id
        project_data["created_at"] = time.time()
        project_data["updated_at"] = time.time()
        
        self.projects[project_id] = project_data
        self.save()
        
        self.logger.info(f"Added project {project_id}: {project_data.get('name', 'Unnamed')}")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project from the database.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data, or None if not found
        """
        return self.projects.get(project_id)
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """
        Update a project in the database.
        
        Args:
            project_id: Project ID
            project_data: Project data
            
        Returns:
            True if the update was successful, False otherwise
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return False
        
        # Update the project data
        self.projects[project_id].update(project_data)
        self.projects[project_id]["updated_at"] = time.time()
        self.save()
        
        self.logger.info(f"Updated project {project_id}: {self.projects[project_id].get('name', 'Unnamed')}")
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project from the database.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return False
        
        # Delete the project
        project_name = self.projects[project_id].get("name", "Unnamed")
        del self.projects[project_id]
        self.save()
        
        self.logger.info(f"Deleted project {project_id}: {project_name}")
        return True
    
    def get_all_projects(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all projects from the database.
        
        Returns:
            Dictionary of project ID to project data
        """
        return self.projects
    
    def search_projects(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        Search for projects in the database.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of project ID to project data for matching projects
        """
        query = query.lower()
        results = {}
        
        for project_id, project_data in self.projects.items():
            # Search in name, description, and requirements
            name = project_data.get("name", "").lower()
            description = project_data.get("description", "").lower()
            requirements = project_data.get("requirements", "").lower()
            
            if query in name or query in description or query in requirements:
                results[project_id] = project_data
        
        return results