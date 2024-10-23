import pygame
from chess_game import play_game_1v1, play_game_vs_ai
from themes import change_theme  # If you have a theme system

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Chess Game")

    # Add text or buttons for options here
    # Then code for mouse clicks to select options
    # Call functions like play_game_vs_ai(), play_game_1v1()

    pygame.quit()

if __name__ == "__main__":
    main_menu()
