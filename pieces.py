# pieces.py
from abc import ABC, abstractmethod

# Define color constants (already in chess_game.py, but useful here for piece logic)
WHITE = "white"
BLACK = "black"
EMPTY = 0 # Assuming EMPTY is defined in chess_game.py or common constants

class Piece(ABC):
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        # self.position = position # Position is dynamic, will be passed to get_valid_moves

    @abstractmethod
    def get_valid_moves(self, board, position):
        """
        Returns a list of valid (row, col) tuples for the piece.
        'board' is the current board state.
        'position' is the current (row, col) of the piece.
        """
        pass

    def _is_on_board(self, r, c):
        return 0 <= r <= 7 and 0 <= c <= 7

    def __str__(self):
        # Simplified str, as position is not stored directly in the object anymore for get_valid_moves
        return f"{self.color.capitalize()} {self.__class__.__name__}"


class Pawn(Piece):
    def get_valid_moves(self, board, position, attacks_only=False, en_passant_target_square_coord=None):
        moves = []
        r, c = position
        direction = -1 if self.color == WHITE else 1  # White moves from row 7 to 0, Black from 0 to 7
        start_row = 6 if self.color == WHITE else 1

        if not attacks_only:
            # Forward 1 square
            # 'board' here is simple_board_for_validation (0 for empty, 1 for occupied)
            if self._is_on_board(r + direction, c) and board[r + direction][c] == EMPTY:
                moves.append((r + direction, c))
                # Forward 2 squares from starting position
                if r == start_row and self._is_on_board(r + 2 * direction, c) and board[r + 2 * direction][c] == EMPTY:
                    moves.append((r + 2 * direction, c))

        # Diagonal attack moves (for normal capture or just checking attacks)
        for dc in [-1, 1]:
            attack_r, attack_c = r + direction, c + dc
            if self._is_on_board(attack_r, attack_c):
                # If attacks_only is true, we add it regardless of whether the target square on the simple_board is empty or not.
                # If attacks_only is false (meaning generating actual moves):
                #   - chess_game.move_piece will later validate if it's a valid capture (opponent piece) or empty (invalid diag move).
                #   - For now, we include it as a potential move.
                moves.append((attack_r, attack_c))
        
        # En Passant
        if en_passant_target_square_coord:
            ep_r, ep_c = en_passant_target_square_coord
            # White pawn en passant requirements:
            # - White pawn must be on its 5th rank (row 3 in 0-indexed)
            # - Target square must be on its 6th rank (row 2 in 0-indexed)
            # - Target square must be adjacent to the current pawn's column
            if self.color == WHITE and r == 3 and ep_r == 2 and abs(c - ep_c) == 1:
                moves.append(en_passant_target_square_coord)
            # Black pawn en passant requirements:
            # - Black pawn must be on its 4th rank (row 4 in 0-indexed)
            # - Target square must be on its 3rd rank (row 5 in 0-indexed)
            # - Target square must be adjacent to the current pawn's column
            elif self.color == BLACK and r == 4 and ep_r == 5 and abs(c - ep_c) == 1:
                moves.append(en_passant_target_square_coord)
        return moves

class Rook(Piece):
    def get_valid_moves(self, board, position):
        moves = []
        r, c = position
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Right, Left, Down, Up

        for dr, dc in directions:
            for i in range(1, 8):
                nr, nc = r + dr * i, c + dc * i
                if not self._is_on_board(nr, nc):
                    break
                moves.append((nr, nc)) # Add the square as a potential move
                if board[nr][nc] != EMPTY: # If it's occupied by any piece
                    break # Then stop (can't move further in this direction)
        return moves

class Knight(Piece):
    def get_valid_moves(self, board, position):
        moves = []
        r, c = position
        potential_moves = [
            (r + 2, c + 1), (r + 2, c - 1), (r - 2, c + 1), (r - 2, c - 1),
            (r + 1, c + 2), (r + 1, c - 2), (r - 1, c + 2), (r - 1, c - 2)
        ]
        for move in potential_moves:
            if self._is_on_board(move[0], move[1]):
                # Knights are not blocked, they jump.
                # We don't check board[move[0]][move[1]] here for EMPTY
                # as per instruction "should not consider whether a square is occupied"
                moves.append(move)
        return moves

class Bishop(Piece):
    def get_valid_moves(self, board, position):
        moves = []
        r, c = position
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Diagonal directions

        for dr, dc in directions:
            for i in range(1, 8):
                nr, nc = r + dr * i, c + dc * i
                if not self._is_on_board(nr, nc):
                    break
                moves.append((nr, nc)) # Add the square as a potential move
                if board[nr][nc] != EMPTY: # If it's occupied by any piece
                    break # Then stop (can't move further in this direction)
        return moves

class Queen(Piece):
    def get_valid_moves(self, board, position):
        # Combines Rook and Bishop moves
        moves = []
        # Rook-like moves
        r_moves = Rook(self.color).get_valid_moves(board, position)
        moves.extend(r_moves)
        # Bishop-like moves
        b_moves = Bishop(self.color).get_valid_moves(board, position)
        moves.extend(b_moves)
        return list(set(moves)) # Remove duplicates if any

class King(Piece):
    def get_valid_moves(self, board, position):
        moves = []
        r, c = position
        potential_moves = [
            (r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1),
            (r + 1, c + 1), (r + 1, c - 1), (r - 1, c + 1), (r - 1, c - 1)
        ]
        for move in potential_moves:
            if self._is_on_board(move[0], move[1]):
                # We don't check board[move[0]][move[1]] here for EMPTY
                # as per instruction "should not consider whether a square is occupied"
                moves.append(move)
        return moves

if __name__ == '__main__':
    # Example usage (board needed for get_valid_moves)
    # This is a simplified board for testing; real board comes from ChessGame
    empty_board_for_testing = [[EMPTY for _ in range(8)] for _ in range(8)]

    white_pawn = Pawn(WHITE)
    # Test standard moves
    print(f"Pawn W at (6,0) valid moves (standard): {white_pawn.get_valid_moves(empty_board_for_testing, (6,0))}")
    # Test attacks_only
    print(f"Pawn W at (6,0) valid moves (attacks_only): {white_pawn.get_valid_moves(empty_board_for_testing, (6,0), attacks_only=True)}")
    # Test en passant
    # White pawn at (3,4) (e.g. e5), en_passant_target_square_coord is (2,3) (d6) or (2,5) (f6)
    white_pawn_for_ep = Pawn(WHITE) # color, original_pos not used by get_valid_moves directly
    print(f"Pawn W at (3,4) with EP target (2,3): {white_pawn_for_ep.get_valid_moves(empty_board_for_testing, (3,4), en_passant_target_square_coord=(2,3))}")
    print(f"Pawn W at (3,4) with EP target (2,5): {white_pawn_for_ep.get_valid_moves(empty_board_for_testing, (3,4), en_passant_target_square_coord=(2,5))}")
    print(f"Pawn W at (3,4) with EP target (2,4) (invalid): {white_pawn_for_ep.get_valid_moves(empty_board_for_testing, (3,4), en_passant_target_square_coord=(2,4))}")
    # Black pawn at (4,3) (e.g. d4), en_passant_target_square_coord is (5,2) (c3) or (5,4) (e3)
    black_pawn_for_ep = Pawn(BLACK)
    print(f"Pawn B at (4,3) with EP target (5,2): {black_pawn_for_ep.get_valid_moves(empty_board_for_testing, (4,3), en_passant_target_square_coord=(5,2))}")


    black_rook = Rook(BLACK)
    # Place a blocker for the rook
    test_board_rook = [[EMPTY for _ in range(8)] for _ in range(8)]
    test_board_rook[3][0] = (Pawn(WHITE), WHITE) # A white pawn
    print(f"Rook at (0,0) valid moves on a board with a blocker at (3,0): {black_rook.get_valid_moves(test_board_rook, (0,0))}")


    white_knight = Knight(WHITE)
    print(f"Knight at (7,1) valid moves: {white_knight.get_valid_moves(empty_board_for_testing, (7,1))}")

    black_bishop = Bishop(BLACK)
    print(f"Bishop at (0,2) valid moves: {black_bishop.get_valid_moves(empty_board_for_testing, (0,2))}")

    white_queen = Queen(WHITE)
    print(f"Queen at (7,3) valid moves: {white_queen.get_valid_moves(empty_board_for_testing, (7,3))}")
    
    black_king = King(BLACK)
    print(f"King at (0,4) valid moves: {black_king.get_valid_moves(empty_board_for_testing, (0,4))}")
