from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Load requirements
requirements = ["requests>=2.31.0", "beautifulsoup4>=4.12.0", "markdownify>=0.11.6"]

setup(
    name="read_wechat_article",
    version="1.0.0",
    description="微信公众号文章阅读工具",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/claw-community/read_wechat_article",
    author="Claw Community",
    author_email="community@claw.ai",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "read-wechat-article=read_wechat_article:main",
        ],
    },
    keywords="微信公众号 文章阅读 网页抓取 内容解析 Markdown",
    project_urls={
        "Bug Reports": "https://github.com/claw-community/read_wechat_article/issues",
        "Source": "https://github.com/claw-community/read_wechat_article",
        "Documentation": "https://read-wechat-article.readthedocs.io/",
        "Community": "https://discord.gg/claw",
    },
)}]}]<|FunctionCallEnd|>