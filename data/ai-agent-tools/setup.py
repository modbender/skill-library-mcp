from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-agent-tools",
    version="1.0.0",
    author="cerbug45",
    author_email="",
    description="A comprehensive Python utility library for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cerbug45/ai-agent-tools",
    project_urls={
        "Bug Tracker": "https://github.com/cerbug45/ai-agent-tools/issues",
        "Documentation": "https://github.com/cerbug45/ai-agent-tools/blob/main/SKILL.md",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    py_modules=["ai_agent_tools"],
    python_requires=">=3.7",
    keywords="ai, agent, tools, utilities, automation, llm, chatbot",
    license="MIT",
)
