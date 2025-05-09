"""
PR analyzer for static analysis.

This module provides the PRAnalyzer class that orchestrates the analysis process.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import json

from .analysis_context import PRAnalysisContext, FileChange, AnalysisResult
from .rule_engine import RuleEngine
from ..utils.config_utils import Config, load_config

logger = logging.getLogger(__name__)


class PRAnalyzer:
    """
    Analyzer for pull requests.
    
    This class orchestrates the analysis process, including:
    - Loading PR data
    - Running analysis rules
    - Generating reports
    - Providing hooks for plugins and extensions
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize a new PR analyzer.
        
        Args:
            config_path: Optional path to a configuration file
        """
        self.rule_engine = RuleEngine()
        self.config = load_config(config_path) if config_path else Config()
        self.hooks: Dict[str, List[Callable]] = {
            "pre_analysis": [],
            "post_analysis": [],
            "pre_rule": [],
            "post_rule": [],
            "pre_report": [],
            "post_report": [],
        }
        
        # Initialize rule engine with rules from configuration
        self._initialize_rule_engine()
        
    def _initialize_rule_engine(self) -> None:
        """Initialize the rule engine with rules from configuration."""
        # Register built-in rules
        self.rule_engine.discover_and_register_rules()
        
        # Register custom rules from configuration
        custom_rule_paths = self.config.get("custom_rule_paths", [])
        for path in custom_rule_paths:
            if os.path.isdir(path):
                # If it's a directory, try to import it as a package
                package_name = os.path.basename(path)
                if os.path.exists(os.path.join(path, "__init__.py")):
                    self.rule_engine.discover_and_register_rules(package_name)
            elif os.path.isfile(path) and path.endswith(".py"):
                # If it's a file, try to import it as a module
                module_name = os.path.splitext(os.path.basename(path))[0]
                self.rule_engine.register_rules_from_module(module_name)
                
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback.
        
        Args:
            hook_name: The name of the hook to register for
            callback: The callback function
        """
        if hook_name not in self.hooks:
            logger.warning(f"Unknown hook name: {hook_name}")
            return
            
        self.hooks[hook_name].append(callback)
        
    def _run_hooks(self, hook_name: str, *args, **kwargs) -> None:
        """
        Run all callbacks for a hook.
        
        Args:
            hook_name: The name of the hook to run
            *args: Arguments to pass to the callbacks
            **kwargs: Keyword arguments to pass to the callbacks
        """
        for callback in self.hooks.get(hook_name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error running hook {hook_name}: {e}")
                
    def create_context(self, pr_id: str, repo_name: str, 
                      base_branch: str, head_branch: str) -> PRAnalysisContext:
        """
        Create a new analysis context.
        
        Args:
            pr_id: The ID of the PR
            repo_name: The name of the repository
            base_branch: The base branch of the PR
            head_branch: The head branch of the PR
            
        Returns:
            A new PRAnalysisContext
        """
        return PRAnalysisContext(pr_id, repo_name, base_branch, head_branch)
        
    def add_file_changes(self, context: PRAnalysisContext, 
                        file_changes: List[Dict[str, Any]]) -> None:
        """
        Add file changes to the context.
        
        Args:
            context: The analysis context
            file_changes: A list of file change dictionaries
        """
        for fc in file_changes:
            file_change = FileChange(
                filename=fc["filename"],
                status=fc["status"],
                patch=fc.get("patch"),
                changed_lines=fc.get("changed_lines", []),
            )
            context.add_file_change(file_change)
            
    def analyze(self, context: PRAnalysisContext, 
               categories: Optional[Set[str]] = None) -> List[AnalysisResult]:
        """
        Analyze a PR.
        
        Args:
            context: The analysis context
            categories: Optional set of rule categories to run
            
        Returns:
            A list of analysis results
        """
        self._run_hooks("pre_analysis", context)
        
        if categories:
            # Run rules for specified categories
            results = []
            for category in categories:
                category_results = self.rule_engine.execute_rules_by_category(context, category)
                results.extend(category_results)
        else:
            # Run all rules
            results = self.rule_engine.execute_rules(context)
            
        self._run_hooks("post_analysis", context, results)
        return results
        
    def generate_report(self, context: PRAnalysisContext, 
                       output_format: str = "json") -> str:
        """
        Generate a report from analysis results.
        
        Args:
            context: The analysis context
            output_format: The format of the report ("json", "html", "markdown")
            
        Returns:
            The report as a string
        """
        self._run_hooks("pre_report", context)
        
        if output_format == "json":
            report = json.dumps(context.to_dict(), indent=2)
        elif output_format == "html":
            # Placeholder for HTML report generation
            report = f"<html><body><h1>PR Analysis Report</h1><p>PR: {context.pr_id}</p></body></html>"
        elif output_format == "markdown":
            # Placeholder for Markdown report generation
            report = f"# PR Analysis Report\n\nPR: {context.pr_id}\n"
        else:
            logger.warning(f"Unknown output format: {output_format}")
            report = json.dumps(context.to_dict(), indent=2)
            
        self._run_hooks("post_report", context, report)
        return report
        
    def save_report(self, report: str, filename: str) -> None:
        """
        Save a report to a file.
        
        Args:
            report: The report to save
            filename: The filename to save to
        """
        with open(filename, "w") as f:
            f.write(report)
            
    def analyze_pr(self, pr_id: str, repo_name: str, base_branch: str, head_branch: str,
                  file_changes: List[Dict[str, Any]], 
                  categories: Optional[Set[str]] = None,
                  output_format: str = "json",
                  output_file: Optional[str] = None) -> Tuple[PRAnalysisContext, str]:
        """
        Analyze a PR and generate a report.
        
        This is a convenience method that combines creating a context, adding file changes,
        running analysis, and generating a report.
        
        Args:
            pr_id: The ID of the PR
            repo_name: The name of the repository
            base_branch: The base branch of the PR
            head_branch: The head branch of the PR
            file_changes: A list of file change dictionaries
            categories: Optional set of rule categories to run
            output_format: The format of the report
            output_file: Optional file to save the report to
            
        Returns:
            A tuple of (context, report)
        """
        # Create context
        context = self.create_context(pr_id, repo_name, base_branch, head_branch)
        
        # Add file changes
        self.add_file_changes(context, file_changes)
        
        # Run analysis
        self.analyze(context, categories)
        
        # Generate report
        report = self.generate_report(context, output_format)
        
        # Save report if requested
        if output_file:
            self.save_report(report, output_file)
            
        return context, report

