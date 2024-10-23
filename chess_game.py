import pygame
import chess  # This imports the python-chess library
import sys
import random
import time  
import os
from stockfish import Stockfish

# Use the correct path for the Stockfish executable
path = r"C:\Users\Admin\Downloads\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe"

# Check if the path exists
if os.path.exists(path):
    print("Stockfish executable found.")
    stockfish = Stockfish(path)
else:
    print("Stockfish executable not found.")



pygame.init()
pygame.mixer.init()

# Define the window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SQUARE_SIZE = 480 // 8

# Colors
button_color = (134, 169, 75)
background_color = (42, 41, 39)  # #2a2927 color for the background around the board
highlight_color = (0, 0, 0, 100)  # Semi-transparent black for highlighting moves

# Load chess sounds
move_sound = pygame.mixer.Sound('assets/sound/move-self.wav')
capture_sound = pygame.mixer.Sound('assets/sound/capture.wav')
checkmate_sound = pygame.mixer.Sound('assets/sound/notify.wav')

# Load the board image and scale it
classic_board = pygame.image.load('assets/boards/Wood.png')
scaled_board = pygame.transform.scale(classic_board, (480, 480))

# Load chess piece images
piece_images = {
    'P': pygame.image.load('assets/pieces/standardboard.1d6f9426__12_-removebg-preview.png'),
    'R': pygame.image.load('assets/pieces/standardboard.1d6f9426__7_-removebg-preview.png'),
    'N': pygame.image.load('assets/pieces/standardboard.1d6f9426__8_-removebg-preview.png'),
    'B': pygame.image.load('assets/pieces/standardboard.1d6f9426__9_-removebg-preview.png'),
    'Q': pygame.image.load('assets/pieces/standardboard.1d6f9426__10_-removebg-preview.png'),
    'K': pygame.image.load('assets/pieces/standardboard.1d6f9426__11_-removebg-preview.png'),
    'p': pygame.image.load('assets/pieces/standardboard.1d6f9426__6_-removebg-preview.png'),
    'r': pygame.image.load('assets/pieces/standardboard.1d6f9426__1_-removebg-preview.png'),
    'n': pygame.image.load('assets/pieces/standardboard.1d6f9426__2_-removebg-preview.png'),
    'b': pygame.image.load('assets/pieces/standardboard.1d6f9426__3_-removebg-preview.png'),
    'q': pygame.image.load('assets/pieces/standardboard.1d6f9426__4_-removebg-preview.png'),
    'k': pygame.image.load('assets/pieces/standardboard.1d6f9426__5_-removebg-preview.png'),
}

# Scale the piece images
for piece in piece_images:
    piece_images[piece] = pygame.transform.scale(piece_images[piece], (40, 50))

# Undo and Redo button properties
undo_button_rect = pygame.Rect(600, 100, 100, 50)
redo_button_rect = pygame.Rect(600, 170, 100, 50)

# Main menu button
start_button_rect = pygame.Rect((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 100) // 2, 200, 50)  # Centered start button

# Game mode selection buttons
button_rect_1v1 = pygame.Rect((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 100) // 2 - 20, 200, 50)  # Centered button for 1v1
button_rect_ai = pygame.Rect((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 100) // 2 + 40, 200, 50)  # Centered button for AI
add_button_rect = pygame.Rect((WINDOW_WIDTH - 200) // 2, (WINDOW_HEIGHT - 100) // 2 + 100, 200, 50)  # Centered button for Add

def select_ai_difficulty():
    """Display options for AI difficulty selection."""
    difficulty_options = ['Easy', 'Medium', 'Hard']
    selected_difficulty = None

    # Create a small window for difficulty selection
    difficulty_window = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Select AI Difficulty")

    while selected_difficulty is None:
        difficulty_window.fill((255, 255, 255))  # White background
        font = pygame.font.Font(None, 36)

        # Display options
        for i, option in enumerate(difficulty_options):
            text = font.render(option, True, (0, 0, 0))
            difficulty_window.blit(text, (50, 50 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Cancel selection
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Easy mode
                    selected_difficulty = 'Easy'
                elif event.key == pygame.K_2:  # Medium mode
                    selected_difficulty = 'Medium'
                elif event.key == pygame.K_3:  # Hard mode
                    selected_difficulty = 'Hard'

    pygame.display.quit()  # Close difficulty window
    return selected_difficulty

def select_ai_level():
    """Display AI level options and allow the user to select one."""
    font = pygame.font.Font(None, 36)
    levels = list(range(1, 21))  # Levels 1 to 20
    level_rects = []

    for i, level in enumerate(levels):
        rect = pygame.Rect(550, 100 + i * 30, 200, 30)
        level_rects.append(rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(level_rects):
                    if rect.collidepoint(event.pos):
                        return levels[i]

        screen.fill((0, 0, 0))
        draw_board(screen)
        draw_pieces(screen, board)
        draw_buttons(screen)

        for i, rect in enumerate(level_rects):
            pygame.draw.rect(screen, (128, 128, 128), rect, border_radius=10)
            text_surface = font.render(f"AI Level {levels[i]}", True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=rect.center))

        pygame.display.flip()

def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def show_checkmate_popup(screen, winner):
    """Display a popup when checkmate occurs."""
    font = pygame.font.Font(None, 50)
    checkmate_text = font.render(f"Checkmate! {winner} wins!", True, (255, 0, 0))
    screen.blit(checkmate_text, ((WINDOW_WIDTH - checkmate_text.get_width()) // 2, WINDOW_HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(3000)  # Display popup for 3 seconds

def show_main_menu():
    """Display the main menu with a Start button."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game Interface")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if start_button_rect.collidepoint(event.pos):
                        show_game_mode_selection()  # Show game mode selection

        # Fill background with the new color
        screen.fill(background_color)

        # Draw Start button
        draw_rounded_rect(screen, button_color, start_button_rect, 20)

        # Button text
        font = pygame.font.Font(None, 36)
        text_surface_start = font.render("Start", True, (255, 255, 255))
        text_rect_start = text_surface_start.get_rect(center=start_button_rect.center)
        screen.blit(text_surface_start, text_rect_start)

        # Update the display
        pygame.display.flip()

    pygame.quit()

def show_game_mode_selection():
    """Display the game mode selection menu."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Select Game Mode")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if button_rect_1v1.collidepoint(event.pos):
                        play_game_1v1()  # Start game vs 1v1
                    elif button_rect_ai.collidepoint(event.pos):
                        play_game_vs_ai()  # Start game vs AI
                    elif add_button_rect.collidepoint(event.pos):
                        print("Add Option Selected")  # Handle Add option here

        # Fill background with the new color
        screen.fill(background_color)

        # Draw buttons for game mode selection
        draw_rounded_rect(screen, button_color, button_rect_1v1, 20)
        draw_rounded_rect(screen, button_color, button_rect_ai, 20)
        draw_rounded_rect(screen, button_color, add_button_rect, 20)

        # Button text
        font = pygame.font.Font(None, 36)
        text_surface_1v1 = font.render("1v1", True, (255, 255, 255))
        text_surface_ai = font.render("Vs AI", True, (255, 255, 255))
        text_surface_add = font.render("Add", True, (255, 255, 255))

        text_rect_1v1 = text_surface_1v1.get_rect(center=button_rect_1v1.center)
        text_rect_ai = text_surface_ai.get_rect(center=button_rect_ai.center)
        text_rect_add = text_surface_add.get_rect(center=add_button_rect.center)

        screen.blit(text_surface_1v1, text_rect_1v1)
        screen.blit(text_surface_ai, text_rect_ai)
        screen.blit(text_surface_add, text_rect_add)

        # Update the display
        pygame.display.flip()

    pygame.quit()

def draw_board(screen):
    # Draw background
    screen.fill(background_color)
    # Draw chess board in the center
    screen.blit(scaled_board, (50, 50))

def draw_pieces(screen, board):
    for rank in range(8):
        for file in range(8):
            piece = board.piece_at(chess.square(file, 7 - rank))
            if piece:
                piece_image = piece_images[piece.symbol()]
                piece_x = 50 + file * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
                piece_y = 50 + rank * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_height()) // 2
                screen.blit(piece_image, (piece_x, piece_y))

def draw_buttons(screen):
    """Draw undo and redo buttons."""
    draw_rounded_rect(screen, button_color, undo_button_rect, 20)
    draw_rounded_rect(screen, button_color, redo_button_rect, 20)

    font = pygame.font.Font(None, 36)
    text_surface_undo = font.render("Undo", True, (255, 255, 255))
    text_surface_redo = font.render("Redo", True, (255, 255, 255))

    text_rect_undo = text_surface_undo.get_rect(center=undo_button_rect.center)
    text_rect_redo = text_surface_redo.get_rect(center=redo_button_rect.center)

    screen.blit(text_surface_undo, text_rect_undo)
    screen.blit(text_surface_redo, text_rect_redo)

def highlight_possible_moves(screen, board, selected_square):
    """Highlight possible moves for the selected piece."""
    if selected_square is not None:
        possible_moves = list(board.legal_moves)
        possible_moves = [move for move in possible_moves if move.from_square == selected_square]
        for move in possible_moves:
            square_x = 50 + chess.square_file(move.to_square) * SQUARE_SIZE
            square_y = 50 + (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE
            # Draw a semi-transparent black circle
            circle_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, highlight_color, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 30)
            screen.blit(circle_surface, (square_x, square_y))

def draw_possible_moves(screen, board, selected_square):
    """Draw circles on the board to show possible moves for the selected piece."""
    if selected_square is None:
        return

    possible_moves = list(board.legal_moves)

    # Go through all possible moves and highlight the destination squares for the selected piece
    for move in possible_moves:
        if move.from_square == chess.square(selected_square[0], selected_square[1]):
            to_square = move.to_square
            file, rank = chess.square_file(to_square), chess.square_rank(to_square)

            # Calculate the position of the square on the screen
            x = file * SQUARE_SIZE + 50  # Adjust based on your board's positioning
            y = (7 - rank) * SQUARE_SIZE + 50

            # Draw a circle on the possible move location
            pygame.draw.circle(screen, (39, 39, 39), (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 15)
            
def draw_navigation_buttons(screen):
    """Draw back and forward buttons."""
    font = pygame.font.Font(None, 36)
    back_button = font.render("Back", True, (0, 0, 0))
    forward_button = font.render("Forward", True, (0, 0, 0))

    # Draw buttons at specific positions
    screen.blit(back_button, (10, 10))
    screen.blit(forward_button, (100, 10))
    
def play_game_1v1():
    """Main loop for the 1v1 game."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game")

    # Initialize board
    board = chess.Board()
    move_stack = []  # Store moves for undo/redo
    running = True
    selected_piece = None
    selected_square = None

    def promote_pawn():
        """Display promotion options and allow the user to select a piece."""
        font = pygame.font.Font(None, 36)
        options = ['q', 'r', 'b', 'n']  # Queen, Rook, Bishop, Knight
        texts = ['Queen', 'Rook', 'Bishop', 'Knight']
        option_rects = []

        # Create option rectangles for each promotion choice
        for i, text in enumerate(texts):
            rect = pygame.Rect(550, 100 + i * 50, 200, 40)
            option_rects.append(rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(event.pos):
                            return options[i]  # Return the selected piece symbol

            # Draw promotion options
            screen.fill((0, 0, 0))  # Background color
            draw_board(screen)
            draw_pieces(screen, board)
            draw_buttons(screen)

            for i, rect in enumerate(option_rects):
                pygame.draw.rect(screen, (128, 128, 128), rect, border_radius=10)
                text_surface = font.render(texts[i], True, (255, 255, 255))
                screen.blit(text_surface, text_surface.get_rect(center=rect.center))

            pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    pos = event.pos
                    x, y = pos[0] - 50, pos[1] - 50
                    file, rank = x // SQUARE_SIZE, 7 - (y // SQUARE_SIZE)

                    if selected_piece:  # If a piece is selected, attempt to move it
                        move = chess.Move(chess.square(selected_square[0], selected_square[1]),
                                          chess.square(file, rank))

                        # Check for promotion: if the piece is a pawn and it reaches the last rank
                        if board.piece_at(chess.square(selected_square[0], selected_square[1])).symbol().lower() == 'p' and \
                                (rank == 0 or rank == 7):
                            # Call promote_pawn function to get player's choice
                            promotion_choice = promote_pawn()
                            move = chess.Move(chess.square(selected_square[0], selected_square[1]),
                                              chess.square(file, rank), promotion=chess.Piece.from_symbol(promotion_choice).piece_type)

                        if move in board.legal_moves:
                            # Play capture or move sound
                            if board.is_capture(move):
                                capture_sound.play()
                            else:
                                move_sound.play()

                            # Execute the move
                            board.push(move)
                            move_stack.append(move)

                            # Reset selected piece and square
                            selected_piece = None
                            selected_square = None
                        else:
                            selected_piece = None
                            selected_square = None
                    else:  # Select a piece
                        selected_piece = board.piece_at(chess.square(file, rank))
                        if selected_piece:
                            selected_square = (file, rank)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:  # Undo move
                    if move_stack:
                        board.pop()
                        move_stack.pop()
                elif event.key == pygame.K_r:  # Redo move
                    if move_stack:
                        last_move = move_stack[-1]
                        board.push(last_move)

        draw_board(screen)
        draw_pieces(screen, board)
        draw_buttons(screen)

        # Show possible moves for selected piece
        draw_possible_moves(screen, board, selected_square)

        # Check for checkmate and play checkmate sound
        if board.is_checkmate():
            winner = "White" if board.turn else "Black"
            checkmate_sound.play()  # Play checkmate sound
            show_checkmate_popup(screen, winner)
            running = False  # Exit the game loop after displaying checkmate

        pygame.display.flip()

    pygame.quit()
    
def get_ai_move(board):
    stockfish.set_fen_position(board.fen())  # Set the current board position
    ai_move = stockfish.get_best_move()  # Get the best move from Stockfish
    return ai_move
# Get the best move from Stockfish


def show_pawn_promotion_popup(screen, color):
    """Display a popup for pawn promotion."""
    font = pygame.font.Font(None, 36)
    promotion_text = font.render(f"Promote to:", True, (255, 255, 255))
    screen.blit(promotion_text, ((WINDOW_WIDTH - promotion_text.get_width()) // 2, WINDOW_HEIGHT // 2 - 40))

    # Define promotion options
    options = ['Q', 'R', 'B', 'N']
    for i, piece in enumerate(options):
        option_text = font.render(piece, True, (255, 255, 255))
        screen.blit(option_text, ((WINDOW_WIDTH - option_text.get_width()) // 2, WINDOW_HEIGHT // 2 + i * 40))

    pygame.display.flip()

    # Wait for user input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = event.pos
                    for i, piece in enumerate(options):
                        if (WINDOW_WIDTH // 2 - 20 < mouse_x < WINDOW_WIDTH // 2 + 20) and \
                                (WINDOW_HEIGHT // 2 + i * 40 < mouse_y < WINDOW_HEIGHT // 2 + (i + 1) * 40):
                            return piece  # Return the selected piece for promotion

def promote_pawn(board, color):
    """Promotes a pawn to a selected piece."""
    # Create a surface for promotion options
    promotion_options = ['Queen ', 'Rook', 'B', 'N']  # Options for promotion to queen, rook, bishop, knight
    font = pygame.font.Font(None, 50)

    screen.fill(background_color)  # Fill background
    draw_board(screen)
    
    # Display promotion options
    for i, piece in enumerate(promotion_options):
        text_surface = font.render(f"Promote to {piece}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 50))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

    selected_piece = None
    while selected_piece is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, piece in enumerate(promotion_options):
                    if (WINDOW_WIDTH // 2 - 100 < mouse_x < WINDOW_WIDTH // 2 + 100) and \
                       (WINDOW_HEIGHT // 2 + i * 50 - 20 < mouse_y < WINDOW_HEIGHT // 2 + i * 50 + 20):
                        selected_piece = piece

    return selected_piece

from stockfish import Stockfish

# Use the correct path for the Stockfish executable
path = r"C:\Users\Admin\Downloads\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe"

# Check if the path exists
if os.path.exists(path):
    print("Stockfish executable found.")
    stockfish = Stockfish(path)
else:
    print("Stockfish executable not found.")

# Define the play_game_vs_ai function (make sure you have a proper chess board setup)
def handle_mouse_click(event, board, selected_square):
    if event.button == 1:  # Left mouse button
        pos = event.pos
        x, y = pos[0] - 50, pos[1] - 50
        file, rank = x // SQUARE_SIZE, 7 - (y // SQUARE_SIZE)

        # Your existing logic for piece selection and movement goes here...

def play_game_vs_ai():
    """Main loop for the game vs AI."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game vs AI")

    # Initialize board
    board = chess.Board()
    move_stack = []  # Store all moves
    history_index = -1  # Track the current position in history
    running = True
    selected_piece = None
    selected_square = None
    ai_turn = False  # Track if it's the AI's turn

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    pos = event.pos
                    x, y = pos[0] - 50, pos[1] - 50
                    file, rank = x // SQUARE_SIZE, 7 - (y // SQUARE_SIZE)

                    if selected_piece:  # If a piece is selected, attempt to move it
                        move = chess.Move(chess.square(selected_square[0], selected_square[1]),
                                          chess.square(file, rank))

                        if move in board.legal_moves:
                            # Execute the move
                            board.push(move)
                            move_stack.append(move)  # Add to move stack
                            history_index += 1  # Update history index

                            # Switch to AI turn
                            ai_turn = True

                            # Reset selected piece and square
                            selected_piece = None
                            selected_square = None
                        else:
                            selected_piece = None
                            selected_square = None
                    else:  # Select a piece
                        selected_piece = board.piece_at(chess.square(file, rank))
                        if selected_piece and (board.turn == (selected_piece.color == chess.WHITE)):  # Check if it's the correct turn
                            selected_square = (file, rank)

                # Navigation buttons
                if event.button == 1:  # Left mouse button click for navigation
                    # Back Button
                    if 10 <= pos[0] <= 110 and 10 <= pos[1] <= 50:
                        if history_index > 0:
                            history_index -= 1  # Move back in history
                            board.pop()  # Undo the last move to show the previous state
                            board.set_fen(move_stack[history_index].fen())  # Set board to previous state

                    # Forward Button
                    elif 100 <= pos[0] <= 200 and 10 <= pos[1] <= 50:
                        if history_index < len(move_stack) - 1:
                            history_index += 1  # Move forward in history
                            board.pop()  # Undo the last move to show the next state
                            board.set_fen(move_stack[history_index].fen())  # Set board to next state

            # AI's turn to move
            if ai_turn and board.turn == chess.BLACK:  # Assuming AI is playing as black
                pygame.time.wait(1000)  # Wait before making the move
                ai_move = get_ai_move(board)  # Get the best move from Stockfish
                board.push(chess.Move.from_uci(ai_move))  # Play the AI move
                move_stack.append(board.copy())  # Store the current board state
                history_index += 1  # Update history index
                ai_turn = False  # Switch back to player's turn

        draw_board(screen)
        draw_pieces(screen, board)
        draw_buttons(screen)
        draw_navigation_buttons(screen)  # Draw navigation buttons

        # Show possible moves for selected piece
        draw_possible_moves(screen, board, selected_square)

        # Check for checkmate and play checkmate sound
        if board.is_checkmate():
            winner = "White" if board.turn else "Black"
            checkmate_sound.play()  # Play checkmate sound
            show_checkmate_popup(screen, winner)
            running = False  # Exit the game loop after displaying checkmate

        pygame.display.flip()

    pygame.quit()  # Make sure to quit pygame properly when done

if __name__ == "__main__":
    show_main_menu()
