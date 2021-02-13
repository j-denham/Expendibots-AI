import numpy as np
import collections as col

# Constants
BOARD_SIZE = 8
STACK_IDX = 0
COLOUR_IDX = 1
# All tiles that are not occupied by allied pieces are cosidered enemies
# even if empty
ENEMY = 0
ALLY = 1


class Player:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your
        program will play as (White or Black). The value will be one of the
        strings "white" or "black" correspondingly.
        """
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
        # Dummy actions for bug testing. Just moves everything into a corner
        # and booms
        # TODO: Implement this function with some basic heursitics
        allies = np.where(self.state[:, :, COLOUR_IDX] == ALLY)
        # ally_coords = np.stack(allies, axis=1).toList()
        # TEST: Below is pretty suss
        allyCoords = col.deque([(x, y) for (x, y) in zip(allies[0], allies[1])])
        # Coords should never be empty, otherwise the player has already lost
        coords = allyCoords.popleft()
        if self.legalMove(coords, (coords[0]+1, coords[1])):
            return ("MOVE", 1, coords, (coords[0]+1, coords[1]))
        elif self.legalMove(coords, (coords[0], coords[1]+1)):
            return ("MOVE", 1, coords, (coords[0], coords[1]+1))
        else:
            return ("BOOM", coords)

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


    # TODO: Will most likely need to be changed when action is changed
    def legalMove(self, oldCoord, newCoord):
        return not (self.outOfBounds(newCoord[0]) or self.outOfBounds(newCoord[1]))

    def outOfBounds(self, pos):
        return True if pos < 0 or pos > BOARD_SIZE - 1 else False

    # Returns the resultant state if a piece is boomed
    def boomPiece(self, coord, state):
        newState = state.copy()
        boomSets = self.collectAllBoomed(coord)
        allBoomed = boomSets[0].union(boomSets[1])
        for i in allBoomed:
            newState[i[0], i[1], STACK_IDX] = 0
            newState[i[0], i[1], COLOUR_IDX] = 0
        return newState

    # Finds all the pieces caught in a chain explosion originating from a
    # single coordinate
    # Returns a doubleton 2D list with the lists of coordinates of enemy and
    # ally pieces repsectively caught in the chain explosion
    def collectAllBoomed(self, coord, state):
        if state[coord[0], coord[1], COLOUR_IDX] == self.colour:
            boomList = [{}, {coord}]
        else:
            boomList = [{coord}, {}]
        caught = self.collectBoomed(coord)
        for i in caught:
            if state[i[0], i[1], COLOUR_IDX] == self.colour:
                boomList[ALLY].add(i)
            else:
                boomList[ENEMY].add(i)
            caught.append(self.collectBoomed)

    # Finds the pieces caught in a singular explosion
    # Takes a 2-tuple x,y, returns list 2-tuple coordinates of pieces caught
    def collectBoomed(self, boomed, state):
        xbounds, ybounds = self.getBounds(boomed[0]), self.getBounds(boomed[1])
        # May have to switch indexing due to cartesian coordinates
        explosion = state[xbounds[0]:xbounds[1], ybounds[0]:ybounds[1], :]
        assert(explosion.shape() == (3, 3))
        pieces = np.where(explosion[:, :, STACK_IDX] > 0)
        caught = np.stack(pieces, axis=1).toList()
        return caught

    # Returns the boundaries for an explosion centred on coord of boomed piece
    def getBounds(self, coord):
        # +2 as array slicing is non-inclusive on upper bound
        upper = BOARD_SIZE + 1 if self.outOfBounds(coord + 1) else coord + 2
        lower = 0 if self.outOfBounds(coord - 1) else coord - 1
        return (lower, upper)


# class Heurisics:
#     def __init__(self):

