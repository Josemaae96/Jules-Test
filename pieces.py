# pieces.py
from abc import ABC, abstractmethod

# Define color constants (already in chess_game.py, but useful here for piece logic)
WHITE = "white"
BLACK = "black"
EMPTY = 0 # Assuming EMPTY is defined in chess_game.py or common constants

class Piece(ABC):
    def __init__(self, color):
        self.color = color
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
    def get_valid_moves(self, board, position):
        moves = []
        r, c = position
        direction = -1 if self.color == WHITE else 1  # White moves from row 7 to 0, Black from 0 to 7
        start_row = 6 if self.color == WHITE else 1

        # Forward 1 square
        if self._is_on_board(r + direction, c) and board[r + direction][c] == EMPTY:
            moves.append((r + direction, c))
            # Forward 2 squares from starting position
            if r == start_row and self._is_on_board(r + 2 * direction, c) and board[r + 2 * direction][c] == EMPTY:
                moves.append((r + 2 * direction, c))

        # Diagonal captures (potential moves, not actual captures yet)
        for dc in [-1, 1]:
            if self._is_on_board(r + direction, c + dc):
                # For now, we add it as a potential move square.
                # Later, ChessGame will check if it's an actual capture.
                moves.append((r + direction, c + dc))
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
    print(f"Pawn at (6,0) valid moves: {white_pawn.get_valid_moves(empty_board_for_testing, (6,0))}")

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
