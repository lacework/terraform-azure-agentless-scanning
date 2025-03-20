import os
import sys

# Add the project root directory to the Python path
# This allows imports from preflight_check to work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))