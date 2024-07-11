import numpy as np
import random
import pygame
import sys
import math
import pygame.gfxdraw

BLUE = (80, 50, 150)
PURPLE = (150, 255, 255)
NUM_ROWS = 6
NUM_COLUMNS = 7

PLAYER = 0
AI = 1

EMPTY = 0
HUMAN_PIECE = 1
COMPUTER_PIECE = 2

WIN_LENGTH = 4

def initialize_board():
    return np.zeros((NUM_ROWS, NUM_COLUMNS))

def place_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_column(board, col):
    return board[NUM_ROWS - 1][col] == 0

def find_next_open_row(board, col):
    for r in range(NUM_ROWS):
        if board[r][col] == 0:
            return r

def display_board(board):
    print(np.flip(board, 0))

def check_winning_move(board, piece):
    for c in range(NUM_COLUMNS - 3):
        for r in range(NUM_ROWS):
            if all(board[r][c + i] == piece for i in range(WIN_LENGTH)):
                return True
    for c in range(NUM_COLUMNS):
        for r in range(NUM_ROWS - 3):
            if all(board[r + i][c] == piece for i in range(WIN_LENGTH)):
                return True
    for c in range(NUM_COLUMNS - 3):
        for r in range(NUM_ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(WIN_LENGTH)):
                return True
            if all(board[r + 3 - i][c + i] == piece for i in range(WIN_LENGTH)):
                return True

def evaluate_window_score(window, piece):
    score = 0
    opp_piece = HUMAN_PIECE if piece == COMPUTER_PIECE else HUMAN_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def evaluate_board(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, NUM_COLUMNS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    for r in range(NUM_ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(NUM_COLUMNS - 3):
            window = row_array[c:c + WIN_LENGTH]
            score += evaluate_window_score(window, piece)

    for c in range(NUM_COLUMNS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(NUM_ROWS - 3):
            window = col_array[r:r + WIN_LENGTH]
            score += evaluate_window_score(window, piece)

    for r in range(NUM_ROWS - 3):
        for c in range(NUM_COLUMNS - 3):
            window = [board[r + i][c + i] for i in range(WIN_LENGTH)]
            score += evaluate_window_score(window, piece)

    for r in range(NUM_ROWS - 3):
        for c in range(NUM_COLUMNS - 3):
            window = [board[r + 3 - i][c + i] for i in range(WIN_LENGTH)]
            score += evaluate_window_score(window, piece)

    return score

def is_terminal_state(board):
    return check_winning_move(board, HUMAN_PIECE) or check_winning_move(board, COMPUTER_PIECE) or len(get_valid_columns(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_columns = get_valid_columns(board)
    is_terminal = is_terminal_state(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if check_winning_move(board, COMPUTER_PIECE):
                return (None, 100000000000000)
            elif check_winning_move(board, HUMAN_PIECE):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, evaluate_board(board, COMPUTER_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_columns)
        for col in valid_columns:
            row = find_next_open_row(board, col)
            b_copy = board.copy()
            place_piece(b_copy, row, col, COMPUTER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_columns)
        for col in valid_columns:
            row = find_next_open_row(board, col)
            b_copy = board.copy()
            place_piece(b_copy, row, col, HUMAN_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_columns(board):
    valid_columns = []
    for col in range(NUM_COLUMNS):
        if is_valid_column(board, col):
            valid_columns.append(col)
    return valid_columns

def choose_best_move(board, piece):
    valid_columns = get_valid_columns(board)
    best_score = -10000
    best_col = random.choice(valid_columns)
    for col in valid_columns:
        row = find_next_open_row(board, col)
        temp_board = board.copy()
        place_piece(temp_board, row, col, piece)
        score = evaluate_board(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

def render_board(board, screen, player_logo, ai_logo, background, game_rect, height):
    background = pygame.transform.scale(background, screen.get_size())

    screen.blit(background, (0, 0)) 

    for c in range(NUM_COLUMNS):
        for r in range(NUM_ROWS):
            pygame.draw.rect(screen, BLUE, (game_rect.x + c * SQUARESIZE, game_rect.y + r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.gfxdraw.aacircle(screen, game_rect.x + int(c * SQUARESIZE + SQUARESIZE / 2), game_rect.y + int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2), RADIUS, PURPLE)
            pygame.gfxdraw.filled_circle(screen, game_rect.x + int(c * SQUARESIZE + SQUARESIZE / 2), game_rect.y + int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2), RADIUS, PURPLE)

    for c in range(NUM_COLUMNS):
        for r in range(NUM_ROWS):
            if board[r][c] == HUMAN_PIECE:
                screen.blit(player_logo, (game_rect.x + c * SQUARESIZE + 5, game_rect.y + height - (r * SQUARESIZE + SQUARESIZE) + 5))
            elif board[r][c] == COMPUTER_PIECE:
                screen.blit(ai_logo, (game_rect.x + c * SQUARESIZE + 5, game_rect.y + height - (r * SQUARESIZE + SQUARESIZE) + 5))

    pygame.display.flip()


def display_winner(screen, text, window_size):
    myfont = pygame.font.SysFont("Comic Sans MS", 75, bold=True)
    label = myfont.render(text, 1, (255, 0, 0))
    label_rect = label.get_rect(center=(window_size[0] // 2, window_size[1] // 8))
    screen.blit(label, label_rect)
    pygame.display.flip()

def main():
    global SQUARESIZE, RADIUS

    pygame.init()

    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE | pygame.DOUBLEBUF)
    window_size = screen.get_size()

    SQUARESIZE = window_size[1] // (NUM_ROWS + 1)
    width = NUM_COLUMNS * SQUARESIZE
    height = (NUM_ROWS + 1) * SQUARESIZE

    RADIUS = int(SQUARESIZE / 2 - 5)

    try:
        player_logo = pygame.image.load("images/player_logo.png")
        ai_logo = pygame.image.load("images/ai_logo.png")
        background = pygame.image.load("images/background.png")
    except pygame.error as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    background = pygame.transform.scale(background, window_size)
    player_logo = pygame.transform.scale(player_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
    ai_logo = pygame.transform.scale(ai_logo, (SQUARESIZE - 10, SQUARESIZE - 10))

    board = initialize_board()
    display_board(board)
    game_over = False
    winner_text = ""

    game_rect = pygame.Rect((window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height)

    render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
    pygame.display.flip()

    turn = random.randint(PLAYER, AI)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                window_size = event.size
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE | pygame.DOUBLEBUF)
                SQUARESIZE = window_size[1] // (NUM_ROWS + 1)
                width = NUM_COLUMNS * SQUARESIZE
                height = (NUM_ROWS + 1) * SQUARESIZE
                RADIUS = int(SQUARESIZE / 2 - 5)
                game_rect = pygame.Rect((window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height)
                background = pygame.transform.scale(background, window_size)
                player_logo = pygame.transform.scale(player_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
                ai_logo = pygame.transform.scale(ai_logo, (SQUARESIZE - 10, SQUARESIZE - 10))
                render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
            if event.type == pygame.MOUSEMOTION:
                screen.blit(background, (0, 0))
                render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
                posx = event.pos[0] - game_rect.x
                if turn == PLAYER:
                    if 0 <= posx <= width:
                        screen.blit(player_logo, (game_rect.x + posx - player_logo.get_width() // 2, game_rect.y + int(SQUARESIZE / 2 - player_logo.get_height() / 2)))
                pygame.display.flip()
            if event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0] - game_rect.x
                render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
                if turn == PLAYER:
                    posx = event.pos[0] - game_rect.x
                    col = int(math.floor(posx / SQUARESIZE))
                    if 0 <= posx <= width and is_valid_column(board, col):
                        row = find_next_open_row(board, col)
                        place_piece(board, row, col, HUMAN_PIECE)
                        if check_winning_move(board, HUMAN_PIECE):
                            winner_text = "Player 1 wins!!!"
                            game_over = True
                        turn = (turn + 1) % 2
                        display_board(board)
                        render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
        if turn == AI and not game_over:
            col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
            if is_valid_column(board, col):
                row = find_next_open_row(board, col)
                place_piece(board, row, col, COMPUTER_PIECE)
                if check_winning_move(board, COMPUTER_PIECE):
                    winner_text = "AI wins!!!"
                    game_over = True
                turn = (turn + 1) % 2
                display_board(board)
                render_board(board, screen, player_logo, ai_logo, background, game_rect, height)
        if game_over:
            display_winner(screen, winner_text, window_size)
            pygame.time.wait(3000)

if __name__ == "__main__":
    main()
