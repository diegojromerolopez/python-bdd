# -*- coding: utf-8 -*-

from bdd import *

###################################
## Algorithm 2: P(ψ)
def get_formula_sat_prob(bdd):
    """
    Gets the probability of having False or True in the BDD.
    Returns a list whose
    - First element (index 0) is the probability of getting False in the function.
    - Second element (index 1) is the probability of getting True in the function.
    """
    bdd_vertices = bdd.vertices
    formula_sat_prob = []
    for i in xrange(0,len(bdd_vertices)):
        formula_sat_prob.append(0.0)
    i = len(bdd_vertices)-1
    formula_sat_prob[-1] = 1.0   # root vertex
    while i > 1:
        formula_sat_prob[bdd_vertices[i].low.id] += formula_sat_prob[i]/2.0
        formula_sat_prob[bdd_vertices[i].high.id] += formula_sat_prob[i]/2.0
        i-=1
    # Técnicamente los valores > 1 no valen para nada
    #formula_sat_prob=[formula_sat_prob[0],formula_sat_prob[1]]
    return formula_sat_prob

###################################
# Algorithm 3: MPr(x_i)
def get_marginal_prob(v, total_prob, formula_sat_prob, prob, bdd, var_ordering):
    prob_low = 0.0
    prob_high = 0.0
    _bdd = bdd
    bdd = bdd.vertices
    names = _bdd.variable_names
    # Avoid visited nodes
    bdd[v].visited = not bdd[v].visited
    # Base case 1
    if bdd[v].low.value==True:
        prob_low = formula_sat_prob[v]/2.0
    elif bdd[v].low.value!=False:
        if bdd[v].visited != bdd[bdd[v].low.id].visited:
            get_marginal_prob(bdd[v].low.id, total_prob, formula_sat_prob, prob, _bdd, var_ordering)
        prob_low = (total_prob[bdd[v].low.id] * formula_sat_prob[v]/2.0) / formula_sat_prob[bdd[v].low.id]
    # Base case 2
    if bdd[v].high.value==True:
        prob_high = formula_sat_prob[v]/2.0
    elif bdd[v].high.value!=False:
        if bdd[v].visited != bdd[bdd[v].low.id].visited:
            get_marginal_prob(bdd[v].high.id, total_prob, formula_sat_prob, prob, _bdd, var_ordering)
        prob_high = (total_prob[bdd[v].high.id] * formula_sat_prob[v]/2.0) / formula_sat_prob[bdd[v].high.id]
    # 
    #print "{0} prob_low={1}, prob_high={2}".format(names[v],prob_low,prob_high)
    print bdd
    print "{0} in total_prob ({1})".format(v,len(total_prob))
    total_prob[v] = prob_low + prob_high
    print "{0} in prob ({1})".format(bdd[v].id,(prob))
    prob[bdd[v].i] += prob_high
    # Trasversal
    i = bdd[v].i+1
    while i<bdd[bdd[v].low.id].i:
        prob[i] += prob_low/2.0
        i += 1
    i = bdd[v].i+1
    while i<bdd[bdd[v].high.id].i:
        prob[i] += prob_high/2.0
        i += 1
    #print prob

# Algorithm 1
def get_prob(bdd):
    bdd.reset()
    number_of_literals = bdd.n
    var_ordering = bdd.variable_names
    bdd_vertices = bdd.vertices
    bdd_length = len(bdd_vertices)
    
    print bdd_length
    print number_of_literals
    
    # Probabilidades totales
    total_prob = [0.0 for i in xrange(0,bdd_length)]
    prob = [0.0 for i in xrange(0,number_of_literals)]
    # Total probabilities
    formula_sat_prob = get_formula_sat_prob(bdd)
    print "Formula SAT Prob, P(psi) = {0}".format(formula_sat_prob)
    # Marginal probabilities
    get_marginal_prob(bdd_length-1, total_prob, formula_sat_prob, prob, bdd, var_ordering)
    print "MP(x_i) = {0}".format(prob)
    for i in xrange(0,number_of_literals):
        prob[i] = prob[i]/formula_sat_prob[1]
    return prob

##############################################
## Pruebas

def f1(a,b):
        return a or b

def f2(x1, x2, x3, x4):
        return (x1 and x2) or (x3 and x4)

REDUCE = True

bdd = BDD(f1, reduce=REDUCE)
#print bdd.vertices
print "BDD array: {0}".format(["{0} (pos={1}, index={2}, i={3})".format(bdd._get_node_label(v),v.id,v.index,v.i) for v in bdd.vertices])
print bdd.variable_names
prob = get_prob(bdd)
print "Prob {0}".format(prob)
bdd.to_png(filename="(x1 and x2) or (x3 and x4)")
    
