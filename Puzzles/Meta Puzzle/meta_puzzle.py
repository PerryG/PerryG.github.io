from math import sqrt

# http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def memoize(f):
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

# Returns true for 1, since really what we want is not composite
@memoize
def isPrime(x):
    if x <= 3:
        return True
    for f in range(2, int(sqrt(x)) + 1):
        if x % f == 0:
            return False
    return True

@memoize
def factorsOf(x):
    factors = []
    for f in xrange(1, x + 1):
        if x % f == 0:
            factors.append(f)
    return factors

def factorsSumToOneOverComposite(lst):
    numFactors = len(lst)
    factorPairs = []
    for i in xrange((numFactors + 1) / 2):
        if not isPrime(lst[i] + lst[numFactors - 1 - i] - 1):
            factorPairs.append((lst[i], lst[numFactors - 1 - i]))
    return factorPairs

@memoize
def inF(x):
    return len(factorsSumToOneOverComposite(factorsOf(x)[1:-1])) > 0

for i in xrange(2, 10000):
    if inF(i):
        pairs = factorsSumToOneOverComposite(factorsOf(i))
        numValidPairs = 0
        validPairs = []
        for pair in pairs:
            pairSum = pair[0] + pair[1]
            for m in xrange(pairSum / 2 + 1):
                if m != pair[0] and inF(m * (pairSum - m)):
                    validPairs.append(pair)
                    break
            if len(validPairs) > 1:
                break
        if len(validPairs) == 1:
            print validPairs[0]

