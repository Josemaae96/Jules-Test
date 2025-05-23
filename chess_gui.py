import tkinter as tk
from chess_game import ChessGame, WHITE, BLACK, EMPTY
from chess_game import PAWN_T, ROOK_T, KNIGHT_T, BISHOP_T, QUEEN_T, KING_T # Piece types
# pieces.py is implicitly imported via chess_game, but specific piece classes are not directly used in GUI yet

class ChessGui:
    def __init__(self, master):
        self.master = master
        master.title("Simple Chess GUI")
        # master.geometry("480x480") # Adjust as needed based on square_size

        self.game = ChessGame()

        self.square_size = 60
        self.board_frame = tk.Frame(master)
        self.board_frame.pack()

        self.colors = {
            "light_square": "#F0D9B5",
            "dark_square": "#B58863",
            "piece_white": "white",
            "piece_black": "black",
            "selected_square_bg": "#90EE90", # Light green for selected piece
            "valid_move_highlight_bg": "#ADD8E6", # Light blue for valid move
            "valid_move_dot_color": "#367EAA" # A darker blue for the dot
        }
        
        self.selected_piece_coords = None
        self.highlighted_move_info = [] # Stores (canvas, original_bg, optional_dot_id)

        # Unicode characters for pieces
        self.piece_unicode = {
            (PAWN_T, WHITE): "♙", (PAWN_T, BLACK): "♟",
            (ROOK_T, WHITE): "♖", (ROOK_T, BLACK): "♜",
            (KNIGHT_T, WHITE): "♘", (KNIGHT_T, BLACK): "♞",
            (BISHOP_T, WHITE): "♗", (BISHOP_T, BLACK): "♝",
            (QUEEN_T, WHITE): "♕", (QUEEN_T, BLACK): "♛",
            (KING_T, WHITE): "♔", (KING_T, BLACK): "♚",
            EMPTY: ""
        }
        # Fallback simple text representation if needed
        self.piece_text_fallback = {
            (PAWN_T, WHITE): "wP", (PAWN_T, BLACK): "bP",
            (ROOK_T, WHITE): "wR", (ROOK_T, BLACK): "bR",
            (KNIGHT_T, WHITE): "wN", (KNIGHT_T, BLACK): "bN",
            (BISHOP_T, WHITE): "wB", (BISHOP_T, BLACK): "bB",
            (QUEEN_T, WHITE): "wQ", (QUEEN_T, BLACK): "bQ",
            (KING_T, WHITE): "wK", (KING_T, BLACK): "bK",
            EMPTY: ""
        }


        self.squares_canvas = [[None for _ in range(8)] for _ in range(8)]

        for r in range(8):
            for c in range(8):
                color = self.colors["light_square"] if (r + c) % 2 == 0 else self.colors["dark_square"]
                canvas = tk.Canvas(self.board_frame, width=self.square_size, height=self.square_size, 
                                   bg=color, highlightthickness=0)
                canvas.grid(row=r, column=c)
                # Create a closure for the event handler
                canvas.bind("<Button-1>", lambda event, row=r, col=c: self.on_square_click(row, col))
                self.squares_canvas[r][c] = canvas
        
        self.draw_board()

    def clear_highlights(self):
        """Clears all highlights from the board."""
        for canvas, original_bg, dot_id in self.highlighted_move_info:
            canvas.configure(bg=original_bg)
            if dot_id:
                canvas.delete(dot_id)
        self.highlighted_move_info = []
        self.selected_piece_coords = None # Also clear selected piece reference

    def draw_board(self):
        # Clear existing highlights before redrawing board (e.g., after a move)
        # This ensures highlights don't persist incorrectly if draw_board is called externally
        # However, for typical click flow, clear_highlights is called explicitly.
        # If self.selected_piece_coords is None, it implies no active selection, so safe to clear.
        if self.selected_piece_coords is None :
             self.clear_highlights() # Clear previous highlights if any

        for r in range(8):
            for c in range(8):
                canvas = self.squares_canvas[r][c]
                # canvas.delete("piece") # Clear only the piece
                # We need to clear dots too if any, so let's manage tags better or clear all and redraw bg
                
                # Determine original background color
                original_bg = self.colors["light_square"] if (r + c) % 2 == 0 else self.colors["dark_square"]
                
                # If the square is currently selected, its bg is already changed.
                # If it was highlighted as a move, its bg is also changed.
                # We need to reset to original unless it's the *newly* selected one.
                
                # If not part of current highlights, ensure it has its original background
                is_currently_highlighted_as_move = False
                for h_canvas, _, _ in self.highlighted_move_info:
                    if h_canvas == canvas:
                        is_currently_highlighted_as_move = True
                        break
                
                if not is_currently_highlighted_as_move and (self.selected_piece_coords != (r,c)):
                     canvas.configure(bg=original_bg)

                canvas.delete("piece_text") # Clear previous piece text
                canvas.delete("move_dot")   # Clear previous move dots


                piece_data = self.game.board[r][c] 

                if piece_data != EMPTY:
                    piece_type, piece_color = piece_data
                    char = self.piece_unicode.get((piece_type, piece_color), "?") 
                    text_color = self.colors["piece_white"] if piece_color == WHITE else self.colors["piece_black"]
                    font_size = self.square_size // 2 
                    canvas.create_text(self.square_size // 2, self.square_size // 2, 
                                       text=char, font=("Arial", font_size), fill=text_color, tags="piece_text")

    def on_square_click(self, row, col):
        """Handles a click on a square."""
        clicked_coords = (row, col)
        # print(f"Clicked on square: {clicked_coords}, Algebraic: {self.game.coords_to_algebraic(clicked_coords)}")

        if self.selected_piece_coords is None:
            # Attempt to select a piece
            piece_on_square = self.game.board[row][col]
            if piece_on_square != EMPTY and piece_on_square[1] == self.game.current_player:
                self.selected_piece_coords = clicked_coords
                
                # Highlight selected square
                canvas = self.squares_canvas[row][col]
                original_bg = canvas.cget("bg") # Get current bg to restore later
                canvas.configure(bg=self.colors["selected_square_bg"])
                self.highlighted_move_info.append((canvas, original_bg, None)) # No dot for selected square itself

                # Get and highlight valid moves
                valid_moves = self.game.get_validated_moves_for_piece(clicked_coords)
                # print(f"Valid moves for {self.game.coords_to_algebraic(clicked_coords)} ({self.game.current_player}): {valid_moves}")

                for move_r, move_c in valid_moves:
                    move_canvas = self.squares_canvas[move_r][move_c]
                    original_move_bg = move_canvas.cget("bg")
                    
                    # Option 1: Change background of valid move squares
                    # move_canvas.configure(bg=self.colors["valid_move_highlight_bg"])
                    # self.highlighted_move_info.append((move_canvas, original_move_bg, None))

                    # Option 2: Draw a dot/circle on valid move squares
                    dot_radius = self.square_size // 8
                    dot_id = move_canvas.create_oval(
                        self.square_size // 2 - dot_radius, self.square_size // 2 - dot_radius,
                        self.square_size // 2 + dot_radius, self.square_size // 2 + dot_radius,
                        fill=self.colors["valid_move_dot_color"], outline="" , tags="move_dot"
                    )
                    # Store original bg to restore, and the dot_id to delete
                    self.highlighted_move_info.append((move_canvas, original_move_bg, dot_id)) 
            else:
                # Clicked on empty square or opponent's piece when no piece was selected
                self.clear_highlights() 
                # print("Clicked on empty or opponent's piece. No selection.")
        else:
            # A piece is already selected, try to make a move or re-select.
            start_pos = self.selected_piece_coords
            end_pos = clicked_coords

            # Get currently valid moves for the selected piece to check against
            # This is important because the game state might have changed if it were a multi-player setup,
            # but for single instance, this is mostly to confirm the click target is valid.
            current_valid_moves = self.game.get_validated_moves_for_piece(start_pos)

            if end_pos in current_valid_moves:
                # Attempt to make the move in the game logic
                move_result = self.game.move_piece(start_pos, end_pos)

                if isinstance(move_result, tuple) and move_result[0] == "PROMOTION":
                    # Handle pawn promotion
                    _, promotion_square, piece_color = move_result
                    # Don't clear highlights or redraw yet. Promotion dialog will handle finalization.
                    self.prompt_pawn_promotion(promotion_square, piece_color)
                    # self.selected_piece_coords remains until promotion choice is made
                elif move_result is True: # Standard successful move
                    self.clear_highlights() # Also sets self.selected_piece_coords = None
                    self.draw_board()
                    # Later: update status, check for check/checkmate for the new current player
                    print(f"Move successful. {self.game.current_player.capitalize()}'s turn.")
                    if self.game.is_in_check(self.game.current_player):
                        print(f"!!! {self.game.current_player.capitalize()} is in check !!!")
                        if self.game.is_checkmate(self.game.current_player):
                             winning_color = WHITE if self.game.current_player == BLACK else BLACK
                             print(f"Checkmate! {winning_color.capitalize()} wins!")
                             # Consider disabling further clicks or closing
                    
                else: # Move was invalid for some reason (e.g. self-check, though get_validated_moves should prevent this)
                    print(f"Move from {start_pos} to {end_pos} failed. Reason: {move_result if isinstance(move_result, str) else 'Unknown'}")
                    # Clear selection and highlights, allowing user to try again or select another piece
                    self.clear_highlights()
                    # Optionally, re-select the original piece if the click was on an invalid square for it
                    # self.on_square_click(start_pos[0], start_pos[1]) # This might be too much, just deselect.
            else:
                # Clicked on a square that is NOT a valid move for the selected piece.
                # This could be an empty square, opponent's piece (not a capture), or one of their own pieces.
                self.clear_highlights() # Deselect the current piece
                # Now, treat this click as a new attempt to select a piece (if it's a valid piece to select)
                self.on_square_click(row, col) # Recursive call to potentially select the newly clicked square
        
        # Ensure board is drawn if a selection was made or cleared without a move attempt
        # This is mostly for the case where a piece is selected and then deselected by clicking an invalid square.
        # If a move is made, draw_board is called above.
        # If selection changes, draw_board is implicitly handled by the flow.
        # The main draw is after a successful move or after promotion.

    def prompt_pawn_promotion(self, promotion_square, piece_color):
        dialog = tk.Toplevel(self.master)
        dialog.title("Pawn Promotion")
        dialog.transient(self.master) # Make it appear on top of the main window
        dialog.grab_set() # Make it modal - disable main window until choice is made
        dialog.geometry("200x150") # Simple size

        label = tk.Label(dialog, text=f"Promote pawn at {self.game.coords_to_algebraic(promotion_square)}:")
        label.pack(pady=10)

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=5)

        choices = {'Q': "Queen", 'R': "Rook", 'B': "Bishop", 'N': "Knight"}
        for char_code, name in choices.items():
            button = tk.Button(buttons_frame, text=name, 
                               command=lambda cc=char_code: self.handle_promotion_choice(promotion_square, piece_color, cc, dialog))
            button.pack(side=tk.LEFT, padx=5)
        
        # Ensure the dialog is destroyed if the user closes it via window manager
        # This might leave the game in an inconsistent state if no choice is made.
        # A more robust solution would handle this, e.g. default to Queen or prevent closing.
        # For now, we assume a choice will be made.
        # dialog.protocol("WM_DELETE_WINDOW", lambda: self.handle_promotion_choice(promotion_square, piece_color, 'Q', dialog)) # Default to Queen if closed

    def handle_promotion_choice(self, promotion_square, piece_color, chosen_piece_char, dialog):
        dialog.destroy() # Close the dialog first

        self.game.complete_pawn_promotion(promotion_square, piece_color, chosen_piece_char)
        
        self.clear_highlights() # Also sets self.selected_piece_coords = None
        self.draw_board()
        
        # Now the turn is fully complete, announce current player and check/checkmate status
        print(f"Promotion complete. {self.game.current_player.capitalize()}'s turn.")
        if self.game.is_in_check(self.game.current_player):
            print(f"!!! {self.game.current_player.capitalize()} is in check !!!")
            if self.game.is_checkmate(self.game.current_player):
                 winning_color = WHITE if self.game.current_player == BLACK else BLACK
                 print(f"Checkmate! {winning_color.capitalize()} wins!")
                 # Consider disabling further clicks or closing

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChessGui(root)
    root.mainloop()
