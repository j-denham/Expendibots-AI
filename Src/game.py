import numpy as np
import queue

# Constants
BOARD_SIZE = 8
STACK_IDX = 0
COLOUR_IDX = 1
# All empty squares are also treated as white
WHITE = 0
BLACK = 1
LEGAL_BOOM_SHAPES = ((2, 2, 2), (3, 3, 2), (2, 3, 2), (3, 2, 2))

# TODO:
# Consider putting all meaningful constants here as all other classes
# will import from this file


class Game:

    # Returns the initial state of the game. State is represented
    # in the form of an 8x8x2 array, with 8x8 representing the board, with
    # each of these elements holding a stack count and colour value
    def initState():
        starting_shape = np.zeros((2, 2, 2), np.int8)
        starting_shape[:, :, STACK_IDX] += 1

        board = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), np.int8)

        for i in [0, BOARD_SIZE-2]:
            for j in range(0, BOARD_SIZE-1, 3):
                board[j:j+starting_shape.shape[0],
                      i:i+starting_shape.shape[1]] = starting_shape
            starting_shape[:, :, COLOUR_IDX] += 1

        return board

    # Returns the set of all possible actions a player can make
    def getAllActions(state, colour):
        allMoves = Game.getAllMoves(state, colour)
        allBooms = {("BOOM", i) for i in Game.getAllyCoords(state)}
        return allMoves.union(allBooms)

    # Returns the resultant state if a piece is moved
    def movePiece(n, prev, to, state):
        newState = state.copy()
        newState[prev[0], prev[1], STACK_IDX] -= n
        newState[to[0], to[1], STACK_IDX] += n
        # Can infer who's turn it is from indexing state with prev
        if newState[prev[0], prev[1], COLOUR_IDX] == BLACK:
            if newState[prev[0], prev[1], STACK_IDX] == 0:
                # Any empty tile is considered white
                newState[prev[0], prev[1], COLOUR_IDX] = WHITE
            newState[to[0], to[1], COLOUR_IDX] = BLACK
        return newState

    def legalMove(oldCoord, newCoord, state):
        if (Game.outOfBounds(newCoord[0]) or Game.outOfBounds(newCoord[1])):
            return False
        tile = state[newCoord[0], newCoord[1], :]
        # Can't move to a square occupied by enemy pieces
        if tile[COLOUR_IDX] == WHITE and tile[STACK_IDX] != 0:
            return False
        return True

    def getAllMoves(state, colour):
        # Coords should never be empty, otherwise the player has already lost
        allyCoords = Game.getAllyCoords(state, colour)
        allMoves = set()
        for i in allyCoords:
            stack = state[i[0], i[1], STACK_IDX]
            moveCoords = Game.getMoveCoords(i, stack, state)
            moveSet = Game.enumStackedMoves(i, stack, moveCoords)
            allMoves = allMoves.union(moveSet)
        return allMoves

    def getAllyCoords(state, colour):
        allies = np.where((state[:, :, COLOUR_IDX] == colour) & (state[:, :, STACK_IDX] != 0))
        print('ALLIES: ' + str(allies))
        # print('STATE: ' + str(state[:, :, COLOUR_IDX]))
        allyCoords = set(zip(allies[0], allies[1]))
        return allyCoords

    # Returns the set of coordinates to which a piece or stack
    # of pieces can move to
    def getMoveCoords(coord, stack, state):
        x, y = coord[0], coord[1]
        coords = set()
        for i in range(1, stack+1):
            moves = set(filter(lambda c: Game.legalMove(coord, c, state),
                               [(x+i, y), (x-i, y), (x, y+i), (x, y-i)]))
            coords = coords.union(moves)
        # print("Coords: " + str(coords))
        return coords

    def enumStackedMoves(coord, stack, moveCoords):
        moveSet = set()
        for i in moveCoords:
            for n in range(1, stack+1):
                moveSet.add(("MOVE", n, coord, i))
        return moveSet

    def outOfBounds(pos):
        return True if pos < 0 or pos > BOARD_SIZE - 1 else False

    # Returns the resultant state if a piece is boomed
    def boomPiece(coord, state):
        newState = state.copy()
        boomSets = Game.collectAllBoomed(coord, state)
        allBoomed = boomSets[0].union(boomSets[1])
        print("Caught in Boom: " + str(allBoomed))
        for i in allBoomed:
            newState[i[0], i[1], STACK_IDX] = 0
            newState[i[0], i[1], COLOUR_IDX] = WHITE
        return newState

    # Finds all the pieces caught in a chain explosion originating from a
    # single coordinate
    # Returns a doubleton 2D list with the sets of coordinates of enemy and
    # ally pieces repsectively caught in the chain explosion
    def collectAllBoomed(coord, state):
#         if state[coord[0], coord[1], COLOUR_IDX] == ALLY:
#             boomList = [set(), {coord}]
#         else:
#             boomList = [{coord}, set()]
        pieceColour = state[coord[0], coord[1], COLOUR_IDX]
        boomList = [set(), {coord}] if pieceColour == BLACK else [{coord}, set()]
        caught = queue.Queue()
        caught.put(coord)
        while caught.empty() is not True:
            i = caught.get()
            # print("CAUGHT ITERATION: " + str(i))
#             if state[i[0], i[1], COLOUR_IDX] == ALLY:
#                 boomList[ALLY].add(i)
#             else:
#                 boomList[ENEMY].add(i)
            caughtColour = state[i[0], i[1], COLOUR_IDX]
            boomList[caughtColour].add(i)
            newCaught = Game.collectBoomed(i, state)
            for j in newCaught:
                if j in boomList[BLACK] or j in boomList[WHITE]:
                    continue
                caught.put(j)
        return boomList

    # Finds the pieces caught in a singular explosion
    # Takes a 2-tuple x,y, returns set of 2-tuple coordinates of pieces caught
    def collectBoomed(boomed, state):
        xbounds, ybounds = Game.getBounds(boomed[0]), Game.getBounds(boomed[1])
        explosion = state[xbounds[0]:xbounds[1], ybounds[0]:ybounds[1], :]
        assert(explosion.shape in LEGAL_BOOM_SHAPES)
        pieces = np.where(explosion[:, :, STACK_IDX] > 0)
        caught = set(map(lambda i: Game.explosionToCoords(boomed, i),
                     np.stack(pieces, axis=1).tolist()))
        return caught

    # Returns the boundaries for an explosion centred on coord of boomed piece
    def getBounds(coord):
        # +2 as array slicing is non-inclusive on upper bound
        upper = BOARD_SIZE + 1 if Game.outOfBounds(coord + 1) else coord + 2
        lower = 0 if Game.outOfBounds(coord - 1) else coord - 1
        return (lower, upper)

    # Returns the coordinates of pieces caught in an 'explosion' slice
    # relative to the actual state
    def explosionToCoords(centre, coord):
        xoff = 0 if centre[0] == 0 else -1
        yoff = 0 if centre[1] == 0 else -1
        return (coord[0] + xoff + centre[0], coord[1] + yoff + centre[1])
