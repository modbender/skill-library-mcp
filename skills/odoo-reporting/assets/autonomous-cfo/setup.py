#!/usr/bin/env python3
"""
Setup script for autonomous-cfo Odoo skill
"""
from setuptools import setup, find_packages

setup(
    name="autonomous-cfo",
    version="2.0.0",
    description="Financial intelligence for Odoo via OpenClaw",
    author="ashrf-in",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "matplotlib>=3.8.0,<4.0.0",
        "pillow>=10.0.0,<12.0.0",
        "fpdf2>=2.8.0,<3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cfo-cli=tools.cfo_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
