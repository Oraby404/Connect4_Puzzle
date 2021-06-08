from numpy import zeros, flip
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

algorithm = -1
MINIMAX = 0
ALPHA_BETA = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
step_default = 4


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
        self.score = 0
        self.prev_col = 0

    def drop_coin(self, col, attribute):
        if self.board[ROWS_COUNT - 1][col] == 0:
            for r in range(ROWS_COUNT):
                if self.board[r][col] == 0:
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

    def checkScore(self, piece):
        score = 0
        opp_piece = PLAYER_PIECE
        if piece == PLAYER_PIECE:
            opp_piece = AI_PIECE

        if self.count(piece) == 4:
            score += 100
        elif self.count(piece) == 3 and self.count(EMPTY) == 1:
            score += 5
        elif self.count(piece) == 2 and self.count(EMPTY) == 2:
            score += 2

        if self.count(opp_piece) == 3 and self.count(EMPTY) == 1:
            score -= 4

        return score

    def calc_score(self, piece):
        score = 0

        ## Score center column
        center_array = [int(i) for i in list(self[:, COLUMNS_COUNT // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        ## Score Horizontal
        for r in range(ROWS_COUNT):
            row_array = [int(i) for i in list(self[r, :])]
            for c in range(COLUMNS_COUNT - 3):
                step = row_array[c:c + step_default]
                score += self.checkScore(step, piece)

        ## Score Vertical
        for c in range(COLUMNS_COUNT):
            col_array = [int(i) for i in list(self[:, c])]
            for r in range(ROWS_COUNT - 3):
                step = col_array[r:r + step_default]
                score += self.checkScore(step, piece)

        ## Score posiive sloped diagonal
        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                step = [self[r + i][c + i] for i in range(step_default)]
                score += self.checkScore(step, piece)

        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                step = [self[r + 3 - i][c + i] for i in range(step_default)]
                score += self.checkScore(step, piece)

        return score

    def minimax(self):
        return random.randint(0, 6)

    def alpha_beta(self):
        return random.randint(0, 6)

    def heuristic(self, piece):
        best_score = -10000
        best_col = random.choice(self.valid_columns)
        for col in self.valid_columns:
            temp_board = deepcopy(self)
            self.drop_coin(temp_board, col, piece)
            score = self.calc_score(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def is_full(self):
        return all([not element for element in self.valid_columns])

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
                    player_turn += 1

                if root.is_full():
                    game_over = True

                root.draw_board()

                player_turn += 1
                player_turn = player_turn % 2

    if player_turn == AI and not game_over:
        if algorithm == MINIMAX:
            insert_in_col = root.minimax()
        else:
            insert_in_col = root.alpha_beta()

        if root.drop_coin(insert_in_col, AI_VALUE):
            player_turn += 1

        if root.is_full():
            game_over = True

        root.draw_board()

        player_turn += 1
        player_turn = player_turn % 2

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
