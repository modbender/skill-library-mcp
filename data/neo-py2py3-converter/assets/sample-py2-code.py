#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sample Python 2 code for testing the py2py3-converter skill."""

from __future__ import print_function
import urllib2
import ConfigParser
import StringIO

# Print statements
print "Hello, World!"
print "Multiple", "values", "here"
print >> sys.stderr, "error message"

# Raw input
name = raw_input("Enter your name: ")

# xrange usage
for i in xrange(10):
    print i

# Unicode and string handling
greeting = unicode("hello")
is_string = isinstance(greeting, basestring)
big_number = long(99999999999)

# Dictionary operations
my_dict = {"a": 1, "b": 2, "c": 3}
if my_dict.has_key("a"):
    print "Found key a"

for key, value in my_dict.iteritems():
    print key, value

for val in my_dict.itervalues():
    print val

# Exception handling
try:
    result = 10 / 0
except ZeroDivisionError, e:
    print "Error:", e

# Raise statement
def validate(x):
    if x < 0:
        raise ValueError, "x must be non-negative"
    return x

# Reduce
total = reduce(lambda a, b: a + b, [1, 2, 3, 4, 5])

# Class definition
class OldStyleClass:
    def __init__(self):
        self.data = []

    def process(self):
        for item in self.data:
            print item
