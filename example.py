# -*- coding: utf-8 -*-

from bdd import *

def f_not(a):
        return (not a)

def f_or(a, b):
        """a or b"""
        return (a or b)

def f_and(a, b):
        """a and b"""
        return (a and b)

def f_implies(a, b, c):
        """not a or b"""
        return (not a or b)

def f1(a, b, x):
        return a or b

REDUCE = False
APPLY_REDUCE = False

bdd1 = BDD(f1, reduce=REDUCE)
bdd1.to_png(filename="bdd1.png")
print "Is BDD1 (a or b)? {0}".format(bdd1.represents(f1))

def f2(a, b, x):
        return x or b

bdd2 = BDD(f2, reduce=REDUCE)
bdd2.to_png(filename="bdd2.png")
print "Is BDD2 (x or b)? {0}".format(bdd2.represents(f2))

# Results
def f_test(a,b,x):
        return (a or b) and (x or b)

bdd3 = bdd1.apply(bdd2,f_and,reduce=APPLY_REDUCE)
bdd3.to_png(filename="bdd3.png")
print "Is (non-reduced) BDD3 (a or b) and (x or b)?: {0}".format(bdd3.represents(f_test))

bdd3.reduce()
bdd3.to_png(filename="reduced_bdd3.png")
print "Is (reduced) BDD3 (a or b) and (x or b)?: {0}".format(bdd3.represents(f_test))
