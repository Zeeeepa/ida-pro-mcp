"""
Setup script for the PR static analysis system.
"""
from setuptools import setup, find_packages

setup(
    name="pr_static_analysis",
    version="0.1.0",
    description="A system for static analysis of pull requests",
    author="Codegen",
    author_email="codegen@example.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.1",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

