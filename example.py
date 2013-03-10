from bdd import *

def boolean_function(a, b):
        return (a and b)

bdd1 = BDD(boolean_function, reduce=True)
print bdd1.represents(boolean_function)

print repr(bdd1)
bdd1.to_png()

#print "000"
#print bdd1.eval(False, False, False)
#print bdd1.eval(False, False, True)
#print bdd1.eval(False, True, False)
#print bdd1.eval(False, True, True)

#print "100"
#print bdd1.eval(True, False, False)
#print bdd1.eval(True, False, True)
#print bdd1.eval(True, True, False)
#print bdd1.eval(True, True, True)

#bdd2 = BDD(values = [True, False, True, True])
#print len(bdd2)

#def tand(a, b): return a and b
#bdd3 = bdd1.apply(bdd2, tand)
#print bdd3
