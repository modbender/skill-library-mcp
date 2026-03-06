from setuptools import setup

setup(
    name="merchantguard",
    version="2.0.0",
    description="MerchantGuard Compliance Skill for OpenClaw Agents",
    author="MerchantGuard",
    author_email="hello@merchantguard.ai",
    url="https://merchantguard.ai",
    py_modules=["guard"],
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "guard=guard:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
)
