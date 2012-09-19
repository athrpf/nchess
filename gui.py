"""
This module is for testing how to plot a board
"""

import numpy as np
import cmath
import matplotlib.pyplot as plt

import threechess as thc

def plot_line(x1, x2, args):
    plt.plot(np.array([x1[0],x2[0]]), np.array([x1[1],x2[1]]), args)

class Rectangle:
    def __init__(self, x1, x2, x3, x4):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.x4 = x4
        self.node = None

    def plot(self, color='k'):
        plot_line(self.x1,self.x2, color)
        plot_line(self.x2,self.x3, color)
        plot_line(self.x3,self.x4, color)
        plot_line(self.x4,self.x1, color)
        if self.node and self.node.piece:
            draw_piece(self.node.piece, (self.x1+self.x2+ self.x3+self.x4)/4.)

def draw_piece(piece, center):
    color = piece.owner.plt_color
    if isinstance(piece, thc.King):
        plt.text(center[0], center[1], 'K', color=color)
    elif isinstance(piece, thc.Queen):
        plt.text(center[0], center[1], 'Q', color=color)
    elif isinstance(piece, thc.Bishop):
        plt.text(center[0], center[1], 'B', color=color)
    elif isinstance(piece, thc.Knight):
        plt.text(center[0], center[1], 'S', color=color)
    elif isinstance(piece, thc.Rook):
        plt.text(center[0], center[1], 'R', color=color)
    elif isinstance(piece, thc.Pawn):
        plt.text(center[0], center[1], 'P', color=color)


class CornerBoard(Rectangle):
    def __init__(self, x1, x2, x3, x4):
        """
        For consistency, and for the ordering of the sub-rectangles to work, the
        corner points of the CornerBoard must be ordered as follows:
        1. The actual corner point
        2. midpoint following in counter-clockwise (math-positive) way
        3. zero (center point of the board)
        4. final 2nd midpoint
        """
        Rectangle.__init__(self, x1, x2, x3, x4)
        self.rectangles = []

    def rectanglify(self, n_intervals_x=4, n_intervals_y=4):
        """
        generate sub-rectangles for this cornerboard.
        The rectangles are stored in the list self.rectangles.
        If you consider a right half board, they are ordered as follows:
        e4, e3, e2, e1, f4, f3, f2, f1, ...
        For a left half board, the ordering is
        d4, c4, b4, a4, d3, c3, b3, a3, d2, ...
        """
        points1 = [float(k)/n_intervals_x*self.x1+float(n_intervals_x-k)/n_intervals_x*self.x4 for k in range(n_intervals_x+1)]
        points2 = [float(k)/n_intervals_x*self.x2+float(n_intervals_x-k)/n_intervals_x*self.x3 for k in range(n_intervals_x+1)]
        for k in range(n_intervals_x):
            for j in range(n_intervals_y):
                p1 = points1[k]*float(j)/n_intervals_y + points2[k]*float(n_intervals_y-j)/n_intervals_y
                p2 = points1[k]*float(j+1)/n_intervals_y + points2[k]*float(n_intervals_y-j-1)/n_intervals_y
                p3 = points1[k+1]*float(j+1)/n_intervals_y + points2[k+1]*float(n_intervals_y-j-1)/n_intervals_y
                p4 = points1[k+1]*float(j)/n_intervals_y + points2[k+1]*float(n_intervals_y-j)/n_intervals_y
                self.rectangles.append(Rectangle(p1, p2, p3, p4))

    def plot(self, color='k'):
        Rectangle.plot(self, color)
        for r in self.rectangles:
            r.plot(color)

class HalfBoard:
    def __init__(self, cornerboard_left, cornerboard_right, playerID):
        self.cb_left = cornerboard_left
        self.cb_right = cornerboard_right
        self.owner = playerID

    def plot(self, color='k'):
        self.cb_left.plot(color)
        self.cb_right.plot(color)

    def connect_nodes(self, nodesdict):
        nleft = []
        for i in reversed(range(4)):
            nleft.extend([(self.owner, j, i) for j in reversed(range(4))])
        for idx, r in zip(nleft, self.cb_left.rectangles):
            r.node = nodesdict[idx]
        nright = []
        for i in range(4, 8):
            nright.extend([(self.owner, i, j) for j in reversed(range(4))])
        for idx, r in zip(nright, self.cb_right.rectangles):
            r.node = nodesdict[idx]


def generate_halfboards(n_players=3):
    # 1. compute the cornerpoints of the board
    n = n_players*2
    alpha = np.pi/n_players
    cornerpoints = []
    for k in range(n):
        c = cmath.rect(1,k*alpha)
        cornerpoints.append( np.array([c.real, c.imag]) )
    midpoints = []
    for k in range(-1,n-1):
        midpoints.append(0.5*(cornerpoints[k] + cornerpoints[k+1]))
    # 2. create cornerboards
    cornerboards = [CornerBoard(cornerpoints[k-1], midpoints[k], np.zeros(2), midpoints[k-1]) for (k,c) in enumerate(cornerpoints)]
    for c in cornerboards:
        c.rectanglify()
    halfboards = []
    for p in range(n_players):
        halfboards.append(HalfBoard(cornerboards[2*p], cornerboards[2*p+1], p))
    return halfboards

class GuiNChessGenerator(thc.NChessGenerator):
    def generate(self):
        self.gui_halfboards = generate_halfboards(self.n_players)
        nodeslist = []
        pieces = []
        players = []
        for p,ptype in zip(self.generate_playerIDs(), self.player_type_list):
            n, pi, pl = self.generate_halfboard(playerID=p, PlayerType=ptype)
            nodeslist.append(n)
            pieces.extend(pi)
            players.append(pl)
            self.gui_halfboards[p.id].connect_nodes(n)
        for p in range(self.n_players):
            self.glue_halfboards(nodeslist[p-1], players[p-1].playerID, nodeslist[p], players[p].playerID)
        nodes = thc.joindicts(nodeslist)
        return nodes, pieces, players

class GuiGame(thc.Game):
    def set_halfboards(self, generator):
        self.halfboards = generator.gui_halfboards

    def print_board(self, filename):
        plt.hold(False)
        plt.plot(0., 0., 'x')
        plt.hold(True)
        colorlist = ['k', 'y', 'b']
        for h, color in zip(self.halfboards, colorlist):
            h.plot(color)
        plt.savefig(filename)

    def play(self, max_moves=100):
        turn_idx = 0
        while not self.game_over and turn_idx < max_moves:
            turn_idx += 1
            filename = ('board%.3d.png' % turn_idx) #.format( turn_idx)
            self.play_next_move()
            self.print_board(filename)
        return self.winner



def test_plot_board():
    halfboards = generate_halfboards()
    colorlist = ['k', 'y', 'b']
    for (h,color) in zip(halfboards, colorlist):
        h.plot(color)
    plt.show()

def test_guigame():
    generator = GuiNChessGenerator()
    game = GuiGame(generator)
    game.set_halfboards(generator)
    game.play()


if __name__=='__main__':
    #test_plot_board()
    test_guigame()
