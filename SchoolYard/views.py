from django.http import JsonResponse
from django.shortcuts import redirect, render
from SchoolYard.models import History

from datetime import datetime
import chess

def home(request):
    if request.method == "POST":
        returned_record_id = eval(request.POST.get("del_record_id", "None"))
        history_record = History.objects.get(id = returned_record_id)
        history_record.delete()

    history_records = History.objects.all().values_list('id', 'csrf_token', 'date', 'game_fen', 'status', 'condition').order_by('id')
    processed_records = []
    for record_id in range(len(history_records)):
        record = list(history_records[record_id])
        returned_csrf_token = record[1]
        status = record[5]
        if status == "In Progress":
            record[4] = "Turn: " + record[4]
            button_name = "Continue Game"
            button_href = "game/" + returned_csrf_token
        else:
            record[4] = "Winner: " + record[4]
            button_name = "View Game"
            button_href = "history/" + returned_csrf_token
        
        record.extend([button_name, button_href])
        processed_records.append(record)

    processed_records.reverse() 
    split_records = []
    # splitting records into left / right
    total_records = len(processed_records)

    if total_records % 2 == 0: 
        for record_num in range(0, total_records, 2):
            split_records.append(processed_records[record_num] + processed_records[record_num+1])
    else: 
        for record_num in range(0, total_records - 1, 2):
            split_records.append(processed_records[record_num] + processed_records[record_num+1])
        else:
            split_records.append(processed_records[-1]+["completed"])

    return render(request, 'home.html', {'records': split_records, 'complete': "completed"})


def game(request):

    # game settings
    first_move = "h4"
    play_time = 10 # minutes
    turn = "Black"
    winner = str()
    game_condition = "In Progress"
    moves_list = []
    returned_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # Starting Game FEN

    board = chess.Board()
    board.push_san(first_move)


    if request.POST.get("action") == "post":
        returned_fen = eval(request.POST.get("fen","None"))    
        board.set_fen(returned_fen)

        returned_csrf_token = request.POST.get("csrfmiddlewaretoken")
        from_square = eval(request.POST.get("from","None"))
        to_square = eval(request.POST.get("to","None"))
        computer_time = eval(request.POST.get("computer_time","None"))
        player_time = eval(request.POST.get("player_time","None"))
        timeover = request.POST.get("timeover")

        computed_move, parsed_computed_move, game_fen, game_over, game_condition, winner = check_game_over(timeover, returned_fen, board)

        current_timestamp = datetime.now().timestamp()
        current_date = datetime.now().strftime('%d %b %Y')
        current_time = datetime.now().strftime('%H:%M:%S')

        if History.objects.filter(csrf_token = returned_csrf_token).exists():
            game_record = History.objects.get(csrf_token = returned_csrf_token)
            game_timestamp = datetime.fromtimestamp(float(game_record.timestamp))

            # checking if record is old
            if (datetime.fromtimestamp(current_timestamp) - game_timestamp).days > 10:
                moves_list.append(from_square + to_square)  # adding player move
                moves_list.append(computed_move)            # adding computer's move
                game_record.csrf_token = game_record.csrf_token + game_timestamp
                game_record.save()
                # add new record
                new_game_record = History()
                new_game_record.csrf_token = returned_csrf_token
                new_game_record.timestamp =  current_timestamp
                new_game_record.date = current_date
                new_game_record.time = current_time
                new_game_record.game_fen = game_fen
                new_game_record.moves = " ".join(move for move in moves_list)
                new_game_record.status = turn
                new_game_record.computer_time_left = str(play_time) + ':00'
                new_game_record.player_time_left = str(play_time) + ':00'
                new_game_record.save()
            else:
                moves_list = game_record.moves.split()
                if (from_square and to_square and computed_move) is not None: 
                    moves_list.append(from_square + to_square)  # adding player move
                    moves_list.append(computed_move)            # adding computer's move
                game_record.game_fen = game_fen
                game_record.moves = " ".join(move for move in moves_list)
                game_record.status = turn
                game_record.winner = winner
                game_record.condition = game_condition
                game_record.computer_time_left = computer_time
                game_record.player_time_left = player_time 
                game_record.save()

        # start a new game
        else:
            moves_list.append("h2"+first_move)
            moves_list.append(from_square + to_square)  # adding player move
            moves_list.append(computed_move)            # adding computer's move
            new_game_record = History()
            new_game_record.csrf_token = returned_csrf_token
            new_game_record.timestamp =  current_timestamp
            new_game_record.date = current_date
            new_game_record.time = current_time
            new_game_record.game_fen = game_fen
            new_game_record.moves = " ".join(move for move in moves_list)
            new_game_record.status = turn
            new_game_record.computer_time_left = str(play_time) + ':00'
            new_game_record.player_time_left = str(play_time) + ':00'
            new_game_record.save()

        last_move = moves_list[-1]

        return JsonResponse({'computed_move': parsed_computed_move, 'gameoverfen': game_fen, 'last_move': last_move, 'game_over': game_over, 'winner_message': winner, 'condition': game_condition, 'moves_list': moves_list}) 


    # view moves: last move / next move
    elif request.POST.get("action") == "view":
        game_over = "False"
        end_move = "False"
        board = chess.Board() 
        returned_csrf_token = request.POST.get("csrfmiddlewaretoken")
        returned_moves_count = int(eval(request.POST.get("view_moves_count", "0")))
        view_move = request.POST.get("view_move","None")

        try:
            new_gamefen, returned_moves_count, last_move, end_move, game_over = view_moves(returned_csrf_token, returned_moves_count, first_move, view_move)
        except ValueError:
            board.push_san(first_move) # first move
            new_gamefen = board.fen() # game fen with first computer move
            last_move = "h2" + first_move

        return JsonResponse({'gamefen': new_gamefen, 'returned_moves_count': returned_moves_count, 'last_move': last_move, 'end_move': end_move, 'game_over': game_over})
    
    return render(request, 'board.html', {'first_move':first_move, 'play_time': play_time, 'moves_list': moves_list})


def games_view(request, returned_csrf_token):

    if History.objects.filter(csrf_token = returned_csrf_token).exists():
        history_record = History.objects.get(csrf_token = returned_csrf_token)
        if history_record.condition == "In Progress":
            return redirect(home)     
    else:
        return redirect(home) # if non existing csrf_token

    returned_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # Starting Game FEN

    moves_list = history_record.moves.split()
    winner = history_record.status
    condition = history_record.condition
    computer_time_left = history_record.computer_time_left
    player_time_left = history_record.player_time_left 

    first_move = last_move = moves_list[0]
    processed_moves_list = " ".join(move for move in moves_list)

    if request.POST.get("action") == "view":
        board = chess.Board() 
        returned_moves_count = int(eval(request.POST.get("view_moves_count", "0")))
        view_move = request.POST.get("view_move")

        if view_move == "view_from_num":   # when player selects specific move
            for i in range(returned_moves_count):
                move = moves_list[i]
                board.push(chess.Move.from_uci(move))

        elif view_move != "start":         # view last / next move 
            if view_move == "forward" and returned_moves_count < len(moves_list):   # checking if next move exists
                returned_moves_count += 1
            elif view_move == "back" and returned_moves_count > 1:                
                returned_moves_count -= 1
            for move_num in range(returned_moves_count):
                board.push(chess.Move.from_uci(moves_list[move_num]))

        else:                              # back to the start
            returned_moves_count = 0

        new_gamefen = board.fen()
        try: last_move = str(board.pop())
        except: last_move = first_move

        return JsonResponse({'gamefen': new_gamefen, 'returned_moves_count': returned_moves_count, 'last_move': last_move, 'winner': winner, 'condition': condition})

    elif request.POST.get("action") == "delete_record":
        history_record.delete()
        return redirect(home)

    return render(request, 'history.html', {'returned_csrf_token': returned_csrf_token, 'first_move': first_move, 'game_fen': returned_fen, 'moves_list': processed_moves_list, 'player_time_left': player_time_left, 'computer_time_left': computer_time_left, 'winner': winner, 'condition': condition})


def continue_game(request, returned_csrf_token):
    first_move = "h4"

    if History.objects.filter(csrf_token = returned_csrf_token).exists():
        game_record = History.objects.get(csrf_token = returned_csrf_token)
        moves_list = game_record.moves.split()
        returned_fen = game_record.game_fen
        game_condition = game_record.condition
        if game_condition != "In Progress":
            return redirect(home)
        computer_time_left = (datetime.strptime(game_record.computer_time_left, "%M:%S") - datetime(1900, 1, 1)).total_seconds()
        player_time_left = (datetime.strptime(game_record.player_time_left, "%M:%S") - datetime(1900, 1, 1)).total_seconds()
    else:
        return redirect(home) # if non existing csrf_token

    winner = str()
    board = chess.Board(returned_fen)

    if request.POST.get("action") == "post":
        returned_fen = eval(request.POST.get("fen","None"))    
        board.set_fen(returned_fen)

        from_square = eval(request.POST.get("from","None"))
        to_square = eval(request.POST.get("to","None"))
        computer_time = eval(request.POST.get("computer_time","None"))
        player_time = eval(request.POST.get("player_time","None"))
        timeover = request.POST.get("timeover")

        computed_move, parsed_computed_move, game_fen, game_over, game_condition, winner = check_game_over(timeover, returned_fen, board)


        if History.objects.filter(csrf_token = returned_csrf_token).exists():
            game_record = History.objects.get(csrf_token = returned_csrf_token)
            moves_list = game_record.moves.split()
            if (from_square and to_square and computed_move) is not None: 
                moves_list.append(from_square + to_square)  # adding player move
                moves_list.append(computed_move)            # adding computer's move
            game_record.game_fen = game_fen
            game_record.moves = " ".join(move for move in moves_list)
            game_record.winner = winner
            game_record.condition = game_condition
            game_record.computer_time_left = computer_time 
            game_record.player_time_left = player_time 
            game_record.save()

        last_move = moves_list[-1]

        return JsonResponse({'computed_move': parsed_computed_move, 'gameoverfen': game_fen, 'last_move': last_move, 'game_over': game_over, 'winner_message': winner, 'condition': game_condition, 'moves_list': moves_list}) 

    # view moves: last move / next move
    elif request.POST.get("action") == "view":
        game_over = "False"
        end_move = "False"
        board = chess.Board() 
        returned_moves_count = int(eval(request.POST.get("view_moves_count", "0")))
        view_move = request.POST.get("view_move","None")
        try:
            new_gamefen, returned_moves_count, last_move, end_move, game_over = view_moves(returned_csrf_token, returned_moves_count, first_move, view_move)
        except ValueError:
            board.push_san(first_move) 
            new_gamefen = board.fen() # game fen with first computer move
            last_move = "h2" + first_move

        return JsonResponse({'gamefen': new_gamefen, 'returned_moves_count': returned_moves_count, 'last_move': last_move, 'end_move': end_move, 'game_over': game_over})

    processed_moves_list = " ".join(move for move in moves_list)
    last_move = moves_list[-1]

    return render(request, 'savedgame.html', {'returned_csrf_token': returned_csrf_token, 'computer_time_left': computer_time_left, 'player_time_left': player_time_left, 'game_fen': returned_fen, 'moves_list': processed_moves_list, 'first_move': first_move, 'last_move': last_move})


def check_game_over(timeover, returned_fen, board):
    # function used by continue_game() and game()
    game_condition = "In Progress"
    game_over = str()
    computed_move = ""
    parsed_computed_move = ""
    game_fen = returned_fen
    winner = ""

    if timeover != "false":
        game_over = "True"
        game_fen = returned_fen
        if timeover == "White":
            game_condition = "White" + " ran out of Time"
            winner = "You win!" # black wins on time
        else:
            game_condition = "Black" + " ran out of Time"
            winner = "Computer Wins!" # white wins on time

    if game_over != "True":
        game_over = "True"
        game_fen = returned_fen
        if board.is_checkmate():
            winner = "You Win!"
            turn = "Black"
            game_condition = turn + " won by Checkmate" # human wins: black wins
        elif board.is_stalemate():
            winner = "Draw"
            game_condition = "Draw by Stalemate"
        elif board.is_insufficient_material():
            winner = "Draw"
            game_condition = "Draw due to Insufficient Material"
        elif board.is_game_over():
            game_condition = board.outcome()
        else:
            game_over = str()
            computed_move = compute_cost(board, 3, 3)[1]
            parsed_computed_move = board.san(chess.Move.from_uci(computed_move)) # b1a3 --> Na3 

            # force promotion to Queen
            if len(computed_move) == 5:
                computed_move = computed_move.replace('r', 'q').replace('n', 'q').replace('b', 'q')
                parsed_computed_move = parsed_computed_move.replace('R','Q').replace('N','Q').replace('B','Q')
            board.push_san(computed_move)
            game_fen = board.fen()
            game_over = "True"
            if board.is_checkmate():
                winner = "Computer Wins!" # we win: white wins
                turn = "White"
                game_condition = turn + " won by Checkmate"
            elif board.is_stalemate():
                winner = "Draw"
                game_condition = "Draw by Stalemate"
            elif board.is_insufficient_material():
                winner = "Draw"
                game_condition = "Draw due to Insufficient Material"
            else:
                game_over = str()

    return computed_move, parsed_computed_move, game_fen, game_over, game_condition, winner


def view_moves(returned_csrf_token, returned_moves_count, first_move, view_move):
    game_over = "False"
    end_move = "False"
    board = chess.Board() 

    if History.objects.filter(csrf_token = returned_csrf_token).exists():   
        game_record = History.objects.get(csrf_token = returned_csrf_token)
        moves_list = game_record.moves.split()
        game_status = game_record.condition
    else:
        board.push_san(first_move) # first move
        returned_fen = board.fen() # game fen with first computer move
        return JsonResponse({'gamefen': returned_fen, 'returned_moves_count': 0})

    if view_move == "view_from_num": # when player selects specific move
        for i in range(returned_moves_count):
            move = moves_list[i]
            board.push(chess.Move.from_uci(move))
        returned_moves_count = len(moves_list) - returned_moves_count # getting how many moves back player went
        if game_status != "In Progress":
            game_over = "True"
        if returned_moves_count == 0:
            end_move = "True"
    # view last / next move 
    elif view_move != "continue": 
        if view_move == "back" and returned_moves_count < len(moves_list):  # last move && checking if last move exists
            returned_moves_count += 1
        elif view_move == "forward" and returned_moves_count > 1:              # next move
            returned_moves_count -= 1
        check_moves_num = len(moves_list) - returned_moves_count    # number of moves to be pushed into stack
        for move_num in range(check_moves_num):
            board.push(chess.Move.from_uci(moves_list[move_num]))
    # back to game
    else: 
        for move in moves_list:
            board.push(chess.Move.from_uci(move))
        returned_moves_count = 0
        if game_status != "In Progress":
            game_over = "True"

    new_gamefen = board.fen()
    try:
        last_move = str(board.pop())
    except:
        last_move = "h2"+first_move

    return new_gamefen, returned_moves_count, last_move, end_move, game_over


# pieces score division
piece_score = {'p':1, 'b':3, 'n':3, 'r': 5, 'q': 9, 'P':-1, 'B':-3, 'N':-3, 'R': -5, 'Q': -9, 'None':0}
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
            
            move_options.append([score + returned_score, move]) # getting the move to execute only; else #move_options.append([score + returned_score, move +" "+ returned_move])

        if n % 2 == 1:
            return max(move_options)
        else:    
            return min(move_options)
