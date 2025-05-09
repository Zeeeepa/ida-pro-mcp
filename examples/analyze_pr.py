"""
Example script for analyzing a PR.
"""
import os
import sys
import logging
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pr_static_analysis import (
    PRAnalyzer, PRData, AnalysisConfig,
    get_default_config
)
from pr_static_analysis.rules import FileExtensionRule, LineCountRule

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main():
    """Run the example."""
    # Create PR data
    pr_data = PRData(
        pr_id="123",
        title="Add new feature",
        description="This PR adds a new feature",
        author="user",
        base_branch="main",
        head_branch="feature",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        files_changed=[
            "pr_static_analysis/core/analysis_context.py",
            "pr_static_analysis/core/rule_engine.py",
            "pr_static_analysis/core/pr_analyzer.py",
            "README.md"
        ]
    )
    
    # Create analyzer with default config
    config = get_default_config()
    analyzer = PRAnalyzer(config)
    
    # Register rules manually
    analyzer.rule_engine.register_rule(FileExtensionRule)
    analyzer.rule_engine.register_rule(LineCountRule)
    
    # Analyze PR
    results = analyzer.analyze_pr(pr_data)
    
    # Print results
    print(f"Analysis completed with {len(results)} results:")
    for result in results:
        print(f"[{result.rule_id}] {result.status}: {result.message}")
        if result.file_path:
            print(f"  File: {result.file_path}")
        if result.details:
            print(f"  Details: {result.details}")
        print()
        
if __name__ == "__main__":
    main()

