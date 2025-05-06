"""
Example script for using the PR static analysis system.

This script demonstrates how to use the PR static analysis system.
"""

import json
import os
import sys
from typing import Dict, List, Any

from pr_analysis.core.pr_analyzer import PRAnalyzer
from pr_analysis.core.analysis_context import PRAnalysisContext
from pr_analysis.github.pr_client import PRClient
from pr_analysis.reporting.report_generator import ReportGenerator
from pr_analysis.reporting.report_formatter import ReportFormatter
from pr_analysis.reporting.visualization import Visualization


def analyze_pr(pr_number: str, repo: str, output_format: str = "json", 
              output_file: str = None) -> None:
    """
    Analyze a PR and generate a report.
    
    Args:
        pr_number: The PR number
        repo: The repository (owner/name)
        output_format: The format of the report
        output_file: The file to save the report to
    """
    # Parse repository
    repo_parts = repo.split("/")
    if len(repo_parts) != 2:
        print(f"Invalid repository format: {repo}")
        print("Expected format: owner/name")
        sys.exit(1)
        
    repo_owner, repo_name = repo_parts
    
    # Create PR client
    client = PRClient()
    
    # Get PR data
    pr_data = client.get_pr(repo_owner, repo_name, int(pr_number))
    if not pr_data:
        print(f"Failed to get PR data for {pr_number}")
        sys.exit(1)
        
    # Get PR files
    files = client.get_pr_files(repo_owner, repo_name, int(pr_number))
    if not files:
        print(f"Failed to get PR files for {pr_number}")
        sys.exit(1)
        
    # Convert files to the format expected by the analyzer
    file_changes = []
    for file in files:
        file_changes.append({
            "filename": file.get("filename"),
            "status": file.get("status"),
            "patch": file.get("patch"),
        })
        
    # Create analyzer
    analyzer = PRAnalyzer()
    
    # Analyze PR
    context, report = analyzer.analyze_pr(
        pr_id=pr_number,
        repo_name=f"{repo_owner}/{repo_name}",
        base_branch=pr_data.get("base", {}).get("ref", "main"),
        head_branch=pr_data.get("head", {}).get("ref", "head"),
        file_changes=file_changes,
        output_format=output_format,
        output_file=output_file,
    )
    
    # Print summary
    print(f"Analysis complete for PR #{pr_number}")
    print(f"Found {len(context.results)} issues:")
    print(f"- Errors: {len([r for r in context.results if r.severity == 'error'])}")
    print(f"- Warnings: {len([r for r in context.results if r.severity == 'warning'])}")
    print(f"- Info: {len([r for r in context.results if r.severity == 'info'])}")
    
    if output_file:
        print(f"Report saved to {output_file}")
    else:
        print("\nReport:")
        print(report)


def main() -> None:
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze a PR for static issues")
    parser.add_argument("pr_number", help="The PR number")
    parser.add_argument("repo", help="The repository (owner/name)")
    parser.add_argument("--format", choices=["json", "html", "markdown"], default="json",
                      help="The format of the report")
    parser.add_argument("--output", help="The file to save the report to")
    
    args = parser.parse_args()
    
    analyze_pr(args.pr_number, args.repo, args.format, args.output)


if __name__ == "__main__":
    main()

