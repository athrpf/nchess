

all_directions = ('e','ne','n','nw','w','sw','s','se')

class Node:
    def __init__(self, playerID, nodeID):
        self.nodeID = nodeID
        self.neighbors = {}
        for d in all_directions:
            self.neighbors[d] = []
        self.owner = playerID
        self.piece = None

    def get_next_nodes(self, moving_playerID, direction):
        if moving_playerID==self.owner:
            return self.neighbors[direction]
        else:
            return self.neighbors[(direction+4)%8]

    def print_full(self, str):
        s  = "Node " + str(self.nodeID) + " owned by player " + str(self.owner) + "\n"
        s += "neighbors:\n"
        for d in all_directions:
            s += str(d) + ": "
            for n in self.neighbors[d]:
                s += str(n.nodeID) + ","
            s += "\n"
        return s

    def __str__(self):
        return str(self.nodeID)

class Piece:
    def __init__(self, playerID, position):
        self.owner = playerID
        self.position = position


class King(Piece):
    def get_possible_moves(self):
        retval = []
        for d in all_directions:
            retval.extend(self.position.get_next_nodes(self.owner, d))
        return retval

    def __str__(self):
        s = "King at " + str(self.position)
        return s

class Pawn(Piece):
    def get_possible_moves(self):
        raise NotImplementedError()

class Player:
    def __init__(self, playerID):
        self.playerID = playerID

    def get_move_list(self, game):
        raise NotImplementedError()

    def get_move(self, game):
        raise NotImplementedError()

    def __str__(self):
        return "Player " + str(self.playerID)


class Move:
    def __init__(self, piece, startnode, endnode):
        self.piece = piece
        self.start = startnode
        self.end   = endnode

    def __str__(self):
        return "Move " + str( self.piece) + " from " + str(self.start) + " to " + str(self.end)

class ConsolePlayer(Player):
    def get_move(self, game):
        print "It is your turn. (press h for help)"
        while True:
            decision = raw_input()
            if decision =='h':
                self.print_help()
                continue
            elif decision =='p':
                self.print_pieces(game)
                continue
            elif decision =='m':
                return self.decide_move(game)

    def decide_move(self, game):
        pieces = game.get_pieces(self.playerID)
        print "You have the following pieces:"
        for (k, p) in enumerate(pieces):
            print k, p
        print "Which one would you like to move?"
        id = int(input())
        assert(id>=0)
        assert(id<len(pieces))
        p = pieces[id]
        print "This piece can move to the following nodes:"
        moves = p.get_possible_moves()
        for (k,m) in enumerate(moves):
            print k,m
        id = int(input())
        assert(id>=0)
        assert(id<len(moves))
        retval = Move(p, p.position, moves[id])
        return retval

    def print_help(self):
        print "You have the following options:"
        print "h : print this help"
        print "m : make a move"
        print "p : print the pieces and their location"

    def print_pieces(self, game):
        pieces = game.get_pieces()
        for p in pieces:
            print p

    def get_move_list(self, game):
        return range(game.n_players)

    def __str__(self):
        return "ConsolePlayer " + str(self.playerID)

class Game:
    def __init__(self, generator):
        self.nodes, self.pieces, self.players = generator.generate()
        self.move_list = list(self.players)
        self.move_decision_list = list(self.players)
        self.n_players = len(self.players)
        self.killed_pieces = []
        self.game_over = False
        self.winner = None

    def play_next_move(self):
        if (len(self.move_decision_list)<=self.n_players):
            self.move_decision_list.extend(self.players)
        if (len(self.move_list)<=self.n_players):
            move_decider = self.move_decision_list.pop(0)
            print "The new order of moves must be decided on by player ", move_decider.playerID
            print "The current order of moves is ", [str(p) for p in self.move_list]
            new_moves = [self.players[k] for k in move_decider.get_move_list(self)]
            print "The new order of moves is " , [str(m) for m in new_moves]
            assert(len(new_moves)==self.n_players)
            self.move_list.extend(new_moves)
            print "The next moves will be ", [str(p) for p in self.move_list]
        mover = self.move_list.pop(0)
        print "It is the turn of", mover
        move = mover.get_move(self)
        self.game_over = self.make_move(move)
        if self.game_over:
            self.winner = mover

    def play_game(self):
        while not self.game_over:
            self.play_next_move()
        return self.winner

    def make_move(self, move):
        #p = self.pieces[move.pieceID]
        print move
        p = move.piece
        assert(p.position==move.start)
        assert(p==move.start.piece)
        move.start.piece = None
        p.position = move.end
        if isinstance(move.end.piece, King):
            return True
        if move.end.piece is not None:
            self.killed_pieces.append(move.end.piece)
        move.end.piece = p
        return False

    def get_pieces(self, playerID=None):
        if playerID is None:
            return self.pieces
        retval = []
        for p in self.pieces:
            if p.owner == playerID:
                retval.append(p)
        return retval


    def __str__(self):
        s = ""
        for n in self.nodes.itervalues():
            s += str(n)
        return s

def joindicts(dict1, dict2):
    retval = {}
    for (k,v) in dict1.iteritems():
        retval[k] = v
    for (k,v) in dict2.iteritems():
        retval[k] = v
    return retval

class TwoChessGenerator:
    def __init__(self, number_of_rows=4, number_of_columns=8):
        self.n_rows = number_of_rows
        self.n_cols = number_of_columns

    def generate_halfboard(self, playerID):
        rows = range(self.n_rows)
        cols = range(self.n_cols)
        nodes = {}
        for r in rows:
            for c in cols:
                nodes[(playerID, c, r)] = Node(playerID, (playerID, c, r))
        for c in cols:
            for r in rows:
                if c<(self.n_cols-1):
                    nodes[(playerID, c, r)].neighbors['e'] = [nodes[(playerID, c+1, r)]]
                    if r>0:
                        nodes[(playerID, c, r)].neighbors['se'] = [nodes[(playerID, c+1, r-1)]]
                    if r<3:
                        nodes[(playerID, c, r)].neighbors['ne'] = [nodes[(playerID, c+1, r+1)]]

                if c>0:
                    nodes[(playerID, c, r)].neighbors['w'] = [nodes[(playerID, c-1, r)]]
                    if r>0:
                        nodes[(playerID, c, r)].neighbors['sw'] = [nodes[(playerID, c-1, r-1)]]
                    if r<(self.n_rows-1):
                        nodes[(playerID, c, r)].neighbors['nw'] = [nodes[(playerID, c-1, r+1)]]
                if r>0:
                    nodes[(playerID, c, r)].neighbors['s'] = [nodes[(playerID, c, r-1)]]
                if r<(self.n_rows-1):
                    nodes[(playerID, c, r)].neighbors['n'] = [nodes[(playerID, c, r+1)]]

        if self.n_cols is not 8:
            raise NotImplementedError()
        pieces = []
        king = King(playerID, nodes[(playerID,4,0)])
        nodes[(playerID,4,0)].piece = king
        pieces.append(king)
        player = ConsolePlayer(playerID)
        return nodes, pieces, player

    def glue_halfboards(self, board1, playerID1, board2, playerID2):
        """
        Attach two half-boards to each other along a quarter-side:

        The right part of board1 is attached to the left part of board2.
        """
        for c in range(self.n_cols/2):
            board1[(playerID1, c+self.n_cols/2, self.n_rows-1)].neighbors['n'].append(board2[(playerID2, self.n_cols/2-c-1, self.n_rows-1)])
            board2[(playerID2, self.n_cols/2-c-1, self.n_rows-1)].neighbors['n'].append(board1[(playerID1, c+self.n_cols/2, self.n_rows-1)])
            board1[(playerID1, c+self.n_cols/2, self.n_rows-1)].neighbors['nw'].append(board2[(playerID2, self.n_cols/2-c, self.n_rows-1)])
            board2[(playerID2, self.n_cols/2-c-1, self.n_rows-1)].neighbors['ne'].append(board1[(playerID1, c+self.n_cols/2-1, self.n_rows-1)])
            if c<(self.n_cols/2-1):
                board1[(playerID1, c+self.n_cols/2, self.n_rows-1)].neighbors['ne'].append(board2[(playerID2, self.n_cols/2-c-2, self.n_rows-1)])
                board2[(playerID2, self.n_cols/2-c, self.n_rows-1)].neighbors['nw'].append(board1[(playerID1, c+self.n_cols/2+1, self.n_rows-1)])

    def generate(self):
        nodes0, pieces0, player0 = self.generate_halfboard(playerID=0)
        nodes1, pieces1, player1 = self.generate_halfboard(playerID=1)
        self.glue_halfboards(nodes0, 0, nodes1, 1)
        self.glue_halfboards(nodes1, 1, nodes0, 0)
        nodes = joindicts(nodes0, nodes1)
        pieces = list(pieces0)
        pieces.extend(pieces1)
        players = [player0, player1]
        return nodes, pieces, players

if __name__=='__main__':
    generator = TwoChessGenerator()
    game = Game(generator)
    f = open('output.txt', 'w')
    f.write(str(game))
    f.close()
    winner = game.play_game()
    print "The winner is " , winner
