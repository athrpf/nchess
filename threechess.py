

all_directions = ('e','ne','n','nw','w','sw','s','se')
direction_map = {'e':0 , 'ne':1, 'n': 2, 'nw':3, 'w':4, 'sw':5, 's':6, 'se':7}

class PlayerID:
    """
    A playerID fully identifies a player.
    It is useful, if more information about a player is necessary, but not
    the player object itself.
    It can be compared to an int.
    """
    def __init__(self, intID, color=None, name=None, plt_color=None):
        self.id = intID
        self.color = color
        self.name = name
        self.plt_color = plt_color

    def __str__(self):
        if self.name is not None:
            return self.name
        if self.color is not None:
            return self.color
        return "Player " +str(self.id)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id==other
        if isinstance(other, PlayerID):
            return self.id==other.id

    def __gt__(self, other):
        return self.id>other.id

    def __ge__(self, other):
        return self.id>=other.id

    def __hash__(self):
        return self.id

class Node:
    def __init__(self, playerID, nodeID):
        self.nodeID = nodeID
        self.neighbors = {}
        for d in all_directions:
            self.neighbors[d] = []
        self.owner = playerID
        self.piece = None

    def get_next_nodes(self, moving_playerID, direction):
        if isinstance(direction, list):
            retval = []
            for d in direction:
                retval.extend(self.get_next_nodes(moving_playerID, d))
            return retval
        if moving_playerID==self.owner:
            return self.neighbors[direction]
        else:
            return self.neighbors[all_directions[(direction_map[direction]+4)%8]]

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
        self.history  = [position]
        self.alive    = True

class King(Piece):
    def get_possible_moves(self):
        retval = []
        for d in all_directions:
            retval.extend(filter(lambda x: x.piece is None,  self.position.get_next_nodes(self.owner, d)))
        return retval

    def __str__(self):
        return "King(" + str(self.owner)+ ") at " + str(self.position)

class Pawn(Piece):
    def get_possible_moves(self):
        retval = []
        onestep = filter(lambda x: x.piece is None,  self.position.get_next_nodes(self.owner, 'n'))
        retval.extend(onestep)
        retval.extend(filter(lambda x: x.piece is not None and x.piece.owner is not self.owner, self.position.get_next_nodes(self.owner, ['nw','ne'])))
        if len(self.history)==1:
            for s in onestep:
                retval.extend(filter(lambda x: x.piece is None,  s.get_next_nodes(self.owner, 'n')))
        return retval

    def __str__(self):
        return "Pawn(" + str(self.owner)+ ") at " + str(self.position)

class DecideAndContinuePiece(Piece):
    def get_possible_moves(self):
        retval = []
        directiondict = {}
        for d in self.initial_directions:
            firststep = filter(lambda x: x.piece is None or x.piece.owner is not self.owner, self.position.get_next_nodes(self.owner, d))
            directiondict[d] = firststep
            retval.extend(firststep)
            for s in filter(lambda x: x.piece is None, firststep):
                retval.extend(self.continue_step(s, d))
        return retval

    def continue_step(self, current_node, direction):
        nextstep = filter(lambda x: x.piece is None or x.piece.owner is not self.owner, current_node.get_next_nodes(self.owner, direction))
        retval = []
        for n in filter(lambda x: x.piece is None, nextstep):
            retval.extend(self.continue_step(n, direction))
        retval.extend(nextstep)
        return retval

class Bishop(DecideAndContinuePiece):
    def __init__(self, playerID, position):
        Piece.__init__(self, playerID, position)
        self.initial_directions = ['nw','ne','sw','se']

    def __str__(self):
        return "Bishop(" + str(self.owner)+ ") at " + str(self.position)

class Rook(DecideAndContinuePiece):
    def __init__(self, playerID, position):
        Piece.__init__(self, playerID, position)
        self.initial_directions = ['n','s','e','w']

    def __str__(self):
        return "Rook(" + str(self.owner)+ ") at " + str(self.position)

class Queen(DecideAndContinuePiece):
    def __init__(self, playerID, position):
        Piece.__init__(self, playerID, position)
        self.initial_directions = all_directions

    def __str__(self):
        return "Queen(" + str(self.owner)+ ") at " + str(self.position)

class KnightLike(Piece):
    """
    Nightlike pieces have a set of move orders that they can do.
    Like knights, they can ignore other pieces on the nodes they pass.
    This set must defined in the constructor as self.move_orders
    """
    def get_possible_moves(self):
        retval = []
        for mo in self.move_orders:
            retval.extend(self.do_move_order(self.position, mo))
        return retval

    def do_move_order(self, current_node, move_order):
        mo = list(move_order)
        d = mo.pop(0)
        if len(mo)==0:
            return filter(lambda x: x.piece is None or x.piece.owner is not self.owner, current_node.get_next_nodes(self.owner, d))
        retval = []
        for n in current_node.get_next_nodes(self.owner, d):
            retval.extend(self.do_move_order(n, mo))
        return retval

class Knight(KnightLike):
    def __init__(self, playerID, position):
        Piece.__init__(self, playerID, position)
        self.move_orders = [['n','n','w'],
                            ['n','n','e'],
                            ['s','s','w'],
                            ['s','s','e'],
                            ['e','e','n'],
                            ['e','e','s'],
                            ['w','w','n'],
                            ['w','w','s']]

    def __str__(self):
        return "Knight(" + str(self.owner)+ ") at " + str(self.position)

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

    def play(self, max_moves=None):
        move_counter = 0
        while not self.game_over:
            self.play_next_move()
            move_counter+=1
            if max_moves is not None and move_counter>max_moves:
                break
        return self.winner

    def make_move(self, move):
        #p = self.pieces[move.pieceID]
        print move
        p = move.piece
        assert(p.position==move.start)
        assert(p==move.start.piece)
        move.start.piece = None
        p.position = move.end
        p.history.append(move.end)
        if isinstance(move.end.piece, King):
            return True
        if move.end.piece is not None:
            move.end.piece.alive = False
        move.end.piece = p
        return False

    def get_pieces(self, playerID=None):
        if playerID is None:
            return filter(lambda x: x.alive, self.pieces)
        return filter(lambda x: x.owner==playerID and x.alive, self.pieces)

    def __str__(self):
        s = ""
        for n in self.nodes.itervalues():
            s += str(n)
        return s

def joindicts(dictlist):
    retval = {}
    for dicti in dictlist:
        for (k,v) in dicti.iteritems():
            retval[k] = v
    return retval

class NChessGenerator:
    def __init__(self, number_of_players=3, number_of_rows=4, number_of_columns=8, player_type_list=None):
        self.n_rows = number_of_rows
        self.n_cols = number_of_columns
        self.n_players = number_of_players
        if player_type_list is None:
            self.player_type_list = [ ConsolePlayer]*self.n_players
        else:
            self.player_type_list = player_type_list

    def generate_halfboard(self, playerID, PlayerType=ConsolePlayer):
        rows = range(self.n_rows)
        cols = range(self.n_cols)
        nodes = {}
        for r in rows:
            for c in cols:
                nodes[(playerID, c, r)] = Node(playerID, (playerID.id, c, r))
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

        queen = Queen(playerID, nodes[(playerID, 3,0)])
        nodes[(playerID, 3,0)].piece = queen
        pieces.append(queen)

        bishop1 = Bishop(playerID, nodes[(playerID,2,0)])
        nodes[(playerID,2,0)].piece = bishop1
        pieces.append(bishop1)
        bishop2 = Bishop(playerID, nodes[(playerID,5,0)])
        nodes[(playerID,5,0)].piece = bishop2
        pieces.append(bishop2)

        knight1 = Knight(playerID, nodes[(playerID,1,0)])
        nodes[(playerID,1,0)].piece = knight1
        pieces.append(knight1)
        knight2 = Knight(playerID, nodes[(playerID,6,0)])
        nodes[(playerID,6,0)].piece = knight2
        pieces.append(knight2)

        rook1 = Rook(playerID, nodes[(playerID,0,0)])
        nodes[(playerID,0,0)].piece = rook1
        pieces.append(rook1)
        rook2 = Rook(playerID, nodes[(playerID,7,0)])
        nodes[(playerID,7,0)].piece = rook2
        pieces.append(rook2)

        for c in cols:
            pawn = Pawn(playerID, nodes[(playerID,c,1)])
            pieces.append(pawn)
            nodes[(playerID,c,1)].piece = pawn
        player = PlayerType(playerID)
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
                board2[(playerID2, self.n_cols/2-c-1, self.n_rows-1)].neighbors['nw'].append(board1[(playerID1, c+self.n_cols/2+1, self.n_rows-1)])

    def generate_playerIDs(self):
        colorlist = ['black', 'brown', 'beige', 'white']
        plt_colorlist = ['k','b','g','y']
        return [PlayerID(i,color=c,plt_color=pc) for i, c, pc in zip(range(self.n_players), colorlist, plt_colorlist)]

    def generate(self):
        nodeslist = []
        pieces = []
        players = []
        for p,ptype in zip(self.generate_playerIDs(), self.player_type_list):
            n, pi, pl = self.generate_halfboard(playerID=p, PlayerType=ptype)
            nodeslist.append(n)
            pieces.extend(pi)
            players.append(pl)
        for p in range(self.n_players):
            self.glue_halfboards(nodeslist[p-1], players[p-1].playerID, nodeslist[p], players[p].playerID)
        nodes = joindicts(nodeslist)
        return nodes, pieces, players

if __name__=='__main__':
    generator = NChessGenerator()
    game = Game(generator)
    f = open('output.txt', 'w')
    f.write(str(game))
    f.close()
    winner = game.play()
    print "The winner is " , winner
