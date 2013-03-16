# -*- coding: utf-8 -*-
"""
    bdd.py
    An advanced Binary Decision Diagram library for Python
    :copyright: (c) 2011 by Christian Hans
    License GPL v2
"""

class Vertex(object):
    id = None
    index = None
    value = None
    low = None
    high = None
    lparents = []
    hparents = []

    def __init__(self, index=None, value=None, low=None, high=None, lparents=[], hparents=[]):
        self.index = index
        self.value = value
        self.low = low
        self.high = high
        lparents = []
        hparents = []

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

    def optimize(self):
        if self.value!=None:
            return False
        if self.low != self.high:
            return False
        # At this point, v has only one child (self.low = self.high)
        s_child = self.low
        # For each parent, erases the link between parent and v
        # and creates a new link between parent and child of v.
        for lparent in self.lparents:
            lparent.low = s_child
        for hparent in self.hparents:
            hparent.low = s_child
        return True
