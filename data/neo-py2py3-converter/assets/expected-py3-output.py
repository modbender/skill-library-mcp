#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sample Python 2 code for testing the py2py3-converter skill."""

import urllib.request
import configparser
import io

# Print statements
print("Hello, World!")
print("Multiple", "values", "here")
print("error message", file=sys.stderr)

# Raw input
name = input("Enter your name: ")

# xrange usage
for i in range(10):
    print(i)

# Unicode and string handling
greeting = str("hello")
is_string = isinstance(greeting, str)
big_number = int(99999999999)

# Dictionary operations
my_dict = {"a": 1, "b": 2, "c": 3}
if "a" in my_dict:
    print("Found key a")

for key, value in my_dict.items():
    print(key, value)

for val in my_dict.values():
    print(val)

# Exception handling
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print("Error:", e)

# Raise statement
def validate(x):
    if x < 0:
        raise ValueError("x must be non-negative")
    return x

# Reduce
from functools import reduce
total = reduce(lambda a, b: a + b, [1, 2, 3, 4, 5])

# Class definition
class OldStyleClass:
    def __init__(self):
        self.data = []

    def process(self):
        for item in self.data:
            print(item)
