import numpy as np
import random
import pygame
import sys
import math
import pygame.gfxdraw

BLUE = (80, 50, 150)
BLACK = (150, 255, 255)
ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
            if all(board[r + 3 - i][c + i] == piece for i in range(4)):
                return True

def draw_board(board, screen, player_logo, ai_logo, background, game_rect, height):
    screen.blit(background, (0, 0))
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (game_rect.x + c * SQUARESIZE, game_rect.y + r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.gfxdraw.aacircle(screen, game_rect.x + int(c * SQUARESIZE + SQUARESIZE / 2), game_rect.y + int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2), RADIUS, BLACK)
            pygame.gfxdraw.filled_circle(screen, game_rect.x + int(c * SQUARESIZE + SQUARESIZE / 2), game_rect.y + int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2), RADIUS, BLACK)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                screen.blit(player_logo, (game_rect.x + c * SQUARESIZE + 5, game_rect.y + height - (r * SQUARESIZE + SQUARESIZE) + 5))
            elif board[r][c] == AI_PIECE:
                screen.blit(ai_logo, (game_rect.x + c * SQUARESIZE + 5, game_rect.y + height - (r * SQUARESIZE + SQUARESIZE) + 5))
    pygame.display.update()

def draw_winner(screen, text, window_size):
    myfont = pygame.font.SysFont("Comic Sans MS", 75, bold=True)
    label = myfont.render(text, 1, (255, 0, 0))
    label_rect = label.get_rect(center=(window_size[0] // 2, window_size[1] // 8))
    screen.blit(label, label_rect)
    pygame.display.update()

def main():
    global SQUARESIZE, RADIUS

    pygame.init()

    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    window_size = screen.get_size()

    SQUARESIZE = window_size[1] // (ROW_COUNT + 1)
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE

    RADIUS = int(SQUARESIZE / 2 - 5)

    player_logo = pygame.image.load("images/player_logo.png")
    ai_logo = pygame.image.load("images/ai_logo.png")
    background = pygame.image.load("images/background.png")
    background = pygame.transform.scale(background, window_size)

    player_logo = pygame.transform.scale(player_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
    ai_logo = pygame.transform.scale(ai_logo, (SQUARESIZE - 10, SQUARESIZE - 10))

    board = create_board()
    print_board(board)
    game_over = False
    winner_text = ""

    game_rect = pygame.Rect((window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height)

    draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
    pygame.display.update()

    turn = random.randint(PLAYER, AI)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                window_size = event.size
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                SQUARESIZE = window_size[1] // (ROW_COUNT + 1)
                width = COLUMN_COUNT * SQUARESIZE
                height = (ROW_COUNT + 1) * SQUARESIZE
                RADIUS = int(SQUARESIZE / 2 - 5)
                game_rect = pygame.Rect((window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height)
                background = pygame.transform.scale(background, window_size)
                player_logo = pygame.transform.scale(player_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
                ai_logo = pygame.transform.scale(ai_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
                draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
            if event.type == pygame.MOUSEMOTION:
                screen.blit(background, (0, 0))
                draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
                posx = event.pos[0] - game_rect.x
                if turn == PLAYER:
                    if 0 <= posx <= width:
                        screen.blit(player_logo, (game_rect.x + posx - player_logo.get_width() // 2, game_rect.y + int(SQUARESIZE / 2 - player_logo.get_height() / 2)))
                pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                screen.blit(background, (0, 0))
                draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
                if turn == PLAYER:
                    posx = event.pos[0] - game_rect.x
                    col = int(math.floor(posx / SQUARESIZE))
                    if 0 <= posx <= width and is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        if winning_move(board, PLAYER_PIECE):
                            winner_text = "Player 1 wins!!!"
                            game_over = True
                        turn = (turn + 1) % 2
                        print_board(board)
                        draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
        if turn == AI and not game_over:
            col = random.randint(0, COLUMN_COUNT - 1)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    winner_text = "Player 2 wins!!!"
                    game_over = True
                turn = (turn + 1) % 2
                print_board(board)
                draw_board(board, screen, player_logo, ai_logo, background, game_rect, height)
        if game_over:
            draw_winner(screen, winner_text, window_size)
            pygame.time.wait(3000)

if __name__ == "__main__":
    main()
