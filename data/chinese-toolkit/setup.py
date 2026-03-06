#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README.md内容
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='openclaw-chinese-toolkit',
    version='1.0.0',
    description='OpenClaw中文处理工具包',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OpenClaw中文社区',
    author_email='chinese-toolkit@openclaw.ai',
    url='https://github.com/openclaw-cn/chinese-toolkit',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'chinese-toolkit=chinese_tools_core:main',
        ],
    },
    keywords='openclaw chinese nlp text-processing translation',
    project_urls={
        'Bug Reports': 'https://github.com/openclaw-cn/chinese-toolkit/issues',
        'Source': 'https://github.com/openclaw-cn/chinese-toolkit',
        'Documentation': 'https://docs.openclaw.ai/zh/',
    },
)