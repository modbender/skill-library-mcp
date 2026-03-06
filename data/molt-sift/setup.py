#!/usr/bin/env python3
"""
Setup for molt-sift
"""

from setuptools import setup, find_packages

setup(
    name='molt-sift',
    version='0.1.0',
    description='Data validation and signal extraction for AI agents. Earn bounties.',
    author='Pinchie',
    author_email='pinchie@claw.ai',
    url='https://github.com/pinchie/molt-sift',
    packages=['molt_sift'],
    package_dir={'molt_sift': 'scripts'},
    entry_points={
        'console_scripts': [
            'molt-sift=molt_sift.molt_sift:main',
        ],
    },
    install_requires=[
        'flask>=2.0.0',
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
