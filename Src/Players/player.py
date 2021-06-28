from ..game import Game
from ..strategy import Heuristic

# Constants
BOARD_SIZE = 8
STACK_IDX = 0
COLOUR_IDX = 1
WHITE = 0
BLACK = 1
LEGAL_BOOM_SHAPES = ((2, 2, 2), (3, 3, 2), (2, 3, 2), (3, 2, 2))


class Player:
    def __init__(self, colour):
        self.colour = WHITE if colour == 'white' else BLACK
        self.state = Game.initState()
        # self.strategy = Strategy()

    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        return Heuristic.evaluate(self.state, self.colour)

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
            self.state = Game.movePiece(n, prev, to, self.state)

        if action[0] == "BOOM":
            self.state = Game.boomPiece(action[1], self.state)
