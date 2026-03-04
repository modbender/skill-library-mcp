"""Shared pytest configuration and fixtures for gpu-service tests."""

import os
import sys

# Add gpu-service directory to path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
