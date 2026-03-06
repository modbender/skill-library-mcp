#!/usr/bin/env python3
"""
Setup script for iCalendar Sync Skill for OpenClaw
"""

from setuptools import setup, find_packages
import os

# Read README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "iCalendar Sync - Professional iCloud Calendar integration for OpenClaw"

setup(
    name="openclaw-icalendar-sync",
    version="2.3.0",
    author="Black_Temple",
    author_email="contact@clawhub.ai",
    description="Professional iCloud Calendar integration for OpenClaw agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/h8kxrfp68z-lgtm/OpenClaw",
    project_urls={
        "Bug Tracker": "https://github.com/h8kxrfp68z-lgtm/OpenClaw/issues",
        "Documentation": "https://github.com/h8kxrfp68z-lgtm/OpenClaw/tree/skills/skills/icalendar-sync",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "caldav>=1.3.0",
        "icalendar>=5.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
        "keyring>=24.0.0",
    ],
    entry_points={
        "console_scripts": [
            "icalendar-sync=icalendar_sync.calendar:main",
        ],
    },
)
