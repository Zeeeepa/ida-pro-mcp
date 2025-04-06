"""Project manager for the projector application."""

import os
import logging
import time
from typing import Dict, List, Optional, Any

from agentgen.application.projector.backend.project import Project
from agentgen.application.projector.backend.project_database import ProjectDatabase
from agentgen.application.projector.backend.github_manager import GitHubManager


class ProjectManager:
    """Project manager for the projector application."""
    
    def __init__(self, project_database: ProjectDatabase, github_manager: GitHubManager):
        """
        Initialize the project manager.
        
        Args:
            project_database: Project database
            github_manager: GitHub manager
        """
        self.project_database = project_database
        self.github_manager = github_manager
        self.logger = logging.getLogger(__name__)
        self.projects = {}
        
        # Load projects from the database
        self._load_projects()
    
    def _load_projects(self) -> None:
        """Load projects from the database."""
        db_projects = self.project_database.get_all_projects()
        
        for project_id, project_data in db_projects.items():
            self.projects[project_id] = Project.from_dict(project_data)
        
        self.logger.info(f"Loaded {len(self.projects)} projects from the database")
    
    def add_project(
        self,
        name: str,
        git_url: str,
        slack_channel: str,
        requirements: str = "",
        plan: str = ""
    ) -> str:
        """
        Add a project.
        
        Args:
            name: Project name
            git_url: Git repository URL
            slack_channel: Slack channel for the project
            requirements: Project requirements
            plan: Project plan
            
        Returns:
            Project ID
        """
        # Create a project data dictionary
        project_data = {
            "name": name,
            "git_url": git_url,
            "slack_channel": slack_channel,
            "requirements": requirements,
            "plan": plan
        }
        
        # Add the project to the database
        project_id = self.project_database.add_project(project_data)
        
        # Create a Project object
        self.projects[project_id] = Project.from_dict(self.project_database.get_project(project_id))
        
        self.logger.info(f"Added project {project_id}: {name}")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """
        Get a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project object, or None if not found
        """
        return self.projects.get(project_id)
    
    def update_project(self, project_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a project.
        
        Args:
            project_id: Project ID
            data: Project data
            
        Returns:
            True if the update was successful, False otherwise
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return False
        
        # Update the project in the database
        result = self.project_database.update_project(project_id, data)
        
        if result:
            # Update the Project object
            self.projects[project_id] = Project.from_dict(self.project_database.get_project(project_id))
            
            self.logger.info(f"Updated project {project_id}")
            return True
        
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return False
        
        # Delete the project from the database
        result = self.project_database.delete_project(project_id)
        
        if result:
            # Delete the Project object
            del self.projects[project_id]
            
            self.logger.info(f"Deleted project {project_id}")
            return True
        
        return False
    
    def get_all_projects(self) -> Dict[str, Project]:
        """
        Get all projects.
        
        Returns:
            Dictionary of project ID to Project object
        """
        return self.projects
    
    def search_projects(self, query: str) -> Dict[str, Project]:
        """
        Search for projects.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of project ID to Project object for matching projects
        """
        db_results = self.project_database.search_projects(query)
        
        results = {}
        for project_id in db_results:
            if project_id in self.projects:
                results[project_id] = self.projects[project_id]
        
        return results
    
    def add_feature(self, project_id: str, feature_name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """
        Add a feature to a project.
        
        Args:
            project_id: Project ID
            feature_name: Feature name
            description: Feature description
            
        Returns:
            The added feature, or None if the project was not found
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return None
        
        # Add the feature to the Project object
        feature = self.projects[project_id].add_feature(feature_name, description)
        
        # Update the project in the database
        self.project_database.update_project(project_id, self.projects[project_id].to_dict())
        
        self.logger.info(f"Added feature {feature['id']} to project {project_id}: {feature_name}")
        return feature
    
    def track_pr(
        self,
        project_id: str,
        pr_number: int,
        pr_url: str,
        feature_name: str,
        status: str = "open"
    ) -> Optional[Dict[str, Any]]:
        """
        Track a pull request for a project.
        
        Args:
            project_id: Project ID
            pr_number: Pull request number
            pr_url: Pull request URL
            feature_name: Feature name
            status: Pull request status
            
        Returns:
            The added pull request, or None if the project was not found
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return None
        
        # Add the pull request to the Project object
        pull_request = self.projects[project_id].add_pull_request(pr_number, pr_url, feature_name, status)
        
        # Update the project in the database
        self.project_database.update_project(project_id, self.projects[project_id].to_dict())
        
        self.logger.info(f"Added pull request #{pr_number} to project {project_id}")
        return pull_request
    
    def validate_pr_against_requirements(self, project_id: str, pr_number: int) -> Dict[str, Any]:
        """
        Validate a pull request against project requirements.
        
        Args:
            project_id: Project ID
            pr_number: Pull request number
            
        Returns:
            Validation results
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return {"error": f"Project {project_id} not found"}
        
        project = self.projects[project_id]
        
        # Get the pull request from GitHub
        repo_name = project.git_url.split("/")[-1].replace(".git", "")
        pr = self.github_manager.get_pull_request(pr_number, repo_name)
        
        if not pr:
            self.logger.warning(f"Pull request #{pr_number} not found in repository {repo_name}")
            return {"error": f"Pull request #{pr_number} not found in repository {repo_name}"}
        
        # This is a mock implementation
        # In a real implementation, this would use an AI agent to validate the PR against the requirements
        return {
            "pr_number": pr_number,
            "project_id": project_id,
            "meets_requirements": True,
            "missing_requirements": [],
            "additional_features": ["Added logging for better debugging"],
            "summary": "The PR meets all the specified requirements and adds some additional features."
        }
    
    def generate_progress_report(self, project_id: str) -> Dict[str, Any]:
        """
        Generate a progress report for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Progress report
        """
        if project_id not in self.projects:
            self.logger.warning(f"Project {project_id} not found")
            return {"error": f"Project {project_id} not found"}
        
        project = self.projects[project_id]
        
        # Count features by status
        feature_counts = {}
        for feature in project.features:
            status = feature.get("status", "unknown")
            feature_counts[status] = feature_counts.get(status, 0) + 1
        
        # Count pull requests by status
        pr_counts = {}
        for pr in project.pull_requests:
            status = pr.get("status", "unknown")
            pr_counts[status] = pr_counts.get(status, 0) + 1
        
        # This is a mock implementation
        # In a real implementation, this would use an AI agent to generate a more detailed report
        report = f"""
# Progress Report for {project.name}

## Summary
- Total features: {len(project.features)}
- Features by status: {feature_counts}
- Total pull requests: {len(project.pull_requests)}
- Pull requests by status: {pr_counts}

## Recent Activity
- Added feature: {project.features[-1]['name'] if project.features else 'None'}
- Latest pull request: {project.pull_requests[-1]['feature_name'] if project.pull_requests else 'None'}

## Next Steps
1. Continue implementing planned features
2. Review open pull requests
3. Update project documentation
"""
        
        return {
            "project_id": project_id,
            "report": report
        }