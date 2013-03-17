# -*- coding: utf-8 -*-

from bdd import *

formula = "(a or not b or not c) and (a or b or d)"

REDUCE = False
bdd1 = BDD(formula, reduce=REDUCE)
bdd1.to_png(filename="complex_bdd.png")
print "Is BDD1 (a or b)? {0}".format(bdd1.represents(bdd1.function))
