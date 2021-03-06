python-bdd
==========

Python-BDD is an advanced Binary Decision Tree (BDD) library for Python.

BDDs can either be constructed by specifying a boolean function or leaf values in the constructor. Trees are automatically compressed with `reduce()`. This behavior can be suppressed by setting the `reduce` parameter to `False` in the constructor. The function `eval()` evaluates the tree for a certain variable assignment.

It is possible to combine two BDDs with boolean functions using `apply()`. BDDs can also be compared using Python's normal compare operator `==`. Python's length function `len()` is also supported and returns the number of vertices. Further more BDDs have a string representation for visualation of trees using Python's built-in `print` function.

Example
-------

    def andor(a, b, c): return (a and b) or c
    bdd1 = BDD(andor)
    print bdd1.represents(andor)
    print bdd1.eval(True, False, True)
    
    bdd2 = BDD(values = [True, False, True, True])
    print len(bdd2)

    def tand(a, b): return a and b
    bdd3 = bdd1.apply(bdd2, tand)
    print bdd3
    
LICENSE
This project has been forked from https://github.com/e-mux/python-bdd. The creator stated that the code has the GPL2 license in https://github.com/e-mux/python-bdd/issues/1. This forked code has the license GPL V2 as well. See the license.txt file for more information.
