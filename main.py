import numpy
from copy import deepcopy
import pygame
import sys
import math
import random

ROWS_COUNT = 6
COLUMNS_COUNT = 7

PLAYER = 0
AI = 1

PLAYER_VALUE = 1
AI_VALUE = -1
EMPTY = 0

connect_len = 4

algorithm = -1
MINIMAX = 0
ALPHA_BETA = 1

game_over = 0
player_turn = AI

SQR_SIZE = 76
width = COLUMNS_COUNT * SQR_SIZE
height = (ROWS_COUNT + 1) * SQR_SIZE

RED = (175, 0, 0)
BLUE = (0, 50, 150)
YELLOW = (255, 255, 0)
GRAY = (175, 175, 175)


class C4Puzzle:
    def __init__(self, board, valid_columns):
        self.board = board
        self.children = []
        self.parent = None
        self.valid_columns = valid_columns
        self.cutoff = 4
        self.score = 0
        self.prev_col = 0

    def drop_coin(self, col, attribute):
        if self.board[ROWS_COUNT - 1][col] == EMPTY:
            for r in range(ROWS_COUNT):
                if self.board[r][col] == EMPTY:
                    self.board[r][col] = attribute
                    self.valid_columns[r].remove(col)
                    if r < ROWS_COUNT - 1:
                        self.valid_columns[r + 1].append(col)
                    return False
        return True

    def generate_children(self, attribute):
        col_count = 0
        for i in range(ROWS_COUNT):
            if col_count < COLUMNS_COUNT:
                for j in self.valid_columns[i]:
                    new_board = deepcopy(self.board)
                    new_valid_columns = deepcopy(self.valid_columns)
                    new_board[i][j] = attribute
                    new_valid_columns[i].remove(j)
                    if i < ROWS_COUNT - 1:
                        new_valid_columns[i + 1].append(j)

                    new_node = C4Puzzle(new_board, new_valid_columns)
                    new_node.prev_col = j
                    new_node.parent = self
                    self.children.append(new_node)
                    col_count += 1
            else:
                break

    def create_tree(self, turn, depth):
        if depth < self.cutoff:
            # max turn
            if turn == PLAYER:
                self.generate_children(PLAYER_VALUE)
                for child in self.children:
                    child.create_tree(AI, depth + 1)
            # min turn
            else:
                self.generate_children(AI_VALUE)
                for child in self.children:
                    child.create_tree(PLAYER, depth + 1)

    def connections_count(self, attribute):
        count = 0
        # Check horizontal locations
        for c in range(COLUMNS_COUNT - 3):
            for r in range(ROWS_COUNT):
                if self.board[r][c] == attribute \
                        and self.board[r][c + 1] == attribute \
                        and self.board[r][c + 2] == attribute \
                        and self.board[r][c + 3] == attribute:
                    count += 1

        # Check vertical locations
        for c in range(COLUMNS_COUNT):
            for r in range(ROWS_COUNT - 3):
                if self.board[r][c] == attribute \
                        and self.board[r + 1][c] == attribute \
                        and self.board[r + 2][c] == attribute \
                        and self.board[r + 3][c] == attribute:
                    count += 1

        # Check positively sloped diagonals
        for c in range(COLUMNS_COUNT - 3):
            for r in range(ROWS_COUNT - 3):
                if self.board[r][c] == attribute \
                        and self.board[r + 1][c + 1] == attribute \
                        and self.board[r + 2][c + 2] == attribute \
                        and self.board[r + 3][c + 3] == attribute:
                    count += 1

        # Check negatively sloped diagonals
        for c in range(COLUMNS_COUNT - 3):
            for r in range(3, ROWS_COUNT):
                if self.board[r][c] == attribute \
                        and self.board[r - 1][c + 1] == attribute \
                        and self.board[r - 2][c + 2] == attribute \
                        and self.board[r - 3][c + 3] == attribute:
                    count += 1
        return count

    def minimax(self, maximizing_player):
        if maximizing_player:
            return self.heuristic(AI_VALUE)
        else:
            return self.heuristic(PLAYER_VALUE)

    def alpha_beta(self, alpha, beta, maximizing_player):
        if maximizing_player:
            return self.heuristic(AI_VALUE)
        else:
            return self.heuristic(PLAYER_VALUE)

    def heuristic(self, piece):
        best_score = 0
        self.generate_children(piece)
        best_child = random.choice(self.children)
        for child in self.children:
            self.score = child.evaluate_windows(piece)
            if self.score > best_score and self.score != 0:
                best_score = self.score
                best_child = child
        return best_child

    def evaluate_windows(self, piece):
        score = 0
        # Score Horizontal
        for r in range(ROWS_COUNT):
            for c in range(COLUMNS_COUNT - 3):
                window = self.board[r][c:c + connect_len]
                score += self.sum_window_score(window, piece)
            if (r + 1 < ROWS_COUNT) and (self.board[r + 1].count(EMPTY) == COLUMNS_COUNT):
                break

        # Score Vertical
        for c in range(COLUMNS_COUNT):
            col_array = [self.board[i][c] for i in range(ROWS_COUNT)]

            # Score center column
            if c == 3:
                center_count = col_array.count(piece)
                score += center_count * 2

            for r in range(ROWS_COUNT - 3):
                window = col_array[r:r + connect_len]
                score += self.sum_window_score(window, piece)
                if col_array[r + 1] == EMPTY:
                    break

        # Score positive sloped diagonal
        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                window = [self.board[r + i][c + i] for i in range(connect_len)]
                score += self.sum_window_score(window, piece)

        # Score negatively sloped diagonal
        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                window = [self.board[r + 3 - i][c + i] for i in range(connect_len)]
                score += self.sum_window_score(window, piece)

        return score

    def sum_window_score(self, window, piece):
        score = 0
        opp_piece = PLAYER_VALUE
        if piece == PLAYER_VALUE:
            opp_piece = AI_VALUE

        if window.count(piece) == 4:
            score += 10000
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 900
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 40

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 450
        elif window.count(opp_piece) == 2 and window.count(EMPTY) == 2:
            score -= 20

        return score

    def is_full(self):
        return all([not element for element in self.valid_columns])

    def print_board(self):
        arr = numpy.array(self.board)
        print(numpy.flip(arr, 0))

    def draw_board(self):
        pygame.draw.rect(screen, BLUE, (0, SQR_SIZE, SQR_SIZE * COLUMNS_COUNT, SQR_SIZE * ROWS_COUNT))
        for i in range(COLUMNS_COUNT):
            for j in range(ROWS_COUNT):
                pygame.draw.circle(screen, GRAY, (
                    int((i + 0.5) * SQR_SIZE), int((j + 1.5) * SQR_SIZE)), RADIUS)

        for c in range(COLUMNS_COUNT):
            for r in range(ROWS_COUNT):
                if self.board[r][c] == PLAYER_VALUE:
                    pygame.draw.circle(screen, RED, (
                        int((c + 0.5) * SQR_SIZE), height - int((r + 0.5) * SQR_SIZE)), RADIUS)
                elif self.board[r][c] == AI_VALUE:
                    pygame.draw.circle(screen, YELLOW, (
                        int((c + 0.5) * SQR_SIZE), height - int((r + 0.5) * SQR_SIZE)), RADIUS)
        pygame.display.update()


def get_algorithm():
    pygame.draw.rect(screen, GRAY, (0, 0, SQR_SIZE * COLUMNS_COUNT, SQR_SIZE * (ROWS_COUNT + 1)))
    my_font2 = pygame.font.SysFont("monospace", 28)
    label1 = my_font2.render("Press M for MiniMax Algorithm", True, BLUE)
    label2 = my_font2.render("Any other key for Alpha-Beta", True, BLUE)
    screen.blit(label1, (20, 175))
    screen.blit(label2, (25, 275))
    pygame.display.update()

    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                sys.exit()

            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_m:
                    return MINIMAX
                else:
                    return ALPHA_BETA


initial_board = [[0 for i in range(COLUMNS_COUNT)] for j in range(ROWS_COUNT)]

initial_columns = [[] for _ in range(ROWS_COUNT)]

for i in range(COLUMNS_COUNT):
    initial_columns[0].append(i)

root = C4Puzzle(deepcopy(initial_board), deepcopy(initial_columns))

pygame.init()
size = (width, height)
RADIUS = int(SQR_SIZE / 2 - 5)
screen = pygame.display.set_mode(size)
my_font = pygame.font.SysFont("monospace", 50)
algorithm = get_algorithm()
pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))
root.draw_board()

while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))
            pos_x = event.pos[0]

            if player_turn == PLAYER:
                pygame.draw.circle(screen, RED, (pos_x, int(SQR_SIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (pos_x, int(SQR_SIZE / 2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))

            # Ask for Player 1 Input
            if player_turn == PLAYER:
                pos_x = event.pos[0]
                insert_in_col = int(math.floor(pos_x / SQR_SIZE))

                if root.drop_coin(insert_in_col, PLAYER_VALUE):
                    player_turn = PLAYER
                else:
                    player_turn = AI
                    root.draw_board()

                if root.is_full():
                    game_over = True

    if player_turn == AI and not game_over:

        if algorithm == MINIMAX:
            root = root.minimax(AI)
        else:
            root = root.alpha_beta(-math.inf, math.inf, AI)

        if root.is_full():
            game_over = True

        root.draw_board()
        player_turn = PLAYER

    if game_over:
        player_count = root.connections_count(PLAYER_VALUE)
        ai_count = root.connections_count(AI_VALUE)

        if player_count > ai_count:
            label = my_font.render("Human Won!", True, RED)
            screen.blit(label, ((SQR_SIZE * 1.5), (SQR_SIZE - 60) / 2))
        elif ai_count > player_count:
            label = my_font.render("AI Won!", True, YELLOW)
            screen.blit(label, ((SQR_SIZE * 2), (SQR_SIZE - 60) / 2))
        else:
            label = my_font.render("Draw!", True, BLUE)
            screen.blit(label, ((SQR_SIZE * 2.5), (SQR_SIZE - 60) / 2))
        root.draw_board()
        game_over = False
        pygame.time.wait(5000)
        root = C4Puzzle(deepcopy(initial_board), deepcopy(initial_columns))
        algorithm = get_algorithm()
        root.draw_board()
