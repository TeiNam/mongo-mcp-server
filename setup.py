from setuptools import setup, find_packages

setup(
    name="mongo-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "fastmcp>=2.3.0",
        "uvicorn>=0.30.0",
        "motor>=3.4.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "mongo-mcp-server=app.cli:main",  # CLI 명령어 이름 변경
        ],
    },
    author="Rastalion",
    author_email="your.email@example.com",
    description="MongoDB MCP Server - A MCP server for MongoDB",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mongo-mcp-server",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
