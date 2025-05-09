#!/usr/bin/env python
"""
Run the reporting system with sample results.
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the run script
from run import main

# Set the arguments
sys.argv = [
    sys.argv[0],
    '--config', os.path.join(os.path.dirname(__file__), 'config.json'),
    '--results', os.path.join(os.path.dirname(__file__), 'sample_results.json'),
    '--pr-number', '456',
    '--pr-title', 'Sample PR',
    '--pr-url', 'https://github.com/org/repo/pull/456',
    '--pr-base', 'main',
    '--pr-head', 'sample-branch',
    '--format', 'markdown',
    '--output-dir', os.path.join(os.path.dirname(__file__), 'reports'),
    '--visualizations'
]

# Run the main function
if __name__ == "__main__":
    main()

