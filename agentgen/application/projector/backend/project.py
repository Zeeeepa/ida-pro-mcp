"""Project class for the projector application."""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any


class Project:
    """Project class for the projector application."""
    
    def __init__(
        self,
        project_id: str,
        name: str,
        git_url: str,
        slack_channel: str,
        requirements: str = "",
        plan: str = "",
        features: Optional[List[Dict[str, Any]]] = None,
        pull_requests: Optional[List[Dict[str, Any]]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        """
        Initialize a project.
        
        Args:
            project_id: Project ID
            name: Project name
            git_url: Git repository URL
            slack_channel: Slack channel for the project
            requirements: Project requirements
            plan: Project plan
            features: List of features
            pull_requests: List of pull requests
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.id = project_id
        self.name = name
        self.git_url = git_url
        self.slack_channel = slack_channel
        self.requirements = requirements
        self.plan = plan
        self.features = features or []
        self.pull_requests = pull_requests or []
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or time.time()
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """
        Create a project from a dictionary.
        
        Args:
            data: Project data
            
        Returns:
            A Project object
        """
        return cls(
            project_id=data.get("id", ""),
            name=data.get("name", ""),
            git_url=data.get("git_url", ""),
            slack_channel=data.get("slack_channel", ""),
            requirements=data.get("requirements", ""),
            plan=data.get("plan", ""),
            features=data.get("features", []),
            pull_requests=data.get("pull_requests", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the project to a dictionary.
        
        Returns:
            A dictionary representation of the project
        """
        return {
            "id": self.id,
            "name": self.name,
            "git_url": self.git_url,
            "slack_channel": self.slack_channel,
            "requirements": self.requirements,
            "plan": self.plan,
            "features": self.features,
            "pull_requests": self.pull_requests,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def add_feature(self, feature_name: str, description: str = "") -> Dict[str, Any]:
        """
        Add a feature to the project.
        
        Args:
            feature_name: Feature name
            description: Feature description
            
        Returns:
            The added feature
        """
        feature = {
            "id": len(self.features) + 1,
            "name": feature_name,
            "description": description,
            "status": "planned",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        self.features.append(feature)
        self.updated_at = time.time()
        
        self.logger.info(f"Added feature {feature['id']} to project {self.id}: {feature_name}")
        return feature
    
    def update_feature(self, feature_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a feature in the project.
        
        Args:
            feature_id: Feature ID
            data: Feature data
            
        Returns:
            The updated feature, or None if not found
        """
        for i, feature in enumerate(self.features):
            if feature.get("id") == feature_id:
                self.features[i].update(data)
                self.features[i]["updated_at"] = time.time()
                self.updated_at = time.time()
                
                self.logger.info(f"Updated feature {feature_id} in project {self.id}")
                return self.features[i]
        
        self.logger.warning(f"Feature {feature_id} not found in project {self.id}")
        return None
    
    def add_pull_request(self, pr_number: int, pr_url: str, feature_name: str, status: str = "open") -> Dict[str, Any]:
        """
        Add a pull request to the project.
        
        Args:
            pr_number: Pull request number
            pr_url: Pull request URL
            feature_name: Feature name
            status: Pull request status
            
        Returns:
            The added pull request
        """
        pull_request = {
            "number": pr_number,
            "url": pr_url,
            "feature_name": feature_name,
            "status": status,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        self.pull_requests.append(pull_request)
        self.updated_at = time.time()
        
        self.logger.info(f"Added pull request #{pr_number} to project {self.id}")
        return pull_request
    
    def update_pull_request(self, pr_number: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a pull request in the project.
        
        Args:
            pr_number: Pull request number
            data: Pull request data
            
        Returns:
            The updated pull request, or None if not found
        """
        for i, pr in enumerate(self.pull_requests):
            if pr.get("number") == pr_number:
                self.pull_requests[i].update(data)
                self.pull_requests[i]["updated_at"] = time.time()
                self.updated_at = time.time()
                
                self.logger.info(f"Updated pull request #{pr_number} in project {self.id}")
                return self.pull_requests[i]
        
        self.logger.warning(f"Pull request #{pr_number} not found in project {self.id}")
        return None