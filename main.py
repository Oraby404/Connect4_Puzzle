from numpy import zeros, flip, array
from copy import deepcopy
import pygame
import sys
import math

ROWS_COUNT = 6
COLUMNS_COUNT = 7

PLAYER = 0
AI = 1

PLAYER_VALUE = 1
AI_VALUE = -1

game_over = 0
player_turn = PLAYER

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
        self.valid_columns = valid_columns
        self.cutoff = 4

    def is_full(self):
        return all([not element for element in self.valid_columns])

    def drop_coin(self, col, attribute):
        if self.board[ROWS_COUNT - 1][col] == 0:
            for r in range(ROWS_COUNT):
                if self.board[r][col] == 0:
                    self.board[r][col] = attribute
                    self.valid_columns[r].remove(col)
                    if r < 5:
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
                    if i < 5:
                        new_valid_columns[i + 1].append(j)
                    new_node = C4Puzzle(new_board, new_valid_columns)
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

    def minimax(self):
        pass

    def alpha_beta(self):
        pass

    def heuristic(self):
        pass

    def print_board(self):
        print(flip(self.board, 0))

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


initial_board = zeros((ROWS_COUNT, COLUMNS_COUNT), int)
initial_columns = [[] for _ in range(ROWS_COUNT)]

for i in range(COLUMNS_COUNT):
    initial_columns[0].append(i)

root = C4Puzzle(deepcopy(initial_board), deepcopy(initial_columns))
# root.create_tree(PLAYER, 0)

pygame.init()
size = (width, height)
RADIUS = int(SQR_SIZE / 2 - 5)
screen = pygame.display.set_mode(size)
my_font = pygame.font.SysFont("monospace", 50)
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
                    player_turn += 1

                if root.is_full():
                    label = my_font.render("Human Won!", 1, RED)
                    screen.blit(label, ((SQR_SIZE * 1.5), (SQR_SIZE - 60) / 2))
                    game_over = True

            # Ask for Player 2 Input
            else:
                pos_x = event.pos[0]
                insert_in_col = int(math.floor(pos_x / SQR_SIZE))
                if root.drop_coin(insert_in_col, AI_VALUE):
                    player_turn += 1

                if root.is_full():
                    label = my_font.render("AI Won!", 1, YELLOW)
                    screen.blit(label, ((SQR_SIZE * 2), (SQR_SIZE - 60) / 2))
                    game_over = True

            root.draw_board()

            player_turn += 1
            player_turn = player_turn % 2

            if game_over:
                game_over = False
                pygame.time.wait(3000)
                root = C4Puzzle(deepcopy(initial_board), deepcopy(initial_columns))
                root.draw_board()
