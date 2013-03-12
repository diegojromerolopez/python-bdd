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

bdd1 = BDD(f1, reduce=True)
bdd1.to_png(filename="bdd1.png")

def f2(a, b, x):
        return x or b

bdd2 = BDD(f2, reduce=True)
bdd2.to_png(filename="bdd2.png")

bdd3 = bdd1.apply(bdd2,f_and)
bdd3.to_png(filename="bdd3.png")

def f_test(a,b,x):
        return (a or b) and (x or b)

print bdd3.represents(f_test)
