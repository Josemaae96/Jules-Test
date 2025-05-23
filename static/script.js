let selectedSquareElement = null; // DOM element of the selected square
let validMoveSquares = []; // Array of [row, col] for currently shown valid moves

// Helper to get the DOM element for a square
function getSquareElement(row, col) {
    return document.querySelector(`.chess-square[data-row="${row}"][data-col="${col}"]`);
}

function clearSquareHighlights() {
    if (selectedSquareElement) {
        selectedSquareElement.classList.remove('selected-square');
        selectedSquareElement = null;
    }
    validMoveSquares.forEach(([r, c]) => {
        const el = getSquareElement(r, c);
        if (el) {
            el.classList.remove('valid-move-square');
            // If using dots, remove them here too
            const dot = el.querySelector('.move-dot');
            if (dot) {
                el.removeChild(dot);
            }
        }
    });
    validMoveSquares = [];
}

function highlightValidMoves(moves) {
    // moves is an array of [row, col] tuples
    moves.forEach(([r, c]) => {
        const el = getSquareElement(r, c);
        if (el) {
            // el.classList.add('valid-move-square'); // Using dots instead of bg change for moves
            const dot = document.createElement('div');
            dot.classList.add('move-dot');
            el.appendChild(dot); 
            validMoveSquares.push([r, c]); 
        }
    });
}

function updateBoard(boardState) {
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const squareEl = getSquareElement(r, c);
            if (squareEl) {
                squareEl.textContent = boardState[r][c] || ""; // Ensure empty string for empty cells
            }
        }
    }
}

function updateTurnIndicator(currentPlayer) {
    const turnIndicator = document.getElementById('turn-indicator');
    if (turnIndicator) {
        turnIndicator.textContent = `Player's Turn: ${currentPlayer}`;
    }
}

function updateGameMessages(message) {
    const gameMessagesEl = document.getElementById('game-messages');
    if (gameMessagesEl) {
        gameMessagesEl.textContent = `Game Messages: ${message}`;
    }
}

function promptForPromotion(promotionSquare, pieceColor) {
    // Remove existing promotion UI if any (should not happen if logic is correct)
    // Remove existing promotion UI if any
    const existingOverlay = document.getElementById('promotion-dialog-overlay');
    if (existingOverlay) {
        document.body.removeChild(existingOverlay);
    }

    // Create overlay div
    const overlayDiv = document.createElement('div');
    overlayDiv.id = 'promotion-dialog-overlay'; 
    // Styles for overlay (like background, position) are handled by CSS

    // Create dialog content div
    const promotionDialogContent = document.createElement('div');
    promotionDialogContent.id = 'promotion-dialog'; // Styled by CSS

    // Construct algebraic notation for display
    const file = String.fromCharCode('a'.charCodeAt(0) + parseInt(promotionSquare.col));
    const rank = 8 - parseInt(promotionSquare.row);
    const algebraicPos = file + rank;

    promotionDialogContent.innerHTML = `<h3>Pawn Promotion at ${algebraicPos}</h3>
                                      <p>Promote to:</p>
                                      <button data-choice="Q">Queen</button>
                                      <button data-choice="R">Rook</button>
                                      <button data-choice="B">Bishop</button>
                                      <button data-choice="N">Knight</button>`;
    
    overlayDiv.appendChild(promotionDialogContent); // Add dialog content to overlay
    document.body.appendChild(overlayDiv); // Add overlay to body

    // Add event listener to the overlay, specifically for buttons within the dialog
    overlayDiv.addEventListener('click', async (event) => {
        // Check if the click was on a button within the dialog content
        if (event.target.tagName === 'BUTTON' && promotionDialogContent.contains(event.target)) {
            const choice = event.target.dataset.choice;
            document.body.removeChild(overlayDiv); // Remove the entire overlay (which contains the dialog)

            try {
                const response = await fetch(`/promote_pawn/${choice}`, { method: 'POST' });
                if (response.ok) {
                    const data = await response.json();
                    console.log('Promotion server response:', data);
                    handleServerResponse(data); // Handle response after promotion
                } else {
                    console.error('Error during promotion:', response.status, await response.text());
                    updateGameMessages(`Error during promotion: ${await response.text()}`);
                    // Might need to refresh board or show error more formally
                }
            } catch (error) {
                console.error('Network error during promotion:', error);
                updateGameMessages(`Network error during promotion.`);
            }
        }
    });
}


function handleServerResponse(data) {
    console.log("Handling server response:", data);
    clearSquareHighlights(); // Always clear previous highlights first

    if (data.board_state) {
        updateBoard(data.board_state);
    }
    if (data.current_player) {
        updateTurnIndicator(data.current_player);
    }
    if (data.message) {
        updateGameMessages(data.message);
    }

    if (data.status === 'piece_selected') {
        if (data.selected_square) {
            const { row, col } = data.selected_square;
            selectedSquareElement = getSquareElement(row, col);
            if (selectedSquareElement) {
                selectedSquareElement.classList.add('selected-square');
            }
        }
        if (data.valid_moves) {
            highlightValidMoves(data.valid_moves);
        }
    } else if (data.status === 'move_successful' || data.status === 'invalid_move' || data.status === 'deselected' || data.status === 'invalid_selection' || data.status === 'promotion_complete') {
        // Highlights already cleared. selectedSquareElement is null. validMoveSquares is empty.
        // Nothing specific to do for highlights here. Game state messages are handled above.
        if (data.is_checkmate) {
            // Optionally disable further clicks or display a more prominent game over message
            console.log("Game Over: Checkmate!");
            // chessboard.removeEventListener('click', ...); // More complex to remove specific listener
        }
    } else if (data.status === 'promotion_required') {
        if (data.promotion_square && data.piece_color) {
            promptForPromotion(data.promotion_square, data.piece_color);
        }
    } else if (data.status === 'error') {
        // Error message already displayed by updateGameMessages
        console.error("Server returned error:", data.message);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const chessboard = document.getElementById('chessboard');
    if (chessboard) {
        chessboard.addEventListener('click', async (event) => {
            const squareElement = event.target.closest('.chess-square');
            if (squareElement) {
                const row = squareElement.dataset.row;
                const col = squareElement.dataset.col;
                // console.log(`Clicked square: (${row}, ${col})`); // Moved logging into handleServerResponse or server log

                // If a promotion dialog is active, don't process board clicks
                if (document.getElementById('promotion-dialog-overlay')) { // Check for overlay
                    console.log("Promotion dialog active, ignoring board click.");
                    return;
                }

                try {
                    const response = await fetch(`/select_square/${row}/${col}`);
                    if (response.ok) {
                        const data = await response.json(); 
                        // console.log('Raw server response:', data); // Logging now inside handleServerResponse
                        handleServerResponse(data); 
                    } else {
                        console.error('Error from server:', response.status, await response.text());
                        updateGameMessages(`Error from server: ${response.status}`);
                    }
                } catch (error) {
                    console.error('Network error:', error);
                    updateGameMessages(`Network error.`);
                }
            }
        });
    }
});
