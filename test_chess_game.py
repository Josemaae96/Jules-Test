import unittest
from chess_game import ChessGame, WHITE, BLACK, EMPTY, PAWN_T, ROOK_T, KNIGHT_T, BISHOP_T, QUEEN_T, KING_T
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class TestChessGameLogic(unittest.TestCase):

    def setUp(self):
        """Set up a new ChessGame instance before each test."""
        self.game = ChessGame()

    def test_initial_board_setup(self):
        """Test if the board is set up correctly at the beginning of the game."""
        # Check specific white pieces
        self.assertEqual(self.game.board[7][0], (ROOK_T, WHITE))  # White Rook at a1
        self.assertEqual(self.game.board[7][4], (KING_T, WHITE))  # White King at e1
        self.assertEqual(self.game.board[6][0], (PAWN_T, WHITE))  # White Pawn at a2

        # Check specific black pieces
        self.assertEqual(self.game.board[0][0], (ROOK_T, BLACK))  # Black Rook at a8
        self.assertEqual(self.game.board[0][4], (KING_T, BLACK))  # Black King at e8
        self.assertEqual(self.game.board[1][0], (PAWN_T, BLACK))  # Black Pawn at a7

        # Check some empty squares
        self.assertEqual(self.game.board[3][3], EMPTY)  # d5 should be empty
        self.assertEqual(self.game.board[4][4], EMPTY)  # e4 should be empty

        # Verify piece counts (optional, but good for completeness)
        white_pieces = 0
        black_pieces = 0
        for r in range(8):
            for c in range(8):
                if self.game.board[r][c] != EMPTY:
                    _, color = self.game.board[r][c]
                    if color == WHITE:
                        white_pieces += 1
                    elif color == BLACK:
                        black_pieces += 1
        self.assertEqual(white_pieces, 16)
        self.assertEqual(black_pieces, 16)
        self.assertEqual(self.game.current_player, WHITE)

    def test_algebraic_to_coords_valid(self):
        """Test valid algebraic notation conversions."""
        self.assertEqual(ChessGame.algebraic_to_coords("a1"), (7, 0))
        self.assertEqual(ChessGame.algebraic_to_coords("h8"), (0, 7))
        self.assertEqual(ChessGame.algebraic_to_coords("e2"), (6, 4))
        self.assertEqual(ChessGame.algebraic_to_coords("d5"), (3, 3))
        self.assertEqual(ChessGame.algebraic_to_coords("g7"), (1, 6))

    def test_algebraic_to_coords_invalid(self):
        """Test invalid algebraic notation conversions."""
        self.assertIsNone(ChessGame.algebraic_to_coords("z9"))
        self.assertIsNone(ChessGame.algebraic_to_coords("a9")) # Invalid rank
        self.assertIsNone(ChessGame.algebraic_to_coords("i1")) # Invalid file
        self.assertIsNone(ChessGame.algebraic_to_coords("a10"))
        self.assertIsNone(ChessGame.algebraic_to_coords(""))
        self.assertIsNone(ChessGame.algebraic_to_coords("e2e4"))
        self.assertIsNone(ChessGame.algebraic_to_coords("e"))
        self.assertIsNone(ChessGame.algebraic_to_coords("2"))
        self.assertIsNone(ChessGame.algebraic_to_coords(None)) # Non-string input
        self.assertIsNone(ChessGame.algebraic_to_coords(123))  # Non-string input

    def test_move_piece_valid(self):
        """Test a valid piece move."""
        start_pos_alg = "e2"
        end_pos_alg = "e4"
        start_pos = ChessGame.algebraic_to_coords(start_pos_alg) # (6,4)
        end_pos = ChessGame.algebraic_to_coords(end_pos_alg)     # (4,4)
        
        original_piece = self.game.board[start_pos[0]][start_pos[1]]
        self.assertEqual(self.game.current_player, WHITE)
        
        move_successful = self.game.move_piece(start_pos, end_pos)
        
        self.assertTrue(move_successful)
        self.assertEqual(self.game.board[end_pos[0]][end_pos[1]], original_piece)
        self.assertEqual(self.game.board[start_pos[0]][start_pos[1]], EMPTY)
        self.assertEqual(self.game.current_player, BLACK) # Turn should switch

    def test_move_piece_invalid_no_piece(self):
        """Test moving from an empty square."""
        start_pos = ChessGame.algebraic_to_coords("e3") # Empty square
        end_pos = ChessGame.algebraic_to_coords("e4")
        initial_board_state = [row[:] for row in self.game.board] # Deep copy
        initial_player = self.game.current_player

        move_successful = self.game.move_piece(start_pos, end_pos)
        
        self.assertFalse(move_successful)
        self.assertEqual(self.game.board, initial_board_state) # Board should not change
        self.assertEqual(self.game.current_player, initial_player) # Player should not change

    def test_move_piece_invalid_wrong_turn(self):
        """Test moving opponent's piece."""
        start_pos = ChessGame.algebraic_to_coords("e7") # Black pawn
        end_pos = ChessGame.algebraic_to_coords("e6")
        initial_board_state = [row[:] for row in self.game.board]
        initial_player = self.game.current_player
        self.assertEqual(initial_player, WHITE) # Ensure it's White's turn

        move_successful = self.game.move_piece(start_pos, end_pos)
        
        self.assertFalse(move_successful)
        self.assertEqual(self.game.board, initial_board_state)
        self.assertEqual(self.game.current_player, initial_player)

    def test_move_piece_invalid_move_for_piece(self):
        """Test an invalid move pattern for a piece."""
        start_pos = ChessGame.algebraic_to_coords("e2") # White pawn
        end_pos = ChessGame.algebraic_to_coords("e5")   # Trying to move 3 steps
        initial_board_state = [row[:] for row in self.game.board]
        initial_player = self.game.current_player

        move_successful = self.game.move_piece(start_pos, end_pos)
        
        self.assertFalse(move_successful)
        self.assertEqual(self.game.board, initial_board_state)
        self.assertEqual(self.game.current_player, initial_player)

    def test_move_piece_to_friendly_occupied_square(self):
        """Test moving to a square occupied by a friendly piece."""
        # White Knight g1 to e2 (occupied by white pawn)
        start_pos = ChessGame.algebraic_to_coords("g1") # (7,6) White Knight
        end_pos = ChessGame.algebraic_to_coords("e2")   # (6,4) White Pawn
        initial_board_state = [row[:] for row in self.game.board]
        initial_player = self.game.current_player
        self.assertIsNotNone(self.game.get_piece_at(start_pos))
        self.assertIsNotNone(self.game.get_piece_at(end_pos))
        self.assertEqual(self.game.get_piece_at(start_pos).color, WHITE)
        self.assertEqual(self.game.get_piece_at(end_pos).color, WHITE)


        move_successful = self.game.move_piece(start_pos, end_pos)
        
        self.assertFalse(move_successful)
        self.assertEqual(self.game.board, initial_board_state)
        self.assertEqual(self.game.current_player, initial_player)

    def test_pawn_moves(self):
        """Test various pawn moves (valid and invalid)."""
        # White pawn e2 to e4 (2 steps initial)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4")))
        self.assertEqual(self.game.board[4][4], (PAWN_T, WHITE))
        self.assertEqual(self.game.current_player, BLACK)

        # Black pawn d7 to d5 (2 steps initial)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("d7"), ChessGame.algebraic_to_coords("d5")))
        self.assertEqual(self.game.board[3][3], (PAWN_T, BLACK))
        self.assertEqual(self.game.current_player, WHITE)

        # White pawn e4 to e5 (1 step)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e4"), ChessGame.algebraic_to_coords("e5")))
        self.assertEqual(self.game.board[3][4], (PAWN_T, WHITE))

        # Black pawn d5 to d4 (1 step)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("d5"), ChessGame.algebraic_to_coords("d4")))
        self.assertEqual(self.game.board[4][3], (PAWN_T, BLACK))
        
        # White pawn e5 to d6 (capture black pawn at d6 if it were there - test valid diagonal move to empty for now)
        # First, place a black pawn for capture
        self.game.board[2][3] = (PAWN_T, BLACK) # Place black pawn at d6 for capture by white e5
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e5"), ChessGame.algebraic_to_coords("d6")))
        self.assertEqual(self.game.board[2][3], (PAWN_T, WHITE)) # White pawn captures
        
        # Invalid: White pawn a2 to a5 (3 steps)
        self.game.current_player = WHITE # Reset turn for this specific test scenario
        self.game.board[6][0] = (PAWN_T, WHITE) # Ensure pawn is at a2
        self.game.board[5][0] = EMPTY
        self.game.board[4][0] = EMPTY
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("a2"), ChessGame.algebraic_to_coords("a5")))

        # Invalid: White pawn a2 to a1 (backward)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("a2"), ChessGame.algebraic_to_coords("a1")))

        # Invalid: Pawn e2 to d2 (sideways)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("d2")))

        # Invalid: Pawn e2 to e3 (1 step) then e3 to e5 (2 steps - not allowed after first move)
        self.game = ChessGame() # Reset board
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e3"))) # White e2-e3
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e7"), ChessGame.algebraic_to_coords("e6"))) # Black e7-e6
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e3"), ChessGame.algebraic_to_coords("e5"))) # White e3-e5 (invalid)

        # Invalid: Pawn e2 to e4 (blocked by own piece at e3)
        self.game = ChessGame() # Reset board
        self.game.board[5][4] = (PAWN_T, WHITE) # Put a white piece at e3
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4")))

        # Invalid: Pawn e2 to e3 (blocked by opponent piece at e3)
        self.game = ChessGame() # Reset board
        self.game.board[5][4] = (PAWN_T, BLACK) # Put a black piece at e3
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e3")))

        # Invalid: Pawn e2 to d3 (diagonal capture to empty square)
        self.game = ChessGame()
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("d3")))


    def test_rook_moves(self):
        """Test rook moves."""
        # Set up a scenario: White Rook at a1, Black pawn at a5, White pawn at e1
        self.game.board = [[EMPTY for _ in range(8)] for _ in range(8)] # Clear board
        self.game.board[7][0] = (ROOK_T, WHITE) # White Rook at a1 (7,0)
        self.game.board[3][0] = (PAWN_T, BLACK) # Black Pawn at a5 (3,0)
        self.game.board[7][4] = (PAWN_T, WHITE) # White Pawn at e1 (7,4)
        self.game.current_player = WHITE

        # Valid: Rook a1 to a4 (vertical)
        self.assertTrue(self.game.move_piece((7,0), (4,0))) # a1 to a4
        self.assertEqual(self.game.board[4][0], (ROOK_T, WHITE))
        self.assertEqual(self.game.board[7][0], EMPTY)
        self.game.current_player = WHITE # Set back for next test

        # Valid: Rook a4 to d4 (horizontal)
        self.assertTrue(self.game.move_piece((4,0), (4,3))) # a4 to d4
        self.assertEqual(self.game.board[4][3], (ROOK_T, WHITE))
        self.game.current_player = WHITE

        # Valid: Rook d4 captures black pawn at a4 (originally a5, now a4 after rook moved there and back)
        self.game.board[4][0] = (PAWN_T, BLACK) # Place black pawn at a4 for capture
        self.assertTrue(self.game.move_piece((4,3), (4,0))) # d4 to a4 (capture)
        self.assertEqual(self.game.board[4][0], (ROOK_T, WHITE))
        self.game.current_player = WHITE
        
        # Invalid: Rook a1 to a6 (moving through black pawn at a5)
        self.game.board[7][0] = (ROOK_T, WHITE) # Reset rook to a1
        self.game.board[3][0] = (PAWN_T, BLACK) # Blocker at a5 (3,0)
        self.assertFalse(self.game.move_piece((7,0), (2,0))) # a1 to a6

        # Invalid: Rook a1 to e1 (moving to square occupied by friendly white pawn)
        self.game.board[7][0] = (ROOK_T, WHITE)
        self.game.board[7][4] = (PAWN_T, WHITE) # Friendly pawn at e1
        self.assertFalse(self.game.move_piece((7,0), (7,4)))

    def test_knight_moves(self):
        """Test knight moves."""
        # White Knight g1 to f3
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("g1"), ChessGame.algebraic_to_coords("f3")))
        self.assertEqual(self.game.board[5][5], (KNIGHT_T, WHITE))
        self.assertEqual(self.game.current_player, BLACK)

        # Black Knight b8 to c6
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("b8"), ChessGame.algebraic_to_coords("c6")))
        self.assertEqual(self.game.board[2][2], (KNIGHT_T, BLACK))
        self.assertEqual(self.game.current_player, WHITE)

        # White Knight f3 to e5 (jumping over pawn at e4 if it were there - knights jump)
        self.game.board[4][4] = (PAWN_T, WHITE) # Place a pawn at e4 to test jumping
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("f3"), ChessGame.algebraic_to_coords("e5")))
        self.assertEqual(self.game.board[3][4], (KNIGHT_T, WHITE))

        # Invalid: Knight g1 to g3 (not L-shape)
        self.game = ChessGame() # Reset
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("g1"), ChessGame.algebraic_to_coords("g3")))

        # Invalid: Knight g1 to e2 (occupied by friendly pawn)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("g1"), ChessGame.algebraic_to_coords("e2")))


    def test_bishop_moves(self):
        """Test bishop moves."""
        # Setup: White e2-e4, Black d7-d5, White Bishop f1 to c4
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4"))) # White e4
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("d7"), ChessGame.algebraic_to_coords("d5"))) # Black d5
        
        # Valid: Bishop f1 to c4
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("f1"), ChessGame.algebraic_to_coords("c4")))
        self.assertEqual(self.game.board[4][2], (BISHOP_T, WHITE))
        self.assertEqual(self.game.current_player, BLACK)

        # Black Bishop c8 to f5
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("c8"), ChessGame.algebraic_to_coords("f5")))
        self.assertEqual(self.game.board[3][5], (BISHOP_T, BLACK))

        # Invalid: Bishop c4 to e5 (blocked by white pawn at e4)
        # (c4 is (4,2), e4 is (4,4) - Bishop is on c4, pawn on e4, trying to move to e6 (2,4))
        # Actually, pawn e4 is (4,4). Bishop c4 is (4,2). Path to e6 (2,4) is not blocked by e4.
        # Let's try Bishop c4 to a6, blocked by b5 if pawn there.
        # For simplicity, let's test Bishop f1 to d3 (blocked by e2 pawn)
        self.game = ChessGame() # Reset
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("f1"), ChessGame.algebraic_to_coords("d3")))

        # Invalid: Bishop f1 to f3 (not diagonal)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("f1"), ChessGame.algebraic_to_coords("f3")))
        
        # Invalid: Bishop f1 to h3 (occupied by friendly pawn g2)
        self.game = ChessGame() # Reset
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("g2"), ChessGame.algebraic_to_coords("g3"))) # W: g3
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("a7"), ChessGame.algebraic_to_coords("a6"))) # B: a6
        #Now try to move f1 to h3, which is not possible as g2 is empty.
        #Try f1 to d3, e2 is on the way
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("f1"), ChessGame.algebraic_to_coords("d3")))


    def test_queen_moves(self):
        """Test queen moves."""
        # Setup: White e2-e4, Black e7-e5, White Queen d1 to h5
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4")))
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e7"), ChessGame.algebraic_to_coords("e5")))
        
        # Valid: Queen d1 to h5 (diagonal)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("d1"), ChessGame.algebraic_to_coords("h5")))
        self.assertEqual(self.game.board[3][7], (QUEEN_T, WHITE))
        self.assertEqual(self.game.current_player, BLACK)

        # Black Queen d8 to e7 (diagonal, e7 is now empty after pawn e7-e5)
        # d8 is (0,3), e7 is (1,4)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("d8"), ChessGame.algebraic_to_coords("e7")))
        self.assertEqual(self.game.board[1][4], (QUEEN_T, BLACK)) # Queen at e7

        # Valid: White Queen h5 to f7 (capture pawn if it was there)
        # Current player is White after Black's Queen move. White Queen is at h5 (3,7)
        self.game.board[1][5] = (PAWN_T, BLACK) # Black pawn at f7 for capture
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("h5"), ChessGame.algebraic_to_coords("f7")))
        self.assertEqual(self.game.board[1][5], (QUEEN_T, WHITE))

        # Invalid: Queen d1 to d5 (blocked by d2 pawn)
        self.game = ChessGame() # Reset
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("d1"), ChessGame.algebraic_to_coords("d5")))

        # Invalid: Queen d1 to c3 (like a knight)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("d1"), ChessGame.algebraic_to_coords("c3")))

    def test_king_moves(self):
        """Test king moves."""
        # Setup: e2-e4 to free king
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4")))
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("a7"), ChessGame.algebraic_to_coords("a6"))) # Dummy black move

        # Valid: King e1 to e2
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e1"), ChessGame.algebraic_to_coords("e2")))
        self.assertEqual(self.game.board[6][4], (KING_T, WHITE))
        self.assertEqual(self.game.current_player, BLACK)

        # Dummy black move
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("a6"), ChessGame.algebraic_to_coords("a5")))

        # Valid: King e2 to f3 (diagonal)
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("f3")))
        self.assertEqual(self.game.board[5][5], (KING_T, WHITE))

        # Invalid: King e1 to e3 (2 steps)
        self.game = ChessGame() # Reset
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("e2"), ChessGame.algebraic_to_coords("e4"))) # Clear e2
        self.assertTrue(self.game.move_piece(ChessGame.algebraic_to_coords("a7"), ChessGame.algebraic_to_coords("a6"))) # Dummy black move
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e1"), ChessGame.algebraic_to_coords("e3")))

        # Invalid: King e1 to d1 (occupied by friendly Queen)
        self.assertFalse(self.game.move_piece(ChessGame.algebraic_to_coords("e1"), ChessGame.algebraic_to_coords("d1")))

if __name__ == '__main__':
    unittest.main()
