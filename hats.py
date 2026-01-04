import itertools as iter
from random import choice, choices
from math import log2, factorial, pow

def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

def simOnce(p1Strat, p2Strat, p1Hats, p2Hats):
    return p1Hats[p1Strat(p2Hats)] and p2Hats[p2Strat(p1Hats)]

def simForAllLenN(p1Strat, p2Strat, n):
    allPossible = list(iter.product([0, 1], repeat = 2*n))
    success = sum([simOnce(p1Strat, p2Strat, h[0:n], h[n:2*n]) for h in allPossible])
    return 1.0 * success / len(allPossible)

def simForAllNonMonochromeLenN(p1Strat, p2Strat, n):
    allPossible = list(iter.product([0, 1], repeat = 2*n))
    results = [
        simOnce(p1Strat, p2Strat, h[0:n], h[n:2*n])
        for h in allPossible
        if 0 < sum(h[0:n]) < n and 0 < sum(h[n:2*n]) < n]
    return sum(results), len(results)

def simForAllSingleMonochromeLenN(p1Strat, p2Strat, n):
    allPossible = list(iter.product([0, 1], repeat = 2*n))
    results = [
        simOnce(p1Strat, p2Strat, h[0:n], h[n:2*n])
        for h in allPossible
        if (sum(h[0:n]) % n == 0) + (0 == sum(h[n:2*n]) % n) == 1]
    return sum(results), len(results)

def simNTimes(p1Strat, p2Strat, numHats, n):
    success = 0
    for i in range(n):
        hats1 = choices([0, 1], k=numHats)
        hats2 = choices([0, 1], k=numHats)
        success += simOnce(p1Strat, p2Strat, hats1, hats2)
    return 1.0 * success / n

def pickFirstStrat(hats):
    for i, h in enumerate(hats):
        if h == 1:
            return i
    return 0

def paperStrat(hats):
    assert(len(hats) == 3)
    if sum(hats) == 3 or sum(hats) == 0:
        return 0
    if hats[0]:
        if not hats[2]:
            return 0
        return 1
    if hats[1]:
        return 2
    return 1

def randomSetStrat(hats):
    options = [i for i, h in enumerate(hats) if h == 1]
    if len(options) == 0:
        return 0
    return choice(options)

def perryStrat4(hats):
    assert(len(hats) == 4)
    if sum(hats) == 4 or sum(hats) == 0:
        return 0
    if hats[0]:
        if not hats[2]:
            return 0
        return 1
    if hats[1]:
        return 2
    return 1

def permuteStrat(strat, permutation):
    def retStrat(hats):
        return permutation[strat(hats)]
    return retStrat

# print(simForAllLenN(pickFirstStrat, pickFirstStrat, 3))
# print(simForAllLenN(paperStrat, paperStrat, 3))
# print(simNTimes(paperStrat, paperStrat, 3, 1000000))
# print(simNTimes(pickFirstStrat, pickFirstStrat, 3, 1000000))
# print(simNTimes(randomSetStrat, randomSetStrat, 3, 1000000))

# permStrat = permuteStrat(paperStrat, [1, 0, 2])
# print(simForAllLenN(permStrat, permStrat, 3))

# Appears to aproach but never reach 1.0 for large n, suggesting
# you can send arbitrarily close to 1 bit. Not that this suggests
# a success probability of 3/4ths when p1 is right, or 3.8 overall!
def maxExpectedBits(n):
    sum = 0
    for k in range(0, n-1):
        sum += 2 * (log2(n) - log2(k+1)) * choose(n-1, k) / pow(2, n)
    return sum

len2template = [1, 0]
len2reverseTemplate = [1, 0]

len3template = [2, 1, 0]
len3reverseTemplate = [2, 0, 1]

len4template = [4, 2, 2, 0]
len4reverseTemplate = [4, 0, 2, 2]

len5template = [6, 4, 3, 2, 0]
len5reverseTemplate = [6, 0, 2, 3, 4]

len6template = [12, 8, 6, 5, 5, 0]
len6reverseTemplate = [12, 0, 5, 5, 6, 8]

def templateScores(hats, template):
    assert(len(hats) == len(template))
    scores = [0 for h in hats]
    for i, h in enumerate(hats):
        if h:
            for j, p in enumerate(template):
                scores[(i + j) % len(template)] += p
    return scores

def templateStratFunc(template):
    def strat(hats):
        scores = templateScores(hats, template)
        return scores.index(max(scores))
    return strat

print(simForAllLenN(templateStratFunc(len6template), templateStratFunc(len6reverseTemplate), 6))
print(simForAllLenN(templateStratFunc(len5template), templateStratFunc(len5reverseTemplate), 5))
print(simForAllLenN(templateStratFunc(len4template), templateStratFunc(len4reverseTemplate), 4))
print(simForAllLenN(templateStratFunc(len3template), templateStratFunc(len3reverseTemplate), 3))
print(simForAllLenN(templateStratFunc(len2template), templateStratFunc(len2reverseTemplate), 2))

# print(simForAllNonMonochromeLenN(paperStrat, paperStrat, 3))
# print(simForAllSingleMonochromeLenN(paperStrat, paperStrat, 3))
# print(simForAllNonMonochromeLenN(templateStratFunc(len5template), templateStratFunc(len5reverseTemplate), 5))
# print(simForAllSingleMonochromeLenN(templateStratFunc(len5template), templateStratFunc(len5reverseTemplate), 5))

# print(simForAllLenN(templateStratFunc(len4template), templateStratFunc(len4reverseTemplate), 4))
# print(simForAllNonMonochromeLenN(templateStratFunc(len4template), templateStratFunc(len4reverseTemplate), 4))
# print(simForAllSingleMonochromeLenN(templateStratFunc(len4template), templateStratFunc(len4reverseTemplate), 4))



# print(simForAllNonMonochromeLenN(templateStratFunc(len3template), templateStratFunc(len3reverseTemplate), 3))
# print(simForAllSingleMonochromeLenN(templateStratFunc(len3template), templateStratFunc(len3reverseTemplate), 3))


# print(simForAllNonMonochromeLenN(templateStratFunc(len2template), templateStratFunc(len2reverseTemplate), 2))
# print(simForAllSingleMonochromeLenN(templateStratFunc(len2template), templateStratFunc(len2reverseTemplate), 2))
