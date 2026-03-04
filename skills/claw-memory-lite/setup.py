#!/usr/bin/env python3
"""
Setup script for claw-memory-lite

Installation:
    pip install -e .

Usage:
    python3 setup.py install
    python3 setup.py develop
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text() if README_PATH.exists() else ""

setup(
    name="claw-memory-lite",
    version="1.0.0",
    author="timothysong0w0",
    description="Lightweight long-term memory for OpenClaw - SQLite-powered, zero dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timothysong0w0/claw-memory-lite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    scripts=[
        "scripts/db_query.py",
        "scripts/extract_memory.py",
    ],
    package_data={
        "": ["templates/*.md"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "claw-memory-query=scripts.db_query:main",
            "claw-memory-extract=scripts.extract_memory:main",
        ],
    },
    # No external dependencies - uses only Python built-in sqlite3
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
