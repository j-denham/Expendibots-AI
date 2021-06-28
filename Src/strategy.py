import random
from Src.game import Game

WHITE = 0
BLACK = 1
STACK_IDX = 0
COLOUR_IDX = 1


class Strategy:

    def __init__(self, search, evaluation):
        self.evaluation = evaluation
        self.search = search


class Evaluation:

    def evaluate(state, colour):
        pass


# Consider adding init function if
# heuristic specific values need to be kept track of (likely)
class Heuristic(Evaluation):

    def evaluate(state, colour):
        bestCoord, bestCount = Heuristic.getMostDesirableBoom(state, colour)
        # Make a move based on the desirable boom heuristic
        if bestCoord is not None:
            return ("BOOM", bestCoord)
        # Otherwise pick a random one
        # Can either call allActions or allMoves here
        allActions = list(Game.getAllMoves(state, colour))
        pickIndex = random.randint(0, len(allActions)-1)
        return allActions[pickIndex]

    def getBoomCount(coord, state):
        boomSets = Game.collectAllBoomed(coord, state)
        boomCounter = [0, 0]
        for i in boomSets[WHITE]:
            boomCounter[WHITE] += state[i[0], i[1], STACK_IDX]
        for i in boomSets[BLACK]:
            boomCounter[BLACK] += state[i[0], i[1], STACK_IDX]
        return boomCounter

    # A desirable boom is one where there are more enemy pieces
    # lost then ally pieces. Returns the coordinates of the most
    # desirable boom, or None if not present
    def getMostDesirableBoom(state, colour):
        allyCoords = Game.getAllyCoords(state, colour)
        # print('ALLY COORDS: ' + str(allyCoords))
        # print('LEN ALLIES: ' + str(len(allyCoords)))
        bestCoord, bestCount = None, 0
        # BUG: Returning positive values for friendly booms
        # for both sides
        for i in allyCoords:
            boomCounter = Heuristic.getBoomCount(i, state)
            difference = boomCounter[WHITE] - boomCounter[BLACK]
            if ((colour == WHITE and difference < bestCount) or
                (colour == BLACK and difference > bestCount)
            ):
                bestCoord, bestCount = i, abs(difference)

        print((bestCoord, bestCount))

        return (bestCoord, bestCount)
