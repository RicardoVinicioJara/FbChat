"""
'Stubborn Greedy' algorithm.

The number of branches followed would be:

    N + (N * N * D)

where:

    N is the number of moves per turn
    D is the depth

So, if there are 4 possible moves per turn and the depth is 10,
then:

    4 + (4 * 4 * 10) = 164 branches followed.

Compare this to MiniMax (without alpha/beta pruning):

    4 ^ 10 = 1,048,576 branches followed

"""

import copy


def stubborn_greedy(game, final_depth, scoring):

    if not scoring:
        scoring = lambda g: g.scoring()

    possible_moves = game.possible_moves()
    best_move = None
    best_value = None

    for move in possible_moves:
        root_game = copy.deepcopy(game)
        root_game.make_move(move)

        if final_depth <= 1:
            root_value = scoring(root_game)
        else:
            value = down_the_rabbit_hole(root_game, final_depth, scoring)
            if final_depth % 2 == 0:  # this AI only works on 2 player games
                root_value = value
            else:
                root_value = -1 * value

        if (best_value is None) or (root_value > best_value):
            best_value = root_value
            best_move = move

    return best_move


def down_the_rabbit_hole(root_game, final_depth, scoring):
    """
    Follow the path of "best moves" as seen by each player to
    extrapolate a final value. Do not consider any other branches
    other than the one with the immediate best score. aka "greedy"
    """
    best_branch_game = root_game

    for depth in range(2, final_depth):
        branch_possible_moves = best_branch_game.possible_moves()
        best_branch_value = None
        for branch_move in branch_possible_moves:
            test_game = copy.deepcopy(best_branch_game)
            test_game.make_move(branch_move)
            value = scoring(test_game)
            if (best_branch_value is None) or (value > best_branch_value):
                best_branch_value = value
                best_branch_game = copy.deepcopy(test_game)

    return best_branch_value, best_branch_game.nplayer


class StubbornGreedy:
    """
    This implements "stubborn greedy" algorithm. The following example shows
    how to setup the AI and play a Connect Four game:

        >>> from easyAI.games import ConnectFour
        >>> from easyAI import StubbornGreedy, Human_Player, AI_Player
        >>> game = ConnectFour([Human_Player(), AI_Player(StubbornGreedy(20))])
        >>> game.play()

    One of the benefits of this AI is that the scope of search is O(n). PLus,
    no recursion is used.

    The downside of this AI is that it is very likely going to give you a
    non-ideal answer; especially compared to SSS and Negamax.

    Parameters
    -----------

    depth:
      How many moves in advance should the AI think ?
      (2 moves = 1 complete turn)

    scoring:
      A function f(game)-> score. If no scoring is provided
         and the game object has a ``scoring`` method it ill be used.
      The most positive scoring result predicted is chosen.

    win_score:
      For keep similarity to other algorithms, this parameter is supported
      but it is not actually used.

    tt:
      A transposition table (a table storing game states and moves).
      For keep similarity to other algorithms, this parameter is supported
      but it is not actually used.

    """

    def __init__(self, depth, scoring=None, win_score=None, tt=None):
        self.scoring = scoring
        self.depth = depth
        self.tt = tt
        self.win_score = win_score

    def __call__(self, game):
        """
        Returns the AI's best move given the current state of the game.
        """

        move_selected = stubborn_greedy(game, self.depth, self.scoring)
        game.ai_move = move_selected
        return move_selected
