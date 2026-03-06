#!/usr/bin/env python3
"""
Token Optimizer Setup
Package configuration for pip installation.
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read version from src/__init__.py (single source of truth)
init_path = Path(__file__).parent / "src" / "__init__.py"
version = re.search(r'__version__\s*=\s*"([^"]+)"', init_path.read_text()).group(1)

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="token-optimizer",
    version=version,
    author="Smart People Connected",
    author_email="smartpeopleconnected@gmail.com",
    description="Reduce OpenClaw AI costs by 97% - From $1,500+/month to under $50/month",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smartpeopleconnected/openclaw-token-optimizer",
    project_urls={
        "Homepage": "https://github.com/smartpeopleconnected/openclaw-token-optimizer",
        "Bug Tracker": "https://github.com/smartpeopleconnected/openclaw-token-optimizer/issues",
        "Ko-fi": "https://ko-fi.com/smartpeopleconnected",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    packages=find_packages(),
    package_data={
        "": ["templates/*", "templates/**/*"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "token-optimizer=cli:main",
        ],
    },
    keywords=[
        "openclaw",
        "token-optimization",
        "cost-reduction",
        "ai-efficiency",
        "claude",
        "anthropic",
        "llm",
    ],
)
