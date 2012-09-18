
from numpy.random import shuffle, random_integers
import threechess as thc
import gui

class RandomPlayer:
    def __init__(self, playerID):
        self.playerID = playerID

    def get_move_list(self, game):
        l = range(game.n_players)
        shuffle(l)
        return l

    def get_move(self, game):
        my_pieces = game.get_pieces(self.playerID)
        possible_moves = []
        for p in my_pieces:
            possible_moves.extend([thc.Move(p, p.position, e) for e in p.get_possible_moves()])
        i = random_integers(0, len(possible_moves)-1)
        return possible_moves[i]

    def __str__(self):
        return "Random Player " + str(self.playerID)

if __name__=='__main__':
    generator = gui.GuiNChessGenerator(player_type_list=[RandomPlayer]*3)
    game = gui.GuiGame(generator)
    game.set_halfboards(generator)
    winner = game.play(max_moves=100)
    print "The winner is " , winner
