import chess

board = chess.Board()
piece_score = {'p':1, 'b':3, 'n':3, 'r': 5, 'q': 9, 'P':-1, 'B':-3, 'N':-3, 'R': -5, 'Q': -9, 'None':0}
#piece_score = {'p':-1, 'b':-3, 'n':-3, 'r': -5, 'q': -9, 'P':1, 'B':3, 'N':3, 'R': 5, 'Q': 9, 'None':0}
#print(list(board.legal_moves))
#board.push_san('h4')
#board.push_san('g5')

#move = list(board.legal_moves)
#comp = ["h5","hxg5","a3","a4","b3","b4","c3","c4","d3","d4","e3","e4","f3","f4","g3","g4","Na3","Nc3","Nf3","Nh3","Rh2","Rh3"]


'''
# Na3 --> b1a3
def san_to_uci(board, notation_list):
    moves = []
    for move in notation_list:
        moves.append(board.parse_san(move))
    return moves
'''

#print(board.parse_san(comp[1]))

'''
#white
moves = list(board.legal_moves)
#print(moves[1])
board.push_san(str(moves[18]))

#black
moves = list(board.legal_moves)
#print(moves[1])
board.push_san(str(moves[17]))

#white 2

#
legal_moves = list(board.legal_moves)
move_options = []
for move in legal_moves:
    move = str(move)
    #from_square = move[:2]
    to_square = eval('chess.'+move[2:].upper())
    piece_at_square = board.piece_at(to_square)
    if piece_at_square != None:
        move_options.append([piece_score[str(piece_at_square)], move])
else:
    best_move = max(move_options)
    board.push_san(best_move[1])
#
#print(moves)
#board.push_san('b4c5')

## test function1 ##
def compute_cost1(board, n=3, cost=0):
    legal_moves = list(board.legal_moves)
    
    for move in legal_moves:
        temp_board = board.copy()
        move = str(move)
        to_square = eval('chess.'+move[2:].upper())
        piece_at_square = board.piece_at(to_square)
        cost += piece_score[piece_at_square] # None values take 0 cost
        temp_board.push_san(to_square)
        if n-1 != 0:
            total_cost = compute_cost(temp_board, n-1, cost)
        else:
            return cost
## ##
        '''   
def compute_cost(board, n=3, const_n=3, alpha=float('-inf'), beta=float('inf')):

    # both 'n' and 'const_n' are same values but 'const_n' is not decremented
    
    legal_moves = list(board.legal_moves)
    move_options = []
    
    if n == 1:
        # if we get checkmate available, game over
        if len(legal_moves) == 0:
            move_options.append([0, ""])
        
        for move in legal_moves:
            move = str(move)
            to_square = eval('chess.' + move[2:4].upper())
            piece_at_square = board.piece_at(to_square)
            new_score = piece_score[str(piece_at_square)]
            move_options.append([new_score, move])
            if const_n % 2 == 1 and alpha > new_score:
                break
            elif const_n % 2 == 0 and beta < new_score:
                break

        if const_n % 2 == 1:    
            return max(move_options)
        else:
            return min(move_options)
    
    elif n != const_n:
        first_iteration = True

        # if we get checkmate available, game over
        if len(legal_moves) == 0:
            move_options.append([0, ""])
            
        for move in legal_moves:
            temp_board = board.copy()
            move = str(move)
            to_square = eval('chess.' + move[2:4].upper())
            piece_at_square = board.piece_at(to_square)
            score = piece_score[str(piece_at_square)]
            temp_board.push_san(move)

            # high penalty if enemy gets possiblity of checkmate
            if n % 2 == 0 and temp_board.is_checkmate():
                return [float('-inf'), move +" "+ returned_move]
            
            if first_iteration:
                returned_score, returned_move = compute_cost(temp_board, n-1, const_n)
                first_iteration = False

                # alpha beta prunning to reduce computation cost
                if n % 2 == 1 and alpha > returned_score:
                    # appending bad value and breaking out #
                    move_options.append([score + returned_score, move +" "+ returned_move])
                    break
                elif n % 2 == 0 and beta < returned_score:
                    move_options.append([score + returned_score, move +" "+ returned_move])
                    break
            else:
                returned_score, returned_move = compute_cost(temp_board, n-1, const_n, alpha, beta)

            # white's favour #
            if n % 2 == 1 and alpha < returned_score: 
                alpha = returned_score
            elif n % 2 == 0 and beta > returned_score:
                beta = returned_score
                
            move_options.append([score + returned_score, move +" "+ returned_move])

        if n % 2 == 1:
            return max(move_options)
        else:    
            return min(move_options)
        
    else:
        for move in legal_moves:
            temp_board = board.copy()
            move = str(move)
            to_square = eval('chess.' + move[2:4].upper())
            piece_at_square = board.piece_at(to_square)
            score = piece_score[str(piece_at_square)]
            temp_board.push_san(move)
            returned_score, returned_move = compute_cost(temp_board, n-1, const_n)

            # if checkmate is available, score = infinity
            if temp_board.is_checkmate():
                return [float('inf'), move]

            # force promotion to Queen
            if len(move) == 5:
                move = move[:4]+'Q'
            
            move_options.append([score + returned_score, move]) # getting the move to execute only; else #move_options.append([score + returned_score, move +" "+ returned_move])

        if n % 2 == 1:
            return max(move_options)
        else:    
            return min(move_options)

board.push_san("d2d4")
while True:
    legal_moves = list(board.legal_moves)
    if len(legal_moves) != 0:
        c_move = compute_cost(board, 3, 3)[1]
        board.push_san(c_move)
    print(board)
    w = input('Move: ')
    board.push_san(w)
    
