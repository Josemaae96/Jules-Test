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


        # If all checks pass, make the move
        piece_to_move = self.board[start_row][start_col]
        self.board[end_row][end_col] = piece_to_move
        self.board[start_row][start_col] = EMPTY
        # print(f"Moved {piece_obj} from {start_pos} to {end_pos}") # Piece_obj is an instance, use board data
        print(f"Moved {PIECE_CLASSES[piece_to_move[0]](piece_to_move[1])} from {start_pos} to {end_pos}")
        
        self.next_turn()
        return True

    def next_turn(self):
        """Switches the current player's turn."""
        self.current_player = BLACK if self.current_player == WHITE else WHITE
        # Verbose print handled by play_game now
        # print(f"It is now {self.current_player}'s turn.")

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
                self.turn_count += 1
                # next_turn() is called inside move_piece if successful.
                # The announcement of whose turn it is now will happen at the start of the next loop iteration.
            # else:
                # If move was not successful, move_piece already prints the error.
                # Loop continues, same player's turn.
                # print("Please try your move again.") # Optional additional prompt

            if self.turn_count >= max_turns:
                print("\nMaximum turns reached. Game over.")
                self.display_board() # Show final board
                break
        else: # Only executed if the loop finishes normally (not via 'break')
             if self.turn_count >= max_turns : # To ensure message is shown if loop ends due to max_turns
                print("\nMaximum turns reached. Game over.")
                self.display_board()


if __name__ == "__main__":
    game = ChessGame()
    game.play_game()
