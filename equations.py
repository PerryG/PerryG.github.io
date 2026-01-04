from itertools import combinations
from collections import defaultdict
from time import clock
from random import shuffle

def tripletWorks(tripletSet):
    a, b, c = sorted(tripletSet)
    return (a + b == c) or (a * b == c)

class StateHolder:
    # When constructing from scratch
    @classmethod
    def buildInitStateHolder(state, N):
        setOfNums = frozenset(range(1, 3 * N + 1))
        candidateTriplets = tuple(c for c in combinations(setOfNums, 3) if tripletWorks(c))[::-1]
        return StateHolder(setOfNums, candidateTriplets)

    # When constructing from raw data
    def __init__(self, setOfNums, candidateTriplets):
        self.setOfNums_ = setOfNums

        self.numInCandidatesCountMap_ = defaultdict(int)
        for c in candidateTriplets:
            for n in c:
                self.numInCandidatesCountMap_[n] += 1

        self.candidateTriplets_ = candidateTriplets


    def getCandidateTriplets(self):
        return self.candidateTriplets_

    def empty(self):
        return len(self.setOfNums_) == 0

    def getSetOfNums(self):
        return self.setOfNums_


    def __hash__(self):
      return hash(self.setOfNums_)

    def getFilteredStateHolder(self, filterByTriplet):
        filterByTripletSet = set(filterByTriplet)
        newSetOfNums = self.setOfNums_ - filterByTripletSet
        newCandidateTriplets = tuple(
            c for c in self.candidateTriplets_ if not set(c).intersection(filterByTripletSet)
        )

        return StateHolder(newSetOfNums, newCandidateTriplets)

    def impossibleHeuristic(self):
        if len(self.candidateTriplets_) < len(self.setOfNums_) / 3:
            return True

        for num in self.setOfNums_:
            if self.numInCandidatesCountMap_[num] == 0:
                return True

        return False


def getSoln(N):
    stateHolder = StateHolder.buildInitStateHolder(N)
    return getSolnWithCandidateTriplets(stateHolder, 0)

setOfNumsCache = dict()

def getSolnWithCandidateTriplets(stateHolder, depth):
    global setOfNumsCache

    if stateHolder.empty():
        return []

    if hash(stateHolder) in setOfNumsCache:
        return setOfNumsCache[hash(stateHolder)]

    if stateHolder.impossibleHeuristic():
        setOfNumsCache[hash(stateHolder)] = None
        return None

    i = 0
    for c in stateHolder.getCandidateTriplets():
        i = i + 1
        if True:
            print('Depth: %d. Candidate: %d out of %d' % (depth, i, len(stateHolder.getCandidateTriplets())))
        filteredState = stateHolder.getFilteredStateHolder(c)
        subSoln = getSolnWithCandidateTriplets(filteredState, depth+1)
        if subSoln is not None:
            subSoln.append(sorted(c))
            setOfNumsCache[hash(stateHolder)] = subSoln[:]
            return subSoln

    setOfNumsCache[hash(stateHolder)] = None
    return None

start = clock()
for N in [10, 15]:
    soln = getSoln(N)[::-1]
    print("%d: %s" % (N, soln))
    # print("%d Mult triples: %s" % (N, [c for c in soln if c[0] * c[1] == c[2]]))
print("Time: %f" % (clock() - start))
