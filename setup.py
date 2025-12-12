"""
Setup configuration for autom8 package.
Agent ALO - Batch 5
"""

from setuptools import find_packages, setup

setup(
    name="autom8",
    version="1.0.0",
    description="Autom8 Systems Automation Platform",
    author="Agent ALO",
    author_email="orenyalphy256.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.11",
    install_requires=[
        "flask>=3.0.0",
        "sqlalchemy>=2.0.23",
        "apscheduler>=3.10.4",
        "requests>=2.31.0",
        "psutil>=5.9.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-flask>=1.3.0",
            "coverage>=7.3.2",
            "flake8>=7.0.0",
            "black>=23.12.1",
            "bandit>=1.7.6",
        ]
    },
    entry_points={
        "console_scripts": [
            "autom8-api=autom8.api:main",
            "autom8-scheduler=autom8.scheduler:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.14",
    ],
)
