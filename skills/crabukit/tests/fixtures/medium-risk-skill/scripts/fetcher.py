#!/usr/bin/env python3
"""Medium risk Python script for testing."""

import requests
import os

# Medium risk: Making HTTP requests to external API
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Medium risk: Using getattr (dynamic attribute access)
def dynamic_access(obj, attr_name):
    return getattr(obj, attr_name, None)

# Low risk: File operations
def read_config():
    with open("config.txt", "r") as f:
        return f.read()

# Low risk: Environment variable access (not secret)
def get_user():
    return os.environ.get("USER", "default")
