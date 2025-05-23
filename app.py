from flask import Flask, render_template, jsonify 
from chess_game import ChessGame, WHITE, BLACK, EMPTY, PIECE_CLASSES # Import PIECE_CLASSES
from chess_game import PAWN_T, ROOK_T, KNIGHT_T, BISHOP_T, QUEEN_T, KING_T

app = Flask(__name__)
game = ChessGame() # Single global game instance

# Server-side state for selected piece and promotion
selected_piece_coords = None
promotion_pending_data = None # Stores {'square': (r,c), 'color': 'white/black', 'original_start_pos': (r,c), 'original_end_pos':(r,c)}


# Unicode characters for pieces (ensure this matches your game's representation)
PIECE_UNICODE_MAP = {
    (PAWN_T, WHITE): "♙", (PAWN_T, BLACK): "♟",
    (ROOK_T, WHITE): "♖", (ROOK_T, BLACK): "♜",
    (KNIGHT_T, WHITE): "♘", (KNIGHT_T, BLACK): "♞",
    (BISHOP_T, WHITE): "♗", (BISHOP_T, BLACK): "♝",
    (QUEEN_T, WHITE): "♕", (QUEEN_T, BLACK): "♛",
    (KING_T, WHITE): "♔", (KING_T, BLACK): "♚",
}

def get_piece_symbol_for_web(piece_data):
    if piece_data == EMPTY:
        return ""
    return PIECE_UNICODE_MAP.get(piece_data, "")

def get_board_state_for_json():
    board_list = []
    for r_idx in range(8):
        row_symbols = []
        for c_idx in range(8):
            piece_data = game.board[r_idx][c_idx]
            row_symbols.append(get_piece_symbol_for_web(piece_data))
        board_list.append(row_symbols)
    return board_list

@app.route('/')
def home():
    global selected_piece_coords, promotion_pending_data # Reset state on new game/refresh
    selected_piece_coords = None
    promotion_pending_data = None
    game.__init__() # Reset the game board and state

    board_for_template = get_board_state_for_json()
    current_player_display = game.current_player.capitalize()
    
    return render_template('index.html', 
                           board=board_for_template, 
                           current_player=current_player_display,
                           game_messages="New Game Started. White's turn.")

@app.route('/select_square/<int:row>/<int:col>', methods=['GET'])
def handle_square_click(row, col):
    global selected_piece_coords, promotion_pending_data
    # print(f"API: Click ({row},{col}). Sel: {selected_piece_coords}. Promo: {promotion_pending_data}. Player: {game.current_player}")

    clicked_coords = (row, col)
    response_data = {}
    message_log = [] # For accumulating messages

    if promotion_pending_data:
        # Client should ideally not allow board clicks if promotion dialog is expected.
        # This is a fallback.
        message_log.append('Promotion choice pending. Please select a piece to promote to.')
        response_data = {
            'status': 'error', # Or 'promotion_still_pending'
            'message': " ".join(message_log),
            'board_state': get_board_state_for_json(),
            'current_player': game.current_player.capitalize(), # Player who made the pawn move
            'promotion_square': promotion_pending_data['square'],
            'is_check': game.is_in_check(game.current_player), # Check status of player who needs to promote
            'is_checkmate': False # Cannot be checkmate if promotion is pending for current player
        }
        return jsonify(response_data)

    if selected_piece_coords is None:
        # No piece currently selected: try to select the piece at (row, col)
        piece_at_click = game.board[row][col]
        if piece_at_click != EMPTY and piece_at_click[1] == game.current_player:
            selected_piece_coords = clicked_coords
            valid_moves = game.get_validated_moves_for_piece(selected_piece_coords)
            piece_class_name = PIECE_CLASSES[piece_at_click[0]](piece_at_click[1]).__class__.__name__
            message_log.append(f"{piece_at_click[1].capitalize()} {piece_class_name} selected at {game.coords_to_algebraic(selected_piece_coords)}.")
            response_data = {
                'status': 'piece_selected',
                'selected_square': selected_piece_coords,
                'valid_moves': valid_moves,
                'message': " ".join(message_log)
            }
        else:
            message_log.append('Invalid selection: Not your piece or empty square.')
            response_data = {
                'status': 'invalid_selection',
                'message': " ".join(message_log)
            }
    else:
        # A piece is already selected: try to move it
        start_pos = selected_piece_coords
        end_pos = clicked_coords

        if start_pos == end_pos: # Clicked the same selected piece again - deselect
            selected_piece_coords = None
            message_log.append('Piece deselected.')
            response_data = {'status': 'deselected', 'message': " ".join(message_log)}
        else:
            valid_moves_for_selected = game.get_validated_moves_for_piece(start_pos)
            if end_pos in valid_moves_for_selected:
                move_result = game.move_piece(start_pos, end_pos) # This might return ("PROMOTION", ...) or True/False

                if isinstance(move_result, tuple) and move_result[0] == "PROMOTION":
                    _, promotion_square, piece_color = move_result
                    # Store data needed for when /promote_pawn is called
                    promotion_pending_data = {
                        'square': promotion_square, 
                        'color': piece_color,
                        'original_start_pos': start_pos, # Store original move for EP setting
                        'original_end_pos': end_pos
                    }
                    selected_piece_coords = None 
                    message_log.append(f"Pawn promotion at {game.coords_to_algebraic(promotion_square)}! Choose piece.")
                    response_data = {
                        'status': 'promotion_required',
                        'promotion_square': promotion_square,
                        'piece_color': piece_color,
                        'message': " ".join(message_log)
                    }
                elif move_result is True: # Successful standard move
                    message_log.append(f"Move from {game.coords_to_algebraic(start_pos)} to {game.coords_to_algebraic(end_pos)} successful.")
                    selected_piece_coords = None
                    # Check/Checkmate status for the *new* current player
                    is_check = game.is_in_check(game.current_player)
                    is_checkmate = False
                    if is_check:
                        message_log.append(f"!!! {game.current_player.capitalize()} is in check !!!")
                        is_checkmate = game.is_checkmate(game.current_player)
                        if is_checkmate:
                            winner = WHITE if game.current_player == BLACK else BLACK
                            message_log.append(f"Checkmate! {winner.capitalize()} wins!")
                    
                    response_data = {
                        'status': 'move_successful',
                        'is_check': is_check,
                        'is_checkmate': is_checkmate,
                        'message': " ".join(message_log)
                    }
                else: # move_piece returned False (should be rare if get_validated_moves is accurate)
                    message_log.append(f"Move from {game.coords_to_algebraic(start_pos)} to {game.coords_to_algebraic(end_pos)} failed internally.")
                    selected_piece_coords = None 
                    response_data = {'status': 'invalid_move', 'message': " ".join(message_log)}
            else: # Clicked on a square that is not a valid move
                message_log.append("Invalid target square. Piece deselected.")
                selected_piece_coords = None 
                # Optionally, try to select the newly clicked square as a new piece
                new_piece_at_click = game.board[row][col]
                if new_piece_at_click != EMPTY and new_piece_at_click[1] == game.current_player:
                    # This is like starting a new selection
                    selected_piece_coords = clicked_coords
                    valid_moves = game.get_validated_moves_for_piece(selected_piece_coords)
                    piece_class_name = PIECE_CLASSES[new_piece_at_click[0]](new_piece_at_click[1]).__class__.__name__
                    message_log.append(f"New selection: {new_piece_at_click[1].capitalize()} {piece_class_name} at {game.coords_to_algebraic(selected_piece_coords)}.")
                    response_data = {
                        'status': 'piece_selected', # Changed status
                        'selected_square': selected_piece_coords,
                        'valid_moves': valid_moves,
                        'message': " ".join(message_log)
                    }
                else: # Clicked on empty or opponent piece after having a piece selected
                     response_data = {'status': 'deselected', 'message': " ".join(message_log)}


    # Common data for all responses from this route
    response_data['board_state'] = get_board_state_for_json()
    response_data['current_player'] = game.current_player.capitalize()
    if 'is_check' not in response_data: # Ensure these fields are present
        response_data['is_check'] = game.is_in_check(game.current_player) if not promotion_pending_data else game.is_in_check(promotion_pending_data['color'])
    if 'is_checkmate' not in response_data:
        response_data['is_checkmate'] = False # Avoid re-calculating unless relevant to current state

    return jsonify(response_data)

@app.route('/promote_pawn/<string:choice>', methods=['POST'])
def promote_pawn(choice):
    global promotion_pending_data, selected_piece_coords
    
    if not promotion_pending_data:
        return jsonify({'status': 'error', 'message': 'No pawn promotion is pending.'}), 400

    square = promotion_pending_data['square']
    color = promotion_pending_data['color']
    original_start_pos = promotion_pending_data['original_start_pos']
    original_end_pos = promotion_pending_data['original_end_pos']

    # Determine if the original pawn move was a two-square advance
    # This is needed for correct EP target setting after promotion.
    # The pawn is already at the promotion square on game.board.
    # original_start_pos[0] is the pawn's starting row for that move.
    # original_end_pos[0] is the pawn's ending row (promotion square row).
    moved_piece_type = PAWN_T # We know it was a pawn
    moved_piece_color = color
    start_row_pawn_move = original_start_pos[0]
    end_row_pawn_move = original_end_pos[0]
    start_col_pawn_move = original_start_pos[1]


    game.complete_pawn_promotion(square, color, choice) # This also calls next_turn()

    # Set En Passant target based on the original pawn move that led to promotion
    if moved_piece_type == PAWN_T and abs(start_row_pawn_move - end_row_pawn_move) == 2:
        if moved_piece_color == WHITE:
            game.en_passant_target_square = (start_row_pawn_move - 1, start_col_pawn_move)
        else: # BLACK pawn
            game.en_passant_target_square = (start_row_pawn_move + 1, start_col_pawn_move)
        # print(f"Debug (promote_pawn): EP target set to {game.en_passant_target_square}")
    else:
        game.en_passant_target_square = None # Should be None if not 2-square move
        # print(f"Debug (promote_pawn): EP target reset to None")


    promotion_pending_data = None # Clear promotion state
    selected_piece_coords = None  # Clear any lingering selection

    is_check = game.is_in_check(game.current_player) # Check new current player
    is_checkmate = False
    message = f"Pawn promoted. {game.current_player.capitalize()}'s turn."
    if is_check:
        is_checkmate = game.is_checkmate(game.current_player)
        message = f"{game.current_player.capitalize()} is in check!"
        if is_checkmate:
            winner = WHITE if game.current_player == BLACK else BLACK
            message = f"Checkmate! {winner.capitalize()} wins!"
            
    return jsonify({
        'status': 'promotion_complete',
        'board_state': get_board_state_for_json(),
        'current_player': game.current_player.capitalize(),
        'is_check': is_check,
        'is_checkmate': is_checkmate,
        'message': message
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
