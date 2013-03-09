# -*- coding: utf-8 -*-
"""
    bdd.py
    An advanced Binary Decision Diagram library for Python
    :copyright: (c) 2011 by Christian Hans
    License GPL v2
"""

from math import log
from inspect import getargspec
from sys import getsizeof
from vertex import Vertex
import pydot

class BDD(object):
    # Function variable names (used to construct the dot graph)
    variable_names = []
    
    # Original boolean function that represents this BDD
    function = None
    
    # Name of the boolean function (defaults to function.func_name if that exists)
    name = None
    
    # Number of boolean variables
    n = 0
    
    # Root vertex of the BDD
    root = None

    # TODO: move to __init__
    _vcount = 0

    def __init__(self, function=None, values=None, reduce=True):

        def generate_tree_function(function, path=[]):
            path_len = len(path)
            if path_len<self.n:
                v = Vertex(index=path_len+1)
                v.low = generate_tree_function(function, path+[False])
                v.high = generate_tree_function(function, path+[True])
                return v
            elif path_len==self.n:
                # reached leafes
                return Vertex(value=function(*path))

        def generate_tree_values(values, level=0):
            if level<self.n:
                v = Vertex(index=level+1)
                v.low = generate_tree_values(values, level+1)
                v.high = generate_tree_values(values, level+1)
                return v
            elif level==self.n:
                # reached leafes
                v = Vertex(value=values[self._vcount])
                self._vcount = self._vcount + 1
                return v

        if function:
            self.function = function
            self.name = function.func_name
            self.variable_names = getargspec(function).args
            self.n = len(getargspec(function).args)
            self.root = generate_tree_function(function)
            if reduce:
                self.reduce()
        elif values:
            values_count = len(values)

            if values_count%2!=0:
                raise ValueError('Number of values must be a power of 2')
            else:
                self.name = "Truth table"
                self.n = int(log(values_count, 2))
                self.variable_names = list("x_{0}".format(i) for i in xrange(1,self.n+1))
                self._vcount = 0
                self.root = generate_tree_values(values)
                if reduce:
                    self.reduce()

    def eval(self, *args):
        def _eval(v, *args):
            if v.index!=None:
                if not args[v.index-1]:
                    return _eval(v.low, *args)
                else:
                    return _eval(v.high, *args)
            elif v.value!=None:
                return v.value

        if len(args)!=self.n:
            raise TypeError('BDD takes exactly ' + str(self.n) +
                ' arguments (' + str(len(args)) + ' given)')

        return _eval(self.root, *args)

    def traverse(self):
        def _traverse(v, levels):
            if v.index!=None:
                levels[v.index-1].append(v)
                _traverse(v.low, levels)
                _traverse(v.high, levels)
            elif v.value!=None:
                levels[len(levels)-1].append(v)

        levels = []
        for i in xrange(self.n+1):
            levels.append([])
        _traverse(self.root, levels)
        return levels

    def reduce(self):
        result = []
        nextid = 0

        # Traverse tree, so that level[i] contains all vertices of level i
        levels = self.traverse()
        levels.reverse()

        # Bottom-up iteration over the BDD
        for level in levels:
            iso_map = {}

            # Merge isomorphic vertices in this tree level under same key in iso_map
            for v in level:
                # Generate key
                if v.value!=None:
                    key = str(v.value)
                elif v.low.id==v.high.id:
                    v.id = v.low.id
                    continue
                else:
                    key = str(v.low.id) + ' ' + str(v.high.id)

                # Append under key to iso_map
                if key in iso_map:
                    iso_map[key].append(v)
                else:
                    iso_map[key] = [v]

            for key, vertices in iso_map.items():
                # Set same id for isomorphic vertices
                for v in vertices:
                    v.id = nextid
                nextid = nextid + 1

                # Store one isomorphic vertex in result
                x = vertices[0]
                result.append(x)

                # Update references
                if x.index!=None:
                    x.low = result[x.low.id]
                    x.high = result[x.high.id]

        # Update reference to root vertex (alwayes the last entry in result)
        self.root = result[-1]

    def apply(self, bdd, function):
        cache = {}

        def _apply(v1, v2, f):
            # Check if v1 and v2 have already been calculated
            key = str(v1.id) + ' ' + str(v2.id)
            if key in cache:
                return cache[key]

            u = Vertex()
            cache[key] = u

            if v1.value!=None and v2.value!=None:
                u.value = f(v1.value, v2.value)
            else:
                if v1.index!=None and (v2.value!=None or v1.index<v2.index):
                    u.index = v1.index
                    u.low = _apply(v1.low, v2, f)
                    u.high = _apply(v1.high, v2, f)
                elif v1.value!=None or v1.index>v2.index:
                    u.index = v2.index
                    u.low = _apply(v1, v2.low, f)
                    u.high = _apply(v1, v2.high, f)
                else:
                    u.index = v1.index
                    u.low = _apply(v1.low, v2.low, f)
                    u.high = _apply(v1.high, v2.high, f)

            return u

        new_bdd = BDD()
        new_bdd.n = self.n
        new_bdd.root = _apply(self.root, bdd.root, function)
        new_bdd.reduce()
        return new_bdd

    # Returns True if the BDD represents function
    def represents(self, function):
        def _represents(args=[]):
            args_len = len(args)
            if args_len==self.n:
                return function(*args)==self.eval(*args)
            elif args_len<self.n:
                return _represents(args+[False]) and _represents(args+[True])

        if len(getargspec(function).args)==self.n:
            return _represents()
        else:
            return False

    def __eq__(self, other):
        def equal(x1, x2):
            return x1==x2

        return (isinstance(other, BDD) and
            self.apply(other, equal).root == Vertex(value=True))

    def __len__(self):
        def _count_bdd(v):
            if v.index!=None:
                return 1 + _count_bdd(v.low) + _count_bdd(v.high)
            elif v.value!=None:
                return 1
        return _count_bdd(self.root)

    def __sizeof__(self):
        def _sizeof_bdd(v):
            if v.index!=None:
                return getsizeof(v) + _sizeof_bdd(v.low) + _sizeof_bdd(v.high)
            elif v.value!=None:
                return getsizeof(v)
        return _sizeof_bdd(self.root)

    def __repr__(self):
        def _bdd_to_string(v):
            if v.index!=None:
                return v.__repr__() + '\n' + _bdd_to_string(v.low) + '\n' + _bdd_to_string(v.high)
            elif v.value!=None:
                return v.__repr__()
        return '<BDD n=' + str(self.n) + ',\n' + _bdd_to_string(self.root) + '>'


    def to_png(self, filename=None):
        if not filename:
            filename = "{0}.png".format(self.name)
        # Abstract representation in dot format of the BDD 
        graph = pydot.Dot(graph_type='digraph', label=self.name)
        graph.edges = {}
        
        bdd = self
        # Obtains the node name (it's useful if the tree is not reduced)
        def get_node_name(v, path_name):
            """Obtains the node name: if BDD is reduced it gets the id, else returns the node path-from-root name"""
            if v.index is not None:
                return bdd.variable_names[v.index-1] + " ("+path_name+")"
            if v.value is not None:
                return str(v.value) + " ("+path_name+")"
            if v.id is not None:
                return v.id
            return path_name
        
        # Generates the graph
        def _traverse(v, levels, path_name):
            """Traverse all nodes and creates a dot graph"""
            if v.index!=None:
                levels[v.index-1].append(v)
                _traverse(v.low, levels, path_name+"L")
                _traverse(v.high, levels, path_name+"H")
                if not hasattr(v,"visited") or not v.visited:
                    v.visited = True
                    v.node = pydot.Node(name=get_node_name(v, path_name))
                    graph.add_edge(pydot.Edge(v.node, v.low.node, style="dashed", arrowtype="normal", dir="forward"))
                    graph.add_edge(pydot.Edge(v.node, v.high.node, arrowtype="normal", dir="forward"))
            elif v.value!=None:
                levels[len(levels)-1].append(v)
                if not hasattr(v,"visited") or not v.visited:
                    v.visited = True
                    v.node = pydot.Node(name=get_node_name(v,path_name), style="filled", fillcolor="red")

        levels = []
        for i in xrange(self.n+1):
            levels.append([])
        
        path_name = "R"
        _traverse(self.root, levels, path_name)
        graph.write_png(filename)
        
        return levels
