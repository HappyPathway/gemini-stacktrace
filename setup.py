"""
Setup script for gemini-stacktrace.
"""

from setuptools import setup, find_packages
import re
from pathlib import Path


# Read the version from the package's __init__.py
init_path = Path("gemini_stacktrace") / "__init__.py"
with open(init_path, "r") as f:
    init_content = f.read()
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version in gemini_stacktrace/__init__.py")


# Read the README for the long description
with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="gemini-stacktrace",
    version=version,
    description="A Python tool that uses Gemini to analyze stack traces and generate remediation plans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HappyPathway",
    author_email="info@happypathway.com",
    url="https://github.com/happypathway/gemini-stacktrace",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "typer>=0.9.0",
        "pydantic>=2.5.2",
        "pydantic-ai>=0.1.4",
        "google-generativeai>=0.3.1",
        "python-dotenv>=1.0.0",
        "pathlib>=1.0.1",
        "rich>=13.6.0",
    ],
    entry_points={
        "console_scripts": [
            "gemini-stacktrace=gemini_stacktrace.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
