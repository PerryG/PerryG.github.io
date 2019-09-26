# https://fivethirtyeight.com/features/step-1-game-theory-step-2-step-3-profit/


def profitForPlay(boardLen, play, allPlays):
    aggr = 0
    for pos in range(1, boardLen + 1):
        winNone = False
        winHalf = False
        for otherPlay in [otherPlay for otherPlay in allPlays if otherPlay != play]:
            if abs(otherPlay - pos) < abs(play - pos):
                winNone = True
                break
            if abs(otherPlay - pos) == abs(play - pos):
                winHalf = True

        if not winNone:
            if winHalf:
                aggr += pos / 2.0
            else:
                aggr += pos
    return aggr


def bestPlayFinalBoardAndVal(boardLen, prevPlays, numRemainingPlayers):
    profit = -1
    bestPos = -1
    if numRemainingPlayers == 0:
        for pos in [pos for pos in range(1, boardLen + 1) if pos not in prevPlays]:
            newPlays = prevPlays.copy()
            newPlays.add(pos)
            profitForPos = profitForPlay(boardLen, pos, newPlays)
            if profitForPos > profit:
                finalPlays = newPlays
                profit = profitForPos
                bestPos = pos
    else:
        for pos in [pos for pos in range(1, boardLen + 1) if pos not in prevPlays]:
            newPlays = prevPlays.copy()
            newPlays.add(pos)
            _, bestFinalPlays, _ = bestPlayFinalBoardAndVal(boardLen, newPlays, numRemainingPlayers - 1)
            finalProfit = profitForPlay(boardLen, pos, bestFinalPlays)
            if finalProfit > profit:
                profit = finalProfit
                bestPos = pos
                finalPlays = bestFinalPlays

    return bestPos, finalPlays, profit

bestPos, finalPlays, profit = bestPlayFinalBoardAndVal(10, set([]), 2)
print "bestPos: ", bestPos, "profit: ", profit
print finalPlays
