import numpy as np
import collections as col
import random

# Constants
BOARD_SIZE = 8
STACK_IDX = 0
COLOUR_IDX = 1
# All tiles that are not occupied by allied pieces are considered enemies
# even if empty
ENEMY = 0
ALLY = 1
LEGAL_BOOM_SHAPES = ((2, 2, 2), (3, 3, 2), (2, 3, 2), (3, 2, 2))


class Player:
    def __init__(self, colour):
        # TODO: Set up state representation.
        self.colour = colour
        self.state = self.initState()

    def initState(self):
        starting_shape = np.zeros((2, 2, 2), np.int8)
        starting_shape[:, :, STACK_IDX] += 1

        board = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), np.int8)
        # Starting rows initial positions of black and white respectively
        row_start = [0, BOARD_SIZE-2]

        # Initialise enemy pieces first
        if self.colour == "white":
            row_start.reverse()

        for i in row_start:
            for j in range(0, BOARD_SIZE-1, 3):
                board[j:j+starting_shape.shape[0],
                      i:i+starting_shape.shape[1]] = starting_shape
            starting_shape[:, :, COLOUR_IDX] += 1

        return board

    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        bestCoord, bestCount = self.getMostDesirableBoom(self.state)
        print("Coords: " + str(self.getAllyCoords(self.state)))
        # Make a move based on the desirable boom heuristic
        if bestCoord is not None:
            return ("BOOM", bestCoord)
        # Otherwise pick a random one
        # Can either call allActions or allMoves here
        allActions = list(self.getAllMoves(self.state))
        pickIndex = random.randint(0, len(allActions)-1)
        return allActions[pickIndex]

    # Returns the set of all possible actions a player can make
    def getAllActions(self, state):
        allMoves = self.getAllMoves(state)
        allBooms = {("BOOM", i) for i in self.getAllyCoords(state)}
        return allMoves.union(allBooms)

    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s
        turns) to inform your player about the most recent action. You should
        use this opportunity to maintain your internal representation of the
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        if action[0] == "MOVE":
            n, prev, to = action[1], action[2], action[3]
            self.state = self.movePiece(n, prev, to, self.state)

        if action[0] == "BOOM":
            self.state = self.boomPiece(action[1], self.state)

    # Returns the resultant state if a piece is moved
    def movePiece(self, n, prev, to, state):
        newState = state.copy()
        newState[prev[0], prev[1], STACK_IDX] -= n
        newState[to[0], to[1], STACK_IDX] += n
        # Can infer who's turn it is from indexing state with prev
        if newState[prev[0], prev[1], COLOUR_IDX] == ALLY:
            if newState[prev[0], prev[1], STACK_IDX] == 0:
                # Any tile that is not occupied by an ally piece
                # is considered an enemy even if it's empty
                newState[prev[0], prev[1], COLOUR_IDX] = ENEMY
            newState[to[0], to[1], COLOUR_IDX] = ALLY
        return newState

    def legalMove(self, oldCoord, newCoord, state):
        if (self.outOfBounds(newCoord[0]) or self.outOfBounds(newCoord[1])):
            return False
        tile = state[newCoord[0], newCoord[1], :]
        # Can't move to a square occupied by enemy pieces
        if tile[COLOUR_IDX] == ENEMY and tile[STACK_IDX] != 0:
            return False
        return True

    def getAllMoves(self, state):
        # Coords should never be empty, otherwise the player has already lost
        allyCoords = self.getAllyCoords(state)
        # FIX: These are printing properly
        allMoves = set()
        for i in allyCoords:
            stack = state[i[0], i[1], STACK_IDX]
            # print("Stack: " + str(stack))
            moveCoords = self.getMoveCoords(i, stack, state)
            # print("Move Coords: " + str(moveCoords))
            moveSet = self.enumStackedMoves(i, stack, moveCoords)
            # print("Move Set: " + str(moveSet))
            allMoves = allMoves.union(moveSet)
        # print("All Moves: " + str(allMoves))
        return allMoves

    def getAllyCoords(self, state):
        allies = np.where(self.state[:, :, COLOUR_IDX] == ALLY)
        allyCoords = set([(x, y) for (x, y) in zip(allies[0], allies[1])])
        return allyCoords

    # Returns the set of coordinates to which a piece or stack
    # of pieces can move to
    # FIX: This isn't returning any moves
    def getMoveCoords(self, coord, stack, state):
        x, y = coord[0], coord[1]
        coords = set()
        for i in range(1, stack+1):
            moves = set(filter(lambda c: self.legalMove(coord, c, state),
                               [(x+i, y), (x-i, y), (x, y+i), (x, y-i)]))
            coords = coords.union(moves)
        # print("Coords: " + str(coords))
        return coords

    def enumStackedMoves(self, coord, stack, moveCoords):
        moveSet = set()
        for i in moveCoords:
            for n in range(1, stack+1):
                moveSet.add(("MOVE", n, coord, i))
        return moveSet

    def outOfBounds(self, pos):
        return True if pos < 0 or pos > BOARD_SIZE - 1 else False

    # Returns the resultant state if a piece is boomed
    def boomPiece(self, coord, state):
        newState = state.copy()
        boomSets = self.collectAllBoomed(coord, state)
        allBoomed = boomSets[0].union(boomSets[1])
        for i in allBoomed:
            newState[i[0], i[1], STACK_IDX] = 0
            newState[i[0], i[1], COLOUR_IDX] = 0
        return newState

    # Finds all the pieces caught in a chain explosion originating from a
    # single coordinate
    # Returns a doubleton 2D list with the sets of coordinates of enemy and
    # ally pieces repsectively caught in the chain explosion
    def collectAllBoomed(self, coord, state):
        if state[coord[0], coord[1], COLOUR_IDX] == ALLY:
            boomList = [set(), {coord}]
        else:
            boomList = [{coord}, set()]
        caught = self.collectBoomed(coord, state)
        for i in caught:
            if state[i[0], i[1], COLOUR_IDX] == ALLY:
                boomList[ALLY].add(i)
            else:
                boomList[ENEMY].add(i)
            caught = caught.union(self.collectBoomed(i, state))
        # print("COLLECT BOOMLIST: " + str(boomList))
        return boomList

    # Finds the pieces caught in a singular explosion
    # Takes a 2-tuple x,y, returns set of 2-tuple coordinates of pieces caught
    def collectBoomed(self, boomed, state):
        xbounds, ybounds = self.getBounds(boomed[0]), self.getBounds(boomed[1])
        # May have to switch indexing due to cartesian coordinates
        explosion = state[xbounds[0]:xbounds[1], ybounds[0]:ybounds[1], :]
        assert(explosion.shape in LEGAL_BOOM_SHAPES)
        pieces = np.where(explosion[:, :, STACK_IDX] > 0)
        caught = set(map(lambda i: self.explosionToCoords(boomed, i),
                     np.stack(pieces, axis=1).tolist()))
        return caught

    # Returns the boundaries for an explosion centred on coord of boomed piece
    def getBounds(self, coord):
        # +2 as array slicing is non-inclusive on upper bound
        upper = BOARD_SIZE + 1 if self.outOfBounds(coord + 1) else coord + 2
        lower = 0 if self.outOfBounds(coord - 1) else coord - 1
        return (lower, upper)

    # Returns the coordinates of pieces caught in an 'explosion' slice
    # relative to the actual state
    def explosionToCoords(self, centre, coord):
        xoff = 0 if centre[0] == 0 else -1
        yoff = 0 if centre[1] == 0 else -1
        return (coord[0] + xoff + centre[0], coord[1] + yoff + centre[1])

    # Consider refactoring this, along with all other heurstics
    # into a Heuristic utility class
    def getBoomCount(self, coord, state):
        boomSets = self.collectAllBoomed(coord, state)
        # print("BOOMSETS: " + str(boomSets))
        boomCounter = [0, 0]
        for i in boomSets[ALLY]:
            boomCounter[ALLY] += state[i[0], i[1], STACK_IDX]
        for i in boomSets[ENEMY]:
            boomCounter[ENEMY] += state[i[0], i[1], STACK_IDX]
        # print("BOOMCOUNT COUNTER: " + str(boomCounter))
        return boomCounter

    # A desirable boom is one where there are more enemy pieces
    # lost then ally pieces. Returns the coordinates of the most
    # desirable boom, or None if not present
    def getMostDesirableBoom(self, state):
        allyCoords = self.getAllyCoords(state)
        # TEST: Asignment of both at the same time could be dodgy
        bestCoord, bestCount = (0, 0), [0, 0]
        for i in allyCoords:
            # print("ALLY: " + str(allyCoords))
            boomCounter = self.getBoomCount(i, state)
            difference = boomCounter[ENEMY] - boomCounter[ALLY]
            if difference > bestCount[ENEMY] - bestCount[ALLY]:
                # print("DIFFERENCE: " + str(difference))
                # print("COUNTER: " + str(boomCounter))
                bestCoord, bestCount = i, boomCounter
        # print(str(bestCount != [0, 0]), " BESTCOUNT: " + str(bestCount))
        # TEST: Asignment of both at the same time could be dodgy
        return (bestCoord, bestCount) if bestCount != [0, 0] else (None, None)
