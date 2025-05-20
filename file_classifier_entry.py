#!/usr/bin/env python3
"""Entry point for PyInstaller executable."""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main function from the CLI module
from file_classifier.file_classifier.cli import main

if __name__ == "__main__":
    sys.exit(main()) 