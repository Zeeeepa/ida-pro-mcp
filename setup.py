"""
Setup script for the PR static analysis package.
"""
from setuptools import setup, find_packages

setup(
    name="pr-static-analysis",
    version="0.1.0",
    description="PR static analysis system",
    author="Codegen",
    author_email="codegen@example.com",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)

