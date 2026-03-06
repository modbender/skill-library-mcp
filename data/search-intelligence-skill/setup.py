from setuptools import setup, find_packages

setup(
    name="search-intelligence-skill",
    version="1.0.0",
    description="Advanced AI search skill with SearXNG backend, dork generation, and intelligent strategies",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["httpx>=0.27.0"],
    author="Your Name",
    license="MIT",
)