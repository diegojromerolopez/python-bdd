# -*- coding: utf-8 -*-
"""
    bdd.py
    An advanced Binary Decision Diagram library for Python
    :copyright: (c) 2011 by Christian Hans
"""

class Vertex(object):
    id = None
    index = None
    value = None
    low = None
    high = None

    def __init__(self, index=None, value=None, low=None, high=None):
        self.index = index
        self.value = value
        self.low = low
        self.high = high

    def __eq__(self, other):
        if self.index!=None and other.index!=None:
            return self.index==other.index
        elif self.value!=None and other.value!=None:
            return self.value==other.value
        else:
            return False

    def __repr__(self):
        if self.index!=None:
            return '<Vertex ' + str(self.index) + '>'
        elif self.value!=None:
            return '<Vertex ' + str(self.value) + '>'
        else:
            return '<Vertex>'
