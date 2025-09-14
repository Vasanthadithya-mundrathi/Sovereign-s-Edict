"""
Setup script for Sovereign's Edict
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="sovereigns-edict",
    version="0.1.0",
    author="SIH 2025 Team",
    author_email="vasanthfeb13@gmail.com",
    description="An Actionable Intelligence Platform for Clause-Level Policy Argumentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vasanthadithya-Mundrathi/SIH-2025",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sovereigns-edict=main:app",
        ],
    },
)