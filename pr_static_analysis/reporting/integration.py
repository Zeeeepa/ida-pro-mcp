"""
Integration module for PR static analysis reporting.

This module provides integration with the core analysis engine.
"""
import logging
from typing import List, Dict, Any, Optional

from .reporting import ReportingSystem
from .delivery import GitHubPRCommentDelivery, FileSystemDelivery, EmailDelivery
from .config import ReportingConfig

logger = logging.getLogger(__name__)


class AnalysisEngineIntegration:
    """Integration with the core analysis engine."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the integration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = ReportingConfig(config_path)
        self.reporting_system = ReportingSystem()
        self._configure_delivery_channels()
    
    def _configure_delivery_channels(self):
        """Configure delivery channels based on configuration."""
        # GitHub PR comment delivery
        if self.config.get('delivery.github_pr_comment.enabled', False):
            from ..github import GitHubClient  # Import here to avoid circular imports
            
            github_client = GitHubClient()
            self.reporting_system.add_delivery_channel(
                GitHubPRCommentDelivery(github_client)
            )
            logger.info("Added GitHub PR comment delivery channel")
        
        # File system delivery
        if self.config.get('delivery.file_system.enabled', False):
            output_dir = self.config.get('delivery.file_system.output_dir', 'reports')
            self.reporting_system.add_delivery_channel(
                FileSystemDelivery(output_dir)
            )
            logger.info(f"Added file system delivery channel with output directory: {output_dir}")
        
        # Email delivery
        if self.config.get('delivery.email.enabled', False):
            smtp_config = self.config.get('delivery.email.smtp', {})
            recipients = self.config.get('delivery.email.recipients', [])
            
            if smtp_config and recipients:
                self.reporting_system.add_delivery_channel(
                    EmailDelivery(smtp_config, recipients)
                )
                logger.info(f"Added email delivery channel with {len(recipients)} recipients")
    
    def process_analysis_results(self, results: list, pr_context: Any) -> Dict[str, Any]:
        """Process analysis results and generate a report.
        
        Args:
            results: List of analysis results
            pr_context: Context information about the PR
            
        Returns:
            Dict containing the report and delivery results
        """
        format_type = self.config.get('default_format', 'markdown')
        include_visualizations = self.config.get('include_visualizations', True)
        
        return self.reporting_system.process_results(
            results=results,
            pr_context=pr_context,
            format_type=format_type,
            include_visualizations=include_visualizations
        )


def create_integration(config_path: Optional[str] = None) -> AnalysisEngineIntegration:
    """Create an integration instance.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        AnalysisEngineIntegration instance
    """
    return AnalysisEngineIntegration(config_path)

