"""
setup.py - Package Installation Configuration
Allows: pip install -e . to install the package in editable mode.
"""
from setuptools import setup, find_packages

setup(
    name="autom8",
    version="0.1.0",
    description="Professional automation & systems management toolkit",
    author="Alphonce Liguori Oreny (Agent ALO)",
    author_email="orenyalphy256@gmail.com",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "requests>=2.31.0",
        "sqlalchemy>=2.0.0",
        "apscheduler>=3.10.0",
        "pytest>=7.4.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)