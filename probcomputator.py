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
    print "v_id " + str(v)
    prob_low = 0.0
    prob_high = 0.0
    _bdd = bdd
    bdd = bdd.vertices
    names = _bdd.variable_names
    # Avoid visited nodes
    bdd[v].visited = not bdd[v].visited
    # Base case 1
    if bdd[v].low.id==1:
        prob_low = formula_sat_prob[v]/2.0
    elif bdd[v].low.id!=0:
        if bdd[v].visited != bdd[bdd[v].low.id].visited:
            get_marginal_prob(bdd[v].low.id, total_prob, formula_sat_prob, prob, _bdd, var_ordering)
        prob_low = (total_prob[bdd[v].low.id] * formula_sat_prob[v]/2.0) / formula_sat_prob[bdd[v].low.id]
    # Base case 2
    if bdd[v].high.id==1:
        prob_high = formula_sat_prob[v]/2.0
    elif bdd[v].high.id!=0:
        if bdd[v].visited != bdd[bdd[v].high.id].visited:
            get_marginal_prob(bdd[v].high.id, total_prob, formula_sat_prob, prob, _bdd, var_ordering)
        prob_high = (total_prob[bdd[v].high.id] * formula_sat_prob[v]/2.0) / formula_sat_prob[bdd[v].high.id]
    # 
    #print "{0} prob_low={1}, prob_high={2}".format(names[v],prob_low,prob_high)
    #print bdd
    #print "{0} in total_prob ({1})".format(v,len(total_prob))
    total_prob[v] = prob_low + prob_high
    #print "{0} in prob ({1})".format(bdd[v].id,(prob))
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
    
    #print bdd_length
    #print number_of_literals
    
    # Probabilidades totales
    total_prob = [0.0 for i in xrange(0,bdd_length)]
    prob = [0.0 for i in xrange(0,number_of_literals)]
    # Total probabilities
    formula_sat_prob = get_formula_sat_prob(bdd)
    print "Formula SAT Prob, P(psi) = {0}".format(formula_sat_prob)
    # Marginal probabilities
    get_marginal_prob(bdd_length-1, total_prob, formula_sat_prob, prob, bdd, var_ordering)
    #print "MP(x_i) = {0}".format(prob)
    #print "{0}".format(["{0} (pos={1}, index={2}, mark={3}, high={4}, low={5}, i={6})".format(bdd._get_node_label(v),v.id,v.index,v.visited,(v.high.id if v.high else "null"),(v.low.id if v.low else "null"),v.i) for v in bdd.vertices])
    for i in xrange(0,number_of_literals):
        #print prob[i]
        prob[i] = prob[i]/formula_sat_prob[1]
    return prob

##############################################
## Pruebas

def test():
    
    print "\n"
    
    def f1(a,b):
        return a or b
    
    print u"Fórmula: a or b"
    bdd = BDD(function=f1)
    prob = get_prob(bdd)
    print prob
    print prob == [2/3., 2/3.]
    print "\n"

    print u"Fórmula: (x1 and x2) or (x3 and x4) or (x5 and x6)"
    bdd = BDD(function="(x1 and x2) or (x3 and x4) or (x5 and x6)", variable_order=["x1","x2","x3","x4","x5","x6"])
    prob = get_prob(bdd)
    good_prob = [(23/37.), (23/37.), (23/37.), (23/37.), (23/37.), (23/37.)]
    print prob
    print good_prob
    print prob == good_prob
    #bdd.print_as_table()
    print "\n"

    def f3(a,b,c):
        return (not a) or b or c

    print u"Fórmula: (not a) or b or c"
    bdd = BDD(function=f3, variable_order=["a","b","c"])
    prob = get_prob(bdd)
    good_prob = [(3/7.), (4/7.), (4/7.)]
    bdd.print_as_table()
    print bdd.name
    print prob
    print good_prob
    print prob == good_prob
    print "\n"

    print u"Fórmula: (not A) or B or C or D"
    bdd = BDD("(not A) or B or C or D",variable_order=["A","B","C","D"])
    prob = get_prob(bdd)
    print bdd.name
    print prob
    print prob == [(7/15.), (8/15.), (8/15.), (8/15.)]
    print "\n"

    print u"Fórmula: (A and B) or (C and not D)"
    bdd = BDD("(A and B) or (C and not D)")
    prob = get_prob(bdd)
    print bdd.name
    print prob
    print prob == [(5/7.), (5/7.), (5/7.), (2/7.)]
    print "\n"

    print u"Fórmula: (not H or M) and (not M or not W)"
    bdd = BDD("(not H or M) and (not M or not W)")
    prob = get_prob(bdd)
    print bdd.name
    print prob
    print prob == [(1/4.), (1/2.), (1/4.)]
    print "\n"
    
test()
