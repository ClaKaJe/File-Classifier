#!/usr/bin/env python3
"""Setup script for File-Classifier."""

from setuptools import setup, find_packages
import os
import re

# Lire la version depuis __init__.py
with open(os.path.join('file_classifier', 'file_classifier', '__init__.py'), 'r', encoding='utf-8') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

# Lire le contenu du README.md pour la description longue
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="file-classifier",
    version=version,
    author="ClaKaJe",
    author_email="clakajedev@gmail.com",
    description="Outil CLI de gestion et classement de fichiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clakaje/file-classifier",
    packages=find_packages() + ['file_classifier.file_classifier'],
    package_data={
        "file_classifier": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-magic",
    ],
    entry_points={
        "console_scripts": [
            "file-classifier=file_classifier.file_classifier.cli:main",
        ],
    },
) 