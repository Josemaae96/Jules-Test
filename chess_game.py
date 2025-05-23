# chess_game.py

from pieces import Pawn, Rook, Knight, Bishop, Queen, King, Piece as PieceABC # PieceABC to avoid name clash

# Define piece type constants (used as keys in board)
PAWN_T = 1 # Using _T suffix to denote type, avoiding clash with class names
ROOK_T = 2
KNIGHT_T = 3
BISHOP_T = 4
QUEEN_T = 5
KING_T = 6
EMPTY = 0

# Define color constants
WHITE = "white"
BLACK = "black"

# Map piece types to their classes
PIECE_CLASSES = {
    PAWN_T: Pawn,
    ROOK_T: Rook,
    KNIGHT_T: Knight,
    BISHOP_T: Bishop,
    QUEEN_T: Queen,
    KING_T: King,
}

class ChessGame:
    def __init__(self):
        self.board = self._initialize_board()
        self.current_player = WHITE
        self.turn_count = 0 # For a simple game end condition
        # self.piece_has_moved stores the has_moved status for pieces based on their initial positions.
        # Key: (initial_row, initial_col), Value: Boolean.
        # This is primarily for Kings and Rooks for castling.
        self.piece_has_moved = {
            # White pieces
            (7, 4): False,  # White King e1
            (7, 0): False,  # White Rook a1
            (7, 7): False,  # White Rook h1
            # Black pieces
            (0, 4): False,  # Black King e8
            (0, 0): False,  # Black Rook a8
            (0, 7): False,  # Black Rook h8
        }
        self.en_passant_target_square = None # For En Passant

    @staticmethod
    def algebraic_to_coords(algebraic_notation):
        """
        Converts algebraic notation (e.g., 'e2', 'h8') to board coordinates (row, col).
        Board representation:
        - Row 0 is Rank 8 (Black's back rank)
        - Row 7 is Rank 1 (White's back rank)
        - Col 0 is File 'a'
        - Col 7 is File 'h'
        
        So: 'a1' -> (7,0), 'h8' -> (0,7), 'e2' -> (6,4)
        Returns (row, col) tuple or None if input is invalid.
        """
        if not isinstance(algebraic_notation, str) or len(algebraic_notation) != 2:
            return None
        
        file_char = algebraic_notation[0].lower()
        rank_char = algebraic_notation[1]

        if not ('a' <= file_char <= 'h' and '1' <= rank_char <= '8'):
            return None
            
        col = ord(file_char) - ord('a')
        row = 8 - int(rank_char) # '1' is row 7, '8' is row 0
        
        return (row, col)

    def _initialize_board(self):
        """Initializes the board to the standard starting chess position.
        Board stores tuples of (PIECE_TYPE, COLOR) or EMPTY.
        """
        board = [[EMPTY for _ in range(8)] for _ in range(8)]

        # Place pawns
        for i in range(8):
            board[1][i] = (PAWN_T, BLACK)
            board[6][i] = (PAWN_T, WHITE)

        # Place rooks
        board[0][0] = (ROOK_T, BLACK); board[0][7] = (ROOK_T, BLACK)
        board[7][0] = (ROOK_T, WHITE); board[7][7] = (ROOK_T, WHITE)

        # Place knights
        board[0][1] = (KNIGHT_T, BLACK); board[0][6] = (KNIGHT_T, BLACK)
        board[7][1] = (KNIGHT_T, WHITE); board[7][6] = (KNIGHT_T, WHITE)

        # Place bishops
        board[0][2] = (BISHOP_T, BLACK); board[0][5] = (BISHOP_T, BLACK)
        board[7][2] = (BISHOP_T, WHITE); board[7][5] = (BISHOP_T, WHITE)

        # Place queens
        board[0][3] = (QUEEN_T, BLACK); board[7][3] = (QUEEN_T, WHITE)

        # Place kings
        board[0][4] = (KING_T, BLACK); board[7][4] = (KING_T, WHITE)

        return board

    def display_board(self):
        """Prints a more user-friendly text representation of the board."""
        print("\n  a b c d e f g h")
        print("  ---------------")
        for r_idx, row in enumerate(self.board):
            print(f"{8 - r_idx}|", end=" ")
            for cell in row:
                if cell == EMPTY:
                    print(".", end=" ")
                else:
                    piece_type, color = cell
                    symbol = "?"
                    if piece_type == PAWN_T: symbol = "P"
                    elif piece_type == ROOK_T: symbol = "R"
                    elif piece_type == KNIGHT_T: symbol = "N"
                    elif piece_type == BISHOP_T: symbol = "B"
                    elif piece_type == QUEEN_T: symbol = "Q"
                    elif piece_type == KING_T: symbol = "K"
                    
                    print(symbol.lower() if color == BLACK else symbol.upper(), end=" ")
            print(f"|{8 - r_idx}")
        print("  ---------------")
        print("  a b c d e f g h\n")

    def get_piece_at(self, position):
        """Returns the piece object at a given position, or None if empty or invalid."""
        r, c = position
        if not (0 <= r <= 7 and 0 <= c <= 7):
            return None
        
        cell_content = self.board[r][c]
        if cell_content == EMPTY:
            return None
        
        piece_type, color = cell_content
        if piece_type in PIECE_CLASSES:
            return PIECE_CLASSES[piece_type](color) # Instantiate the piece object
        return None

    def move_piece(self, start_pos, end_pos):
        """Moves a piece from start_pos to end_pos if the move is valid."""
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        piece_obj = self.get_piece_at(start_pos)

        if piece_obj is None:
            print(f"No piece at {start_pos}")
            return False
        
        if piece_obj.color != self.current_player:
            print(f"Cannot move opponent's piece at {start_pos}. It's {self.current_player}'s turn.")
            return False

        # The board for get_valid_moves should represent occupied squares for blocking,
        # but the piece logic itself doesn't check for friendly pieces at destination.
        # For now, pieces.py's get_valid_moves expects a board of EMPTY or non-EMPTY markers.
        # We can pass self.board directly if piece implementations handle (TYPE, COLOR) tuples for blocking.
        # Let's refine the board representation for get_valid_moves if necessary.
        # For now, assuming pieces.py's get_valid_moves can interpret self.board correctly
        # or we adapt the board representation for it.
        # The current pieces.py uses EMPTY for empty squares and non-EMPTY for occupied.
        # Our self.board has (TYPE, COLOR) tuples. We need to adapt.
        
        # Create a simplified board for validation: 1 for occupied, 0 for empty.
        # This is what get_valid_moves in pieces.py expects for blocking.
        simple_board_for_validation = [[(EMPTY if self.board[r][c] == EMPTY else 1) for c in range(8)] for r in range(8)]

        # Get valid moves, potentially including castling options for King
        valid_moves = []
        if isinstance(piece_obj, King):
            king_color = piece_obj.color
            king_original_row = 7 if king_color == WHITE else 0
            
            # Check king's has_moved status from self.piece_has_moved
            # piece_obj.has_moved is True if instantiated from a piece that has moved,
            # but self.piece_has_moved is the authority for initial K/R positions.
            king_has_moved_check = self.piece_has_moved.get((king_original_row, 4), True) # Default to True if somehow not in dict

            can_castle_kingside = False
            if not king_has_moved_check:
                rook_kingside_pos = (king_original_row, 7)
                rook_kingside_moved = self.piece_has_moved.get(rook_kingside_pos, True)
                # Check path on actual board for emptiness
                if not rook_kingside_moved and \
                   self.board[king_original_row][5] == EMPTY and \
                   self.board[king_original_row][6] == EMPTY:
                    can_castle_kingside = True
            
            can_castle_queenside = False
            if not king_has_moved_check:
                rook_queenside_pos = (king_original_row, 0)
                rook_queenside_moved = self.piece_has_moved.get(rook_queenside_pos, True)
                # Check path on actual board for emptiness
                if not rook_queenside_moved and \
                   self.board[king_original_row][1] == EMPTY and \
                   self.board[king_original_row][2] == EMPTY and \
                   self.board[king_original_row][3] == EMPTY:
                    can_castle_queenside = True
            
            # Set the King object's has_moved state before calling get_valid_moves
            # This ensures King.get_valid_moves uses the correct state for its internal has_moved check.
            piece_obj.has_moved = king_has_moved_check 
            valid_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos,
                                                  can_castle_kingside=can_castle_kingside,
                                                  can_castle_queenside=can_castle_queenside)
        elif isinstance(piece_obj, Pawn):
             valid_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos, 
                                                   attacks_only=False, 
                                                   en_passant_target_square_coord=self.en_passant_target_square)
        else:
            valid_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos)


        # Basic validation: is end_pos a valid destination for the piece type?
        if end_pos not in valid_moves:
            print(f"Invalid move for {piece_obj} from {start_pos} to {end_pos}. Possible moves: {valid_moves}")
            return False

        # Validation: is end_pos occupied by a friendly piece?
        destination_content = self.board[end_row][end_col]
        if destination_content != EMPTY:
            dest_piece_type, dest_piece_color = destination_content
            if dest_piece_color == self.current_player:
                print(f"Invalid move: cannot capture your own piece at {end_pos}")
                return False
        
        # Pawn specific capture validation: must capture diagonally
        if isinstance(piece_obj, Pawn):
            # If it's a diagonal move, there must be an opponent piece to capture or it's invalid
            if start_col != end_col: # Diagonal move
                if destination_content == EMPTY:
                    print("Invalid pawn move: diagonal movement only for captures, but destination is empty.")
                    return False
                elif destination_content[1] == self.current_player: # Trying to capture own piece
                    print("Invalid pawn move: cannot capture own piece.") # Should be caught above, but good to be explicit
                    return False
            # If it's a forward move, the destination must be empty
            else: # Forward move
                if destination_content != EMPTY:
                    print("Invalid pawn move: cannot move forward onto an occupied square.")
                    return False


        # --- Castling Pre-validation (before temporary board modification for self-check) ---
        is_castling_move = False
        rook_original_pos_for_castling = None # Store rook's original position if castling
        rook_new_pos_for_castling = None      # Store rook's new position if castling
        original_rook_piece_content = None    # Store the actual rook piece tuple

        if isinstance(piece_obj, King) and abs(start_col - end_col) == 2:
            is_castling_move = True
            king_color = self.current_player 
            opponent_color = BLACK if king_color == WHITE else WHITE
            king_current_row = start_row # King's current row

            # 1. King must not be in check currently.
            if self.is_in_check(king_color):
                print("Invalid castling: King is currently in check.")
                return False

            # 2. Determine direction and check if King passes through an attacked square.
            # Path emptiness for pieces was already checked by flags passed to King.get_valid_moves.
            king_passes_through_col = -1
            if end_col > start_col: # King-side castling (e.g., e1g1 -> king moves from col 4 to 6)
                king_passes_through_col = start_col + 1 # f-file (col 5)
                rook_original_pos_for_castling = (king_current_row, 7) # h-file (col 7)
                rook_new_pos_for_castling = (king_current_row, king_passes_through_col) # Rook to f-file
            else: # Queen-side castling (e.g., e1c1 -> king moves from col 4 to 2)
                king_passes_through_col = start_col - 1 # d-file (col 3)
                rook_original_pos_for_castling = (king_current_row, 0) # a-file (col 0)
                rook_new_pos_for_castling = (king_current_row, king_passes_through_col) # Rook to d-file
                # Queen-side also requires the square king "skips over" (b-file for white, start_col - 2) to be unattacked by some strict interpretations.
                # However, standard rules usually only care about squares the king *passes over* or *lands on*.
                # The square board[start_row][start_col-2] (c-file for white) is end_pos, which is checked by main self-check.
                # So, only king_passes_through_col (d-file for white) needs checking here for "passing through".

            if self.is_square_attacked((king_current_row, king_passes_through_col), opponent_color):
                print(f"Invalid castling: King cannot pass through an attacked square {(king_current_row, king_passes_through_col)}.")
                return False
            
            # Store original rook piece for later use in temporary move and revert
            original_rook_piece_content = self.board[rook_original_pos_for_castling[0]][rook_original_pos_for_castling[1]]
            if original_rook_piece_content == EMPTY or original_rook_piece_content[0] != ROOK_T:
                 print(f"Error: Rook for castling not found or not a rook at {rook_original_pos_for_castling}.")
                 return False # Should not happen if can_castle flags were set correctly

        # --- Actual Move Execution (temporary first for self-check) ---
        original_board_state_at_start = self.board[start_row][start_col] # This is the King
        original_board_state_at_end = self.board[end_row][end_col]       # This is where King lands

        # Temporarily move the King
        self.board[end_row][end_col] = original_board_state_at_start
        self.board[start_row][start_col] = EMPTY

        # If castling, also temporarily move the rook
        if is_castling_move:
            self.board[rook_new_pos_for_castling[0]][rook_new_pos_for_castling[1]] = original_rook_piece_content
            self.board[rook_original_pos_for_castling[0]][rook_original_pos_for_castling[1]] = EMPTY
            
        # Check if this move (King's move, and Rook's if castling) puts the current player's king in check
        # This covers the king landing on an attacked square.
        if self.is_in_check(self.current_player):
            # Revert King's move
            self.board[start_row][start_col] = original_board_state_at_start
            self.board[end_row][end_col] = original_board_state_at_end
            # If castling, also revert rook's move
            if is_castling_move:
                self.board[rook_original_pos_for_castling[0]][rook_original_pos_for_castling[1]] = original_rook_piece_content
                self.board[rook_new_pos_for_castling[0]][rook_new_pos_for_castling[1]] = EMPTY # Assuming rook's new square was empty before this transaction
            
            print(f"Invalid move: You cannot leave your King in check (or landed in check during castling).")
            return False
        
        # --- If all checks passed, commit the move (board is already in desired state) and update has_moved status ---

        # Handle En Passant capture: removing the captured pawn.
        # The self.en_passant_target_square here is from the *previous* turn.
        # piece_obj is the pawn making the capture. start_pos and end_pos are its move.
        captured_en_passant_flag = False # To avoid printing normal capture message for EP
        if isinstance(piece_obj, Pawn) and end_pos == self.en_passant_target_square and start_col != end_col:
            # This was an en passant capture. The piece_obj (capturing pawn) has already been moved to end_pos.
            # We need to remove the pawn that was "jumped".
            captured_pawn_row = -1
            if piece_obj.color == WHITE: # White pawn captured en passant (e.g., moved from row 3 to row 2)
                captured_pawn_row = end_row + 1 # Captured black pawn is one row below white's landing square (on row 3)
            else: # Black pawn captured en passant (e.g., moved from row 4 to row 5)
                captured_pawn_row = end_row - 1 # Captured white pawn is one row above black's landing square (on row 4)
            
            # Ensure the captured pawn row is valid and actually remove the piece
            if 0 <= captured_pawn_row <= 7:
                # For robustness, check if the piece being removed is actually an opponent's pawn.
                # This should be guaranteed by valid en passant rules and target square setting.
                piece_being_removed = self.board[captured_pawn_row][end_col]
                if piece_being_removed != EMPTY and piece_being_removed[0] == PAWN_T and piece_being_removed[1] != piece_obj.color:
                    print(f"En Passant! Captured {PIECE_CLASSES[piece_being_removed[0]](piece_being_removed[1])} at {(captured_pawn_row, end_col)}")
                    self.board[captured_pawn_row][end_col] = EMPTY
                    captured_en_passant_flag = True
                else:
                    # This condition should ideally not be met if all EP logic is correct.
                    print(f"Warning: En passant capture attempted at {end_pos}, but expected captured pawn at {(captured_pawn_row, end_col)} was not valid: {piece_being_removed}.")
            else:
                 print(f"Warning: Invalid row for captured pawn during en passant: {captured_pawn_row}")
        
        # Update has_moved status for the primary piece that moved (King or Rook from initial position).
        # The key for self.piece_has_moved is the *original* position of the King/Rook.
        # Using piece_obj.__class__ to ensure we are checking the actual type of the piece that moved.
        if piece_obj.__class__ == King:
            king_original_fixed_pos = (7 if piece_obj.color == WHITE else 0, 4)
            if king_original_fixed_pos == start_pos : # Check if king moved from its original square
                 self.piece_has_moved[king_original_fixed_pos] = True
        elif piece_obj.__class__ == Rook:
            # Check if the rook moved from any of its initial positions
            if start_pos in self.piece_has_moved and self.board[end_row][end_col][0] == ROOK_T : # Ensure the piece that landed is a rook
                 # self.piece_has_moved only contains initial K/R positions.
                 # If start_pos is a key, it means a K or R started there.
                 # If it's a rook, update its status.
                 self.piece_has_moved[start_pos] = True
        
        # If castling, also update has_moved for the rook from its original fixed position.
        if is_castling_move:
             # rook_original_pos_for_castling is already the key for the specific rook that moved.
            if rook_original_pos_for_castling in self.piece_has_moved:
                 self.piece_has_moved[rook_original_pos_for_castling] = True
            print(f"Castling successful. Rook moved from {rook_original_pos_for_castling} to {rook_new_pos_for_castling}")

        print(f"Moved {PIECE_CLASSES[original_board_state_at_start[0]](original_board_state_at_start[1])} from {start_pos} to {end_pos}")
        if original_board_state_at_end != EMPTY and not captured_en_passant_flag: 
            # This check is mostly for non-castling captures.
            # If captured_en_passant_flag is true, the EP capture message was already printed.
            print(f"Captured {PIECE_CLASSES[original_board_state_at_end[0]](original_board_state_at_end[1])} at {end_pos}")

        # --- En Passant Target Setting (for the next turn) ---
        # This must be done AFTER the current move is fully processed, including EP capture.
        # original_board_state_at_start holds the piece type and color that moved.
        moved_piece_type = original_board_state_at_start[0]
        moved_piece_color = original_board_state_at_start[1]

        # Reset en_passant_target_square for the next turn, then set it if applicable
        # The self.en_passant_target_square used for the *current* move's validation was from the *previous* turn.
        if moved_piece_type == PAWN_T and abs(start_row - end_row) == 2:
            if moved_piece_color == WHITE:
                new_ep_target = (start_row - 1, start_col) # Square behind white pawn
            else: # BLACK pawn
                new_ep_target = (start_row + 1, start_col) # Square behind black pawn
            self.en_passant_target_square = new_ep_target
            # print(f"Debug: En passant target for next turn set to {self.en_passant_target_square}")
        else:
            self.en_passant_target_square = None
            # print(f"Debug: En passant target for next turn reset to None")
        
        # --- Pawn Promotion Check ---
        # piece_obj is the original piece object that initiated the move.
        # Check if the moved piece was a pawn and reached the promotion rank.
        if isinstance(piece_obj, Pawn):
            pawn_color = piece_obj.color # Color of the pawn that moved
            promotion_rank_reached = False
            if pawn_color == WHITE and end_row == 0: # White pawn reaches rank 8 (row 0)
                promotion_rank_reached = True
            elif pawn_color == BLACK and end_row == 7: # Black pawn reaches rank 1 (row 7)
                promotion_rank_reached = True
            
            if promotion_rank_reached:
                # Signal GUI that promotion is required instead of handling via input()
                # The board still has the pawn at end_pos.
                # The game state (current_player, en_passant_target) should be set *after* promotion is chosen.
                # So, we return a special status here.
                # next_turn() and en_passant_target_square setting will be deferred until after promotion.
                return ("PROMOTION", (end_row, end_col), pawn_color)
                
        # If not promotion, set en_passant_target for next turn and switch player
        if moved_piece_type == PAWN_T and abs(start_row - end_row) == 2:
            if moved_piece_color == WHITE:
                new_ep_target = (start_row - 1, start_col) 
            else: 
                new_ep_target = (start_row + 1, start_col) 
            self.en_passant_target_square = new_ep_target
        else:
            self.en_passant_target_square = None

        self.next_turn() 
        return True # Standard successful move

    def complete_pawn_promotion(self, square, color, choice_char):
        """Completes the pawn promotion after GUI interaction."""
        row, col = square
        valid_choices = {
            'q': QUEEN_T, 'r': ROOK_T, 'b': BISHOP_T, 'n': KNIGHT_T
        }
        chosen_piece_type = valid_choices.get(choice_char.lower())

        if chosen_piece_type is None:
            print(f"Error: Invalid promotion choice '{choice_char}'. Defaulting to Queen.")
            chosen_piece_type = QUEEN_T
        
        self.board[row][col] = (chosen_piece_type, color)
        # Note: The piece on board is now promoted. The 'has_moved' status for this new piece
        # is implicitly true as it's a new piece. self.piece_has_moved tracks original K/R.
        
        # Now that promotion is done, finalize turn-dependent states:
        # En passant target should have been determined based on the pawn's *original* 2-square move,
        # which is handled by the calling context (GUI will call this, then finalize turn).
        # For simplicity, if move_piece returned "PROMOTION", it means the pawn move itself
        # did not set en_passant_target_square yet.
        # We need to know if the original pawn move was a 2-square advance.
        # This info is lost if we only call complete_pawn_promotion.
        #
        # Let's adjust: move_piece will handle EP target setting *before* returning "PROMOTION".
        # Then, complete_pawn_promotion will just call next_turn().
        
        self.next_turn() # Finalize the turn
        print(f"Pawn at {self.coords_to_algebraic(square)} promoted to {PIECE_CLASSES[chosen_piece_type](color).__class__.__name__}.")


    def next_turn(self):
        """Switches the current player's turn."""
        self.current_player = BLACK if self.current_player == WHITE else WHITE
        # Verbose print handled by play_game now
        # print(f"It is now {self.current_player}'s turn.")

    def find_king(self, king_color):
        """Finds the position of the king of the specified color."""
        for r in range(8):
            for c in range(8):
                cell = self.board[r][c]
                if cell != EMPTY:
                    piece_type, color = cell
                    if piece_type == KING_T and color == king_color:
                        return (r, c)
        return None # Should not happen in a normal game

    def is_square_attacked(self, square, attacker_color):
        """Checks if a given square is attacked by any piece of the attacker_color."""
        # Create a simplified board for validation, as used in move_piece
        # This represents occupied squares (1) vs empty (0) for piece move calculation.
        simple_board_for_validation = [[(EMPTY if self.board[r][c] == EMPTY else 1) for c in range(8)] for r in range(8)]

        for r in range(8):
            for c in range(8):
                cell_content = self.board[r][c]
                if cell_content == EMPTY:
                    continue

                piece_type, piece_color = cell_content
                if piece_color == attacker_color:
                    current_piece_obj = PIECE_CLASSES[piece_type](piece_color)
                    current_pos = (r, c)
                    
                    valid_moves_for_piece = []
                    if isinstance(current_piece_obj, Pawn):
                        # For pawns, only diagonal attacks matter for is_square_attacked.
                        # En passant is an attack, so pass the target square.
                        valid_moves_for_piece = current_piece_obj.get_valid_moves(
                            simple_board_for_validation, current_pos, attacks_only=True,
                            en_passant_target_square_coord=self.en_passant_target_square
                        )
                    else:
                        valid_moves_for_piece = current_piece_obj.get_valid_moves(
                            simple_board_for_validation, current_pos
                        )
                    
                    if square in valid_moves_for_piece:
                        # print(f"Debug: Square {square} is attacked by {attacker_color} {current_piece_obj} from {current_pos} via moves {valid_moves_for_piece}")
                        return True
        return False

    def is_in_check(self, player_color):
        """Checks if the king of player_color is currently in check."""
        king_pos = self.find_king(player_color)
        if not king_pos:
            # This should ideally not happen in a valid game state.
            print(f"Error: King of {player_color} not found on the board.")
            return False # Or raise an error
        
        opponent_color = BLACK if player_color == WHITE else WHITE
        return self.is_square_attacked(king_pos, opponent_color)

    def is_checkmate(self, player_color):
        """Checks if the given player_color is in checkmate."""
        if not self.is_in_check(player_color):
            return False # Not in check, so cannot be checkmate.

        # Iterate through all pieces of player_color
        for r_start in range(8):
            for c_start in range(8):
                cell_content = self.board[r_start][c_start]
                if cell_content == EMPTY:
                    continue

                piece_type, piece_color_on_board = cell_content
                if piece_color_on_board == player_color:
                    current_piece_obj = PIECE_CLASSES[piece_type](player_color)
                    start_pos = (r_start, c_start)

                    # Use a simplified board for generating potential moves, as piece logic expects.
                    # This board marks squares as 0 (empty) or 1 (occupied).
                    simple_board_for_validation = [[(EMPTY if self.board[r_idx][c_idx] == EMPTY else 1) for c_idx in range(8)] for r_idx in range(8)]

                    potential_moves = []
                    if isinstance(current_piece_obj, Pawn):
                        # Pawns need full move logic (not just attacks_only) to see if they can block check or move king's path
                        potential_moves = current_piece_obj.get_valid_moves(simple_board_for_validation, start_pos, attacks_only=False)
                    else:
                        potential_moves = current_piece_obj.get_valid_moves(simple_board_for_validation, start_pos)
                    
                    for end_pos in potential_moves:
                        r_end, c_end = end_pos
                        
                        # Before checking if the move is valid (e.g., not capturing own piece),
                        # we must simulate it to see if it resolves the check.
                        # The `move_piece` method's internal check logic is what we need.

                        # Further validation for the generated move (e.g. pawn forward onto occupied)
                        # This is already part of move_piece, but we need to check it here too
                        # before attempting the temporary move for check validation.
                        
                        # Check if end_pos is occupied by a friendly piece
                        dest_content_sim = self.board[r_end][c_end]
                        if dest_content_sim != EMPTY and dest_content_sim[1] == player_color:
                            continue # Cannot move to a square occupied by a friendly piece

                        # Pawn specific validation:
                        if isinstance(current_piece_obj, Pawn):
                            if c_start != c_end: # Diagonal move
                                if dest_content_sim == EMPTY: # Must capture if moving diagonally
                                    continue
                            else: # Forward move
                                if dest_content_sim != EMPTY: # Cannot move forward onto an occupied square
                                    continue
                        
                        # --- Simulate the move ---
                        original_start_square_content = self.board[r_start][c_start]
                        original_end_square_content = self.board[r_end][c_end]

                        self.board[r_end][c_end] = original_start_square_content
                        self.board[r_start][c_start] = EMPTY
                        
                        # Check if the player is still in check
                        still_in_check = self.is_in_check(player_color)
                        
                        # Revert the move
                        self.board[r_start][c_start] = original_start_square_content
                        self.board[r_end][c_end] = original_end_square_content
                        # --- End simulation ---

                        if not still_in_check:
                            # Found a legal move to get out of check
                            # print(f"Debug: {player_color} can escape check via {start_pos} to {end_pos}")
                            return False
        
        # If loop completes, no legal move was found to get out of check.
        return True

    def get_validated_moves_for_piece(self, start_pos):
        """
        Calculates all valid moves for a piece at start_pos,
        ensuring each move does not leave the current player's king in check.
        Returns a list of (end_row, end_col) tuples.
        """
        start_row, start_col = start_pos
        piece_obj = self.get_piece_at(start_pos)

        if piece_obj is None or piece_obj.color != self.current_player:
            return []

        # Generate potential moves using the same logic as in the beginning of move_piece
        simple_board_for_validation = [[(EMPTY if self.board[r][c] == EMPTY else 1) for c in range(8)] for r in range(8)]
        potential_moves = []

        # Logic to get potential_moves, similar to how it's done in move_piece
        if isinstance(piece_obj, King):
            king_color = piece_obj.color
            king_original_row = 7 if king_color == WHITE else 0
            king_at_original_pos_key = (king_original_row, 4)
            
            king_has_moved_check = True
            if start_pos == king_at_original_pos_key:
                king_has_moved_check = self.piece_has_moved.get(king_at_original_pos_key, True)
            piece_obj.has_moved = king_has_moved_check

            can_castle_kingside = False
            if not piece_obj.has_moved:
                rook_kingside_pos_key = (king_original_row, 7)
                rook_kingside_moved = self.piece_has_moved.get(rook_kingside_pos_key, True)
                if not rook_kingside_moved and \
                   self.board[king_original_row][5] == EMPTY and \
                   self.board[king_original_row][6] == EMPTY:
                    can_castle_kingside = True
            
            can_castle_queenside = False
            if not piece_obj.has_moved:
                rook_queenside_pos_key = (king_original_row, 0)
                rook_queenside_moved = self.piece_has_moved.get(rook_queenside_pos_key, True)
                if not rook_queenside_moved and \
                   self.board[king_original_row][1] == EMPTY and \
                   self.board[king_original_row][2] == EMPTY and \
                   self.board[king_original_row][3] == EMPTY:
                    can_castle_queenside = True
                                   
            potential_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos,
                                                      can_castle_kingside=can_castle_kingside,
                                                      can_castle_queenside=can_castle_queenside)
        elif isinstance(piece_obj, Pawn):
             potential_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos, 
                                                       attacks_only=False, 
                                                       en_passant_target_square_coord=self.en_passant_target_square)
        else:
            potential_moves = piece_obj.get_valid_moves(simple_board_for_validation, start_pos)

        truly_valid_moves = []
        for end_pos_candidate in potential_moves:
            end_row_candidate, end_col_candidate = end_pos_candidate

            # --- Perform pre-move validation checks (like in move_piece) ---
            destination_content_sim = self.board[end_row_candidate][end_col_candidate]
            if destination_content_sim != EMPTY and destination_content_sim[1] == self.current_player:
                continue 

            if isinstance(piece_obj, Pawn):
                if start_col != end_col_candidate: 
                    if end_pos_candidate == self.en_passant_target_square:
                        pass 
                    elif destination_content_sim == EMPTY:
                        continue 
                else: 
                    if destination_content_sim != EMPTY:
                        continue 
            
            is_castling_move_sim = isinstance(piece_obj, King) and abs(start_col - end_col_candidate) == 2
            if is_castling_move_sim:
                opponent_color = BLACK if self.current_player == WHITE else WHITE
                if self.is_in_check(self.current_player): 
                    continue 
                
                king_passes_through_col_sim = start_col + 1 if end_col_candidate > start_col else start_col - 1
                if self.is_square_attacked((start_row, king_passes_through_col_sim), opponent_color):
                    continue

            # --- Simulate the move and check for self-check ---
            original_start_square_content_sim = self.board[start_row][start_col]
            original_end_square_content_sim = self.board[end_row_candidate][end_col_candidate]
            
            rook_original_pos_sim_val = None
            rook_new_pos_sim_val = None
            original_rook_content_sim_val = None
            captured_pawn_pos_ep_sim = None 
            original_captured_pawn_content_ep = None # Store content if EP capture occurs

            self.board[end_row_candidate][end_col_candidate] = original_start_square_content_sim
            self.board[start_row][start_col] = EMPTY

            if is_castling_move_sim:
                king_current_row_sim_val = start_row
                if end_col_candidate > start_col: 
                    rook_original_pos_sim_val = (king_current_row_sim_val, 7)
                    rook_new_pos_sim_val = (king_current_row_sim_val, start_col + 1)
                else: 
                    rook_original_pos_sim_val = (king_current_row_sim_val, 0)
                    rook_new_pos_sim_val = (king_current_row_sim_val, start_col - 1)
                
                if rook_original_pos_sim_val:
                    original_rook_content_sim_val = self.board[rook_original_pos_sim_val[0]][rook_original_pos_sim_val[1]]
                    if original_rook_content_sim_val != EMPTY and original_rook_content_sim_val[0] == ROOK_T:
                        self.board[rook_new_pos_sim_val[0]][rook_new_pos_sim_val[1]] = original_rook_content_sim_val
                        self.board[rook_original_pos_sim_val[0]][rook_original_pos_sim_val[1]] = EMPTY
                    else: 
                        self.board[start_row][start_col] = original_start_square_content_sim
                        self.board[end_row_candidate][end_col_candidate] = original_end_square_content_sim
                        continue 
            elif isinstance(piece_obj, Pawn) and end_pos_candidate == self.en_passant_target_square and start_col != end_col_candidate:
                captured_pawn_row_sim = end_row_candidate + 1 if piece_obj.color == WHITE else end_row_candidate - 1
                captured_pawn_pos_ep_sim = (captured_pawn_row_sim, end_col_candidate)
                original_captured_pawn_content_ep = self.board[captured_pawn_row_sim][end_col_candidate] # Store it
                self.board[captured_pawn_row_sim][end_col_candidate] = EMPTY

            if not self.is_in_check(self.current_player):
                truly_valid_moves.append(end_pos_candidate)
            
            # Revert the board
            self.board[start_row][start_col] = original_start_square_content_sim
            self.board[end_row_candidate][end_col_candidate] = original_end_square_content_sim
            if is_castling_move_sim and rook_original_pos_sim_val and original_rook_content_sim_val: 
                self.board[rook_original_pos_sim_val[0]][rook_original_pos_sim_val[1]] = original_rook_content_sim_val
                if rook_new_pos_sim_val: 
                     self.board[rook_new_pos_sim_val[0]][rook_new_pos_sim_val[1]] = EMPTY
            elif captured_pawn_pos_ep_sim: 
                self.board[captured_pawn_pos_ep_sim[0]][captured_pawn_pos_ep_sim[1]] = original_captured_pawn_content_ep # Restore EP captured pawn
        
        return truly_valid_moves

    # def _handle_pawn_promotion(self, position, pawn_color):
    #     """Handles the pawn promotion process by prompting the user for a piece choice."""
    #     row, col = position
    #     valid_choices = {
    #         'q': QUEEN_T, 'r': ROOK_T, 'b': BISHOP_T, 'n': KNIGHT_T
    #     }
    #     choice_symbols = {'q': 'Queen', 'r': 'Rook', 'b': 'Bishop', 'n': 'Knight'}

    #     while True:
    #         user_input = input(f"Pawn promotion at {ChessGame.coords_to_algebraic(position)}! Choose piece (Q, R, B, N): ").strip().lower()
    #         if user_input in valid_choices:
    #             chosen_piece_type = valid_choices[user_input]
    #             self.board[row][col] = (chosen_piece_type, pawn_color)
    #             # The new piece object itself doesn't need its has_moved set here,
    #             # as self.piece_has_moved tracks original K/R.
    #             # Promoted pieces are not original K/R for castling.
    #             print(f"Pawn promoted to {choice_symbols[user_input]}.")
    #             break
    #         else:
    #             print("Invalid choice. Please enter Q, R, B, or N.")

    @staticmethod
    def coords_to_algebraic(coords):
        """Converts (row, col) to algebraic notation string like 'a1', 'h8'."""
        if coords is None: return "N/A"
        row, col = coords
        if not (0 <= row <= 7 and 0 <= col <= 7): return "N/A"
        file = chr(ord('a') + col)
        rank = str(8 - row)
        return file + rank

    def play_game(self, max_turns=50): # Added max_turns for a simple end condition
        """Main game loop for interactive play."""
        print("Starting chess game. Type 'quit' to end the game.")
        print("Enter moves in algebraic notation (e.g., 'e2 e4').")
        
        # Test algebraic_to_coords (can be removed or kept for debugging)
        # print("Testing algebraic_to_coords internal function:")
        # print(f"e2 -> {ChessGame.algebraic_to_coords('e2')}") # Expected: (6, 4)
        # print(f"a1 -> {ChessGame.algebraic_to_coords('a1')}") # Expected: (7, 0)
        # print(f"h8 -> {ChessGame.algebraic_to_coords('h8')}") # Expected: (0, 7)

        while self.turn_count < max_turns:
            self.display_board()
            print(f"{self.current_player.capitalize()}'s turn (Turn {self.turn_count + 1}/{max_turns}).")
            
            user_input = input("Enter your move (e.g., 'e2 e4') or 'quit': ").strip().lower()

            if user_input == 'quit':
                print("Game ended by user.")
                break

            parts = user_input.split()
            if len(parts) != 2:
                print("Invalid input format. Please use format: 'start_square end_square' (e.g., 'e2 e4'). Try again.")
                continue

            start_algebraic, end_algebraic = parts[0], parts[1]
            
            start_pos = ChessGame.algebraic_to_coords(start_algebraic)
            end_pos = ChessGame.algebraic_to_coords(end_algebraic)

            if start_pos is None or end_pos is None:
                print(f"Invalid algebraic notation: '{start_algebraic}' or '{end_algebraic}' is not valid (e.g., use 'a1' through 'h8'). Try again.")
                continue
            
            move_successful = self.move_piece(start_pos, end_pos)
            
            if move_successful:
                self.turn_count += 1 # Increment turn count only on successful move
                # self.current_player has been switched by next_turn() called in move_piece
                
                # Announce check if the new current player (whose turn it now is) is in check
                if self.is_in_check(self.current_player):
                    print(f"!!! {self.current_player.capitalize()} is in check !!!")
                    # Check for checkmate
                    if self.is_checkmate(self.current_player):
                        self.display_board()
                        winning_color = BLACK if self.current_player == WHITE else WHITE
                        print(f"Checkmate! {winning_color.capitalize()} wins!")
                        return # End game
                
                # The announcement of whose turn it is now will happen at the start of the next loop iteration.
            # else:
                # If move was not successful, move_piece already prints the error.
                # Loop continues, same player's turn.
                # print("Please try your move again.")

            if self.turn_count >= max_turns:
                print("\nMaximum turns reached. Game over.")
                self.display_board() # Show final board
                break # Break from the while loop
        else: # Only executed if the while loop finishes normally (max_turns reached without a 'break' from checkmate or quit)
             if self.turn_count >= max_turns : 
                print("\nMaximum turns reached. Game over by turn limit.")
                self.display_board()


if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
    # Example of setting up a checkmate scenario for testing (e.g. Fool's Mate)
    # game = ChessGame()
    # # White: f2-f3 (6,5) -> (5,5)
    # game.move_piece(ChessGame.algebraic_to_coords("f2"), ChessGame.algebraic_to_coords("f3"))
    # # Black: e7-e5 (1,4) -> (3,4)
    # game.move_piece(ChessGame.algebraic_to_coords("e7"), ChessGame.algebraic_to_coords("e5"))
    # # White: g2-g4 (6,6) -> (4,6)
    # game.move_piece(ChessGame.algebraic_to_coords("g2"), ChessGame.algebraic_to_coords("g4"))
    # # Black: Qd8-h4# (0,3) -> (4,7)
    # game.move_piece(ChessGame.algebraic_to_coords("d8"), ChessGame.algebraic_to_coords("h4"))
    # game.play_game() # This won't run if checkmate ends the game in move_piece/play_game
