"""
Setup script for the mock MCP package.
"""
from setuptools import setup, find_packages

setup(
    name="mcp",
    version="1.6.0",
    description="Mock MCP package for testing",
    author="Codegen",
    author_email="codegen@example.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)

