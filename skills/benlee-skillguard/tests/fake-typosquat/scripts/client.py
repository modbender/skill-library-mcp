#!/usr/bin/env python3
"""HTTP client that imports typosquatted packages."""
import reqeusts  # typosquat of requests

def fetch(url):
    return reqeusts.get(url)
