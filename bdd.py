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

########################################################################
## Binary Decision Diagram class
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

    # Is the BDD reduced
    is_reduced = False

    ####################################################################
    ## Constructor
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


    ####################################################################
    ## Evaluate the boolean function using truth arguments.
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

    
    ####################################################################
    ## Traverses the BDD
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


    ####################################################################
    ## Reduces the BDD deleting redundant nodes and edges
    def reduce(self):
        if self.is_reduced:
            return self
        
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
                    # Here's the core of the reduction method
                    # If there is a redundant node whose id is equal to one of its descendants' id
                    # we get the descendant, so we skip the redundant node
                    x.low = result[x.low.id]
                    x.high = result[x.high.id]

        # Update reference to root vertex (alwayes the last entry in result)
        self.root = result[-1]
        # this BDD is now reduced
        self.is_reduced = True
        self.to_png(filename="xxx_bdd1.png")



    ####################################################################
    ## Apply operation
    def apply(self, bdd, function, reduce=True):
        # If the trees are not reduced, we reduce them first
        if not bdd.is_reduced:
            bdd.reduce()
        if not self.is_reduced:
            self.reduce()
        
        cache = {}
        # Leafs
        true = Vertex(value=True)
        false = Vertex(value=False)
        leafs = {True:true, False:false}
        
        def _apply(v1, v2, f):
            # Check if v1 and v2 have already been calculated
            key = str(v1.id) + ' ' + str(v2.id)
            if key in cache:
                return cache[key]
            
            # Result vertex
            u = Vertex()
            
            # If the vertices are both leafs,
            # apply the boolean function to them
            if v1.value!=None and v2.value!=None:
                u = leafs[f(v1.value, v2.value)]
                #u = Vertex(value=f(v1.value, v2.value))
                cache[key] = u
                return u
            if v1.value==None and (v2.value!=None or v1.index<v2.index):
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
            
            #u.low.lparents.append(u)
            #u.high.hparents.append(u)
            #u.low.optimize()
            #u.high.optimize()
            cache[key] = u
            return u

        new_bdd = BDD()
        new_bdd.n = self.n
        new_bdd.root = _apply(self.root, bdd.root, function)
        new_bdd.variable_names = list(self.variable_names)
        if reduce:
            new_bdd.reduce()
        return new_bdd

    ####################################################################
    ## Returns True if the BDD represents the boolean function
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


    ####################################################################
    ## Equal to operator
    def __eq__(self, other):
        def equal(x1, x2):
            return x1==x2

        return (isinstance(other, BDD) and
            self.apply(other, equal).root == Vertex(value=True))


    ####################################################################
    ## Gets the number of nodes of the BDD
    def __len__(self):
        def _count_bdd(v):
            if v.index!=None:
                return 1 + _count_bdd(v.low) + _count_bdd(v.high)
            elif v.value!=None:
                return 1
        return _count_bdd(self.root)


    ####################################################################
    ## Gets the memory consumed by the BDD
    def __sizeof__(self):
        def _sizeof_bdd(v):
            if v.index!=None:
                return getsizeof(v) + _sizeof_bdd(v.low) + _sizeof_bdd(v.high)
            elif v.value!=None:
                return getsizeof(v)
        return _sizeof_bdd(self.root)


    ####################################################################
    ## Converts the BDD to a string
    def __repr__(self):
        def _bdd_to_string(v):
            if v.index!=None:
                return v.__repr__() + '\n' + _bdd_to_string(v.low) + '\n' + _bdd_to_string(v.high)
            elif v.value!=None:
                return v.__repr__()
        return '<BDD n=' + str(self.n) + ',\n' + _bdd_to_string(self.root) + '>'


    ####################################################################
    ## Creates a dot graph of the BDD
    def get_dot_graph(self):

        # Abstract representation in dot format of the BDD 
        graph = pydot.Dot(graph_type='digraph', label=self.name)
        graph.edges = {}
        visited_vertices = []
        
        bdd = self
        # Obtains the unique node name (better than using a rand())
        def get_node_name(v, path_name):
            """Obtains the node name: if BDD is reduced it gets the id, else returns the node path-from-root name"""
            if v.index is not None:
                return bdd.variable_names[v.index-1] + " ("+path_name+")"
            if v.value is not None:
                return str(v.value) + " ("+path_name+")"
            if v.id is not None:
                return v.id
            return path_name
            
        # Obtains the node label that is the variable name that the node represents
        def get_node_label(v):
            """Obtains the node variable name"""
            # If it's not a leaf, get the variable name associated
            if v.index is not None:
                return bdd.variable_names[v.index-1]
            # If it's a leaf, get 1/0 from True/False, resp.
            if v.value is not None:
                if v.value:
                    return "1"
                return "0"
            raise ValueError("There is no label for this node!")
        
        # Generates the graph
        def _create_graph(v, path_name):
            """Traverse all nodes and creates a dot graph"""
            if v.index!=None:
                _create_graph(v.low, path_name+"L")
                _create_graph(v.high, path_name+"H")
                if not hasattr(v,"visited") or not v.visited:
                    v.visited = True
                    visited_vertices.append(v)
                    v.node = pydot.Node(name=get_node_name(v,path_name), label=get_node_label(v))
                    graph.add_node(v.node)
                    graph.add_edge(pydot.Edge(v.node, v.low.node, style="dashed", arrowtype="normal", dir="forward"))
                    graph.add_edge(pydot.Edge(v.node, v.high.node, arrowtype="normal", dir="forward"))
            elif v.value!=None:
                if not hasattr(v,"visited") or not v.visited:
                    v.visited = True
                    visited_vertices.append(v)
                    v.node = pydot.Node(name=get_node_name(v,path_name), label=get_node_label(v),  shape="box")
                    graph.add_node(v.node)
        
        path_name = "R"
        _create_graph(self.root, path_name)
        for visited_vertex in visited_vertices:
            visited_vertex.visited = False
        return graph
    
    
    ####################################################################
    ## Creates a PNG file with a graph of the BDD        
    def to_png(self, filename=None):
        if not filename:
            filename = "{0}.png".format(self.name)
        
        graph = self.get_dot_graph()
        graph.write_png(filename)

