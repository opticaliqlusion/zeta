#
#   This script naively brute force the algebraic form
#   of expressions in an attempt to mine a number's regular form
#

import os
import sys
import sympy
import itertools
import pprint
import copy

from sympy import I, E
from mpmath import pi as PI

from sympy import binomial

# small helper class to make using, printing ops easier
class Operation():
    def __init__(self, name, functor):
        self.name = name
        self.f = functor
    def __call__(self, x, y):
        return self.f(x,y)
    def __str__(self):
        return self.name
    def __repr__(self):
        return str(self)

class Expression():
    def __init__(self, data):
        self.data = data
    def __str__(self):
        return str(self.data)
    def __repr__(self):
        return str(self)

def reduce(args):
    stack = []

    while len(args) > 0:

        token = args.pop()

        if isinstance(token, Operation):
            const1 = stack.pop().data
            const2 = stack.pop().data
            result = token(const1, const2)
            stack.append(Expression(result))
        else:
            stack.append(token)

    if len(stack) != 1:
        raise IndexError()

    ret = stack.pop().data
    return ret

def is_valid_rpn(tokens):
    nops  = len([i for i in tokens if isinstance(i, Operation)])
    exprs = len([i for i in tokens if isinstance(i, Expression)])

    if nops != exprs -1:
        return False

    stack_count = 0
    for i in tokens[::-1]:
        if isinstance(i, Expression):
            stack_count += 1
        elif isinstance(i, Operation) and stack_count >= 2:
            stack_count -= 1
        else:
            return False

    return True

def main():

    tokens = [
        Expression(1),
        Expression(2),
        Expression(3),
        Expression(5),
        Expression(-1),
        Expression(I),
        Expression(E),
        Expression(PI),
        Operation('Add', lambda x,y : sympy.Add(x,y)),
        Operation('Sub', lambda x,y : sympy.Add(x,  sympy.Mul(sympy.Integer(-1), y))),
        Operation('Mul', lambda x,y : sympy.Mul(x,y)),
        Operation('Div', lambda x,y : sympy.Mul(x, sympy.Pow(y, sympy.Integer(-1)))),
        Operation('Pow', lambda x,y : sympy.Pow(x,y)),
    ]

    # increment this to expand the search...
    # small increases in this explode the search space
    stack_size = 3

    # the number we're looking for
    target = 14.134725141734693790457251983562470270784257115699243175685567460149963429809256764949010393171561012779202971548797436766142691469882254582505363239447137780413381237205970549621955865860200555566725836010773700205410982661507542780517442591306254481978651072304938725629738321577420395215725674809332140034990468034346267314420920377385487141378317356396995365428113079680531491688529067820822980492643386667346233200787587617920056048680543568014444246510655975686659032286865105448594443206240727270320942745222130487487209241238514183514605427901524478338354254533440044879368067616973008190007313938549837362150130451672696838920039176285123212854220523969133425832275335164060169763527563758969537674920336127209259991730427075683087951184453489180086300826483125169112710682910523759617977431815170713545316775495153828937849036474709727019948485532209253574357909226125247736595518016975233461213977316005354125926747455725877801472609830808978600712532087509395997966660675378381214891908864977277554420656532052405

    # cant forget to optimize -- keep a hash table of already-computed answers
    memoize_dict = {}

    # keep a list of the best guesses
    best_guesses = []
    max_best_guesses = 10

    # test to make sure phi works
    phi = 1.6180339887498948482
    test_args = [
        Expression(2),
        Expression(1),
        Expression(2),
        Expression(1),
        Operation('Div', lambda x,y : sympy.Mul(x, sympy.Pow(y, sympy.Integer(-1)))),
        Expression(5),
        Operation('Pow', lambda x,y : sympy.Pow(x,y)),
        Operation('Add', lambda x,y : sympy.Add(x,y)),
        Operation('Div', lambda x,y : sympy.Mul(x, sympy.Pow(y, sympy.Integer(-1)))),
    ]
    test = reduce(test_args[::-1])
    test_tolerance = 0.000000001
    assert(test - phi < test_tolerance)

    # brute force the maths
    # ... forever
    while True:

        # we want updates to know how far along we are
        total_iters = binomial(len(tokens) + stack_size - 1, stack_size) * sympy.factorial(stack_size)
        i = 0
        last_percent = 0.0

        for args in itertools.combinations_with_replacement(tokens, stack_size):
            for perms in itertools.permutations(args):

                # update our progress, if we've made enough progress
                percent_done = float(i) / float(total_iters)
                if (percent_done) - last_percent > 0.01:
                    print('[{} / %{:02}] {}'.format(stack_size, int(percent_done*100), best_guesses[0] if best_guesses else 'No Guesses'))
                    last_percent = percent_done

                i += 1

                if str(perms) in memoize_dict:
                    continue
                
                if not is_valid_rpn(perms):
                    memoize_dict[str(perms)] = 'INVALID'
                    continue

                try:
                    expression = reduce(list(perms))
                except:
                    continue

                if str(expression) in memoize_dict:
                    # check to see if we've already done the work
                    guess = memoize_dict[str(perms)]
                else:
                    # otherwise, calculate the result and record the answer
                    guess = expression.evalf()
                    memoize_dict[str(perms)] = guess

                # how good of a guess was this?
                delta = sympy.Abs(guess - target)

                try:
                    best_guesses = sorted(best_guesses + [(delta, guess, perms)], key=lambda x : x[0])[:max_best_guesses]
                except:
                    continue

        print('done after: {}'.format(i))
        print('stack size: {}'.format(stack_size))
        pprint.pprint(best_guesses)
        stack_size += 1

    return

if __name__ == "__main__":
    main()
