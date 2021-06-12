import numpy
from copy import deepcopy
import pygame
import sys
import math
import graphviz
import time

ROWS_COUNT = 6
COLUMNS_COUNT = 7

# max search depth , equals number of levels , equals number of edges from root to leaf
DEPTH_CUTOFF = 3
GRAPH_DEPTH_CUTOFF = 3

# To choose the player turn , player or ai
PLAYER = 0
AI = 1

# Setting the values inside the board
PLAYER_VALUE = 1
AI_VALUE = -1
EMPTY = 0

# setting the AI algorithm
algorithm = -1
MINIMAX = 0
ALPHA_BETA = 1

# initial values
game_over = 0
player_turn = AI

# setting screen dimensions
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
        # A list of valid positions in the board to drop a piece in it
        self.valid_columns = valid_columns
        # used by minimax algorithm to back up the best minimax value to the parent node
        self.backed_up_score = -1
        # the column that generated the current board configuration
        self.prev_col = 0

    # attribute is the value of the coin inside the board ; PLAYER_VALUE or AI_VALUE or EMPTY
    def drop_coin(self, col, attribute):
        r = 0
        # check if it is possible to drop a piece in the specified column
        if self.board[ROWS_COUNT - 1][col] == EMPTY:
            for r in range(ROWS_COUNT):
                # get the first empty row in the specified column
                if self.board[r][col] == EMPTY:
                    # drop the coin
                    self.board[r][col] = attribute
                    # modify the valid columns to the new values
                    self.valid_columns[r].remove(col)
                    if r < ROWS_COUNT - 1:
                        self.valid_columns[r + 1].append(col)
                    return False, r
        # return true if failed to drop a coin
        # returns the row in which the coin was dropped to be used in other functions
        return True, r

    # attribute is the value of the coin inside the board ; PLAYER_VALUE or AI_VALUE or EMPTY
    def generate_children(self, attribute):
        # col_count to keep track of the generated children count so it can generate
        # the 7 children in 7 iterations (max)
        col_count = 0
        for i in range(ROWS_COUNT):
            if col_count < COLUMNS_COUNT:
                # j is the valid column in this row
                for j in self.valid_columns[i]:
                    # create the child and modify the valid columns to the new values
                    new_board = deepcopy(self.board)
                    new_valid_columns = deepcopy(self.valid_columns)
                    new_board[i][j] = attribute
                    new_valid_columns[i].remove(j)
                    if i < ROWS_COUNT - 1:
                        new_valid_columns[i + 1].append(j)
                    new_node = C4Puzzle(new_board, new_valid_columns)
                    new_node.parent = self
                    new_node.prev_col = j
                    self.children.append(new_node)
                    col_count += 1
            else:
                break

    def create_tree(self, depth, turn):
        if depth > 0:
            if turn == PLAYER:
                # check if the node have no children to avoid the recreation of the same children
                if not len(self.children):
                    self.generate_children(PLAYER_VALUE)
                # for each child , recursively create the children
                for child in self.children:
                    child.create_tree(depth - 1, AI)
            else:
                # check if the node have no children to avoid the recreation of the same children
                if not len(self.children):
                    self.generate_children(AI_VALUE)
                    # for each child , recursively create the children
                for child in self.children:
                    child.create_tree(depth - 1, PLAYER)

    # counts how many connected 4s in a given board
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

    # used by minimax algorithm , finds the maximum score among all children
    def maximize(self):
        # if a leaf node , calculate the score and return it
        if not len(self.children):
            self.backed_up_score = self.evaluate_windows(AI_VALUE)
            return None, self.backed_up_score

        max_child = None
        max_utility = -math.inf

        # the next turn is the PLAYER turn , then we call minimize function so that
        # PLAYER chooses the minimum score among all children
        for child in self.children:
            new_child, utility = child.minimize()

            # if a higher score is found among children , set it as the best child
            if utility > max_utility:
                max_child = child
                max_utility = utility
                self.backed_up_score = utility

        return max_child, max_utility

    # used by minimax algorithm , finds the minimum score among all children
    def minimize(self):
        # if a leaf node , calculate the score and return it
        if not len(self.children):
            self.backed_up_score = self.evaluate_windows(AI_VALUE)
            return None, self.backed_up_score

        min_child = None
        min_utility = math.inf

        # the next turn is the AI turn , then we call maximize function so that
        # AI chooses the maximum score among all children
        for child in self.children:
            new_child, utility = child.maximize()

            # if a lower score is found among children , set it as the best child
            if utility < min_utility:
                min_child = child
                min_utility = utility
                self.backed_up_score = utility

        return min_child, min_utility

    # minimax algorithm , starts by maximizing the children
    def minimax(self):
        child, utility = self.maximize()
        return child

    # used by alpha-beta pruning algorithm , finds the maximum score among all children
    def alpha_beta_maximize(self, alpha, beta):
        if not len(self.children):
            # if a leaf node , calculate the score and return it
            self.backed_up_score = self.evaluate_windows(AI_VALUE)
            return None, self.backed_up_score

        max_child = None
        max_utility = -math.inf

        # the next turn is the PLAYER turn , then we call minimize function so that
        # PLAYER chooses the minimum score among all children
        for child in self.children:
            new_child, utility = child.alpha_beta_minimize(alpha, beta)
            # if a higher score is found among children , set it as the best child
            if utility > max_utility:
                max_child = child
                max_utility = utility
                self.backed_up_score = utility

            # prune the whole branch
            if max_utility >= beta:
                break

            if max_utility > alpha:
                alpha = max_utility

        return max_child, max_utility

    # used by alpha-beta pruning algorithm , finds the minimum score among all children
    def alpha_beta_minimize(self, alpha, beta):
        # if a leaf node , calculate the score and return it
        if not len(self.children):
            self.backed_up_score = self.evaluate_windows(AI_VALUE)
            return None, self.backed_up_score

        min_child = None
        min_utility = math.inf

        # the next turn is the AI turn , then we call maximize function so that
        # AI chooses the maximum score among all children
        for child in self.children:
            new_child, utility = child.alpha_beta_maximize(alpha, beta)

            # if a lower score is found among children , set it as the best child
            if utility < min_utility:
                min_child = child
                min_utility = utility
                self.backed_up_score = utility

            # prune the whole branch
            if min_utility <= alpha:
                break

            if min_utility < beta:
                beta = min_utility

        return min_child, min_utility

    # alpha-beta pruning algorithm , starts by maximizing the children
    def alpha_beta(self, alpha, beta):
        child, utility = self.alpha_beta_maximize(alpha, beta)
        return child

    # given a board , evaluate_windows generate all possible size-of-4 windows and evaluate the score of each one
    def evaluate_windows(self, piece):
        score = 0
        # Score Horizontal
        for r in range(ROWS_COUNT):
            for c in range(COLUMNS_COUNT - 3):
                window = self.board[r][c:c + 4]
                score += self.sum_window_score(window, piece)

            if (r + 1 < ROWS_COUNT) and (
                    (self.board[r + 1].size - numpy.count_nonzero(self.board[r + 1])) == COLUMNS_COUNT):
                break

        # Score Vertical
        for c in range(COLUMNS_COUNT):
            col_array = [self.board[i][c] for i in range(ROWS_COUNT)]

            # Score center column
            if c == 3:
                center_count = col_array.count(piece)
                score += center_count * 2

            for r in range(ROWS_COUNT - 3):
                window = col_array[r:r + 4]
                score += self.sum_window_score(window, piece)
                if col_array[r + 1] == EMPTY:
                    break

        # Score positive sloped diagonal
        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                window = [self.board[r + i][c + i] for i in range(4)]
                score += self.sum_window_score(window, piece)

        # Score negatively sloped diagonal
        for r in range(ROWS_COUNT - 3):
            for c in range(COLUMNS_COUNT - 3):
                window = [self.board[r + 3 - i][c + i] for i in range(4)]
                score += self.sum_window_score(window, piece)

        return score

    # returns the score of a given size-of-4 window
    def sum_window_score(self, window, piece):
        score = 0
        window = list(window)
        if window.count(piece) == 4:
            score += 10000
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 900
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 40
        return score

    # check if the board is full , the end condition of the game
    def is_full(self):
        return all([not element for element in self.valid_columns])

    def print_board(self):
        print(numpy.flip(self.board, 0))

    # GUI
    def draw_board(self):
        # draw the background of the board
        pygame.draw.rect(screen, BLUE, (0, SQR_SIZE, SQR_SIZE * COLUMNS_COUNT, SQR_SIZE * ROWS_COUNT))
        # draw the empty circles in the background
        for i in range(COLUMNS_COUNT):
            for j in range(ROWS_COUNT):
                pygame.draw.circle(screen, GRAY, (
                    int((i + 0.5) * SQR_SIZE), int((j + 1.5) * SQR_SIZE)), RADIUS)

        # after inserting a value , draw the colored circles in the background
        for c in range(COLUMNS_COUNT):
            for r in range(ROWS_COUNT):
                if self.board[r][c] == PLAYER_VALUE:
                    pygame.draw.circle(screen, RED, (
                        int((c + 0.5) * SQR_SIZE), height - int((r + 0.5) * SQR_SIZE)), RADIUS)
                elif self.board[r][c] == AI_VALUE:
                    pygame.draw.circle(screen, YELLOW, (
                        int((c + 0.5) * SQR_SIZE), height - int((r + 0.5) * SQR_SIZE)), RADIUS)
        # update the screen
        pygame.display.update()

    def create_graph(self, graph, root_name, chosen_node, depth, turn):
        if depth > 0:
            if turn:
                for child in self.children:

                    str_score = 'Max\nColumn %d \n' % child.prev_col

                    temp = depth
                    temp_child = child.parent
                    while GRAPH_DEPTH_CUTOFF - temp:
                        temp += 1
                        str_score += 'Previous Column %d \n' % temp_child.prev_col
                        temp_child = temp_child.parent

                    str_score += "Score = " + str(child.backed_up_score)

                    if child == chosen_node:
                        graph.node(str_score, style="filled", fillcolor="red")
                    graph.edge(root_name, str_score)
                    child.create_graph(graph, str_score, chosen_node, depth - 1, PLAYER)
            else:
                for child in self.children:

                    str_score = 'Min\nColumn %d \n' % child.prev_col
                    temp = depth
                    temp_child = child.parent
                    while GRAPH_DEPTH_CUTOFF - temp:
                        temp += 1
                        str_score += 'Previous Column %d \n' % temp_child.prev_col
                        temp_child = temp_child.parent

                    str_score += "Score = " + str(child.backed_up_score)

                    if child == chosen_node:
                        graph.node(str_score, style="filled", fillcolor="red")
                    graph.edge(root_name, str_score)
                    child.create_graph(graph, str_score, chosen_node, depth - 1, AI)


# a function to choose algorithm fot AI
# minimax or alpha-beta
def get_algorithm():
    pygame.draw.rect(screen, GRAY, (0, 0, SQR_SIZE * COLUMNS_COUNT, SQR_SIZE * (ROWS_COUNT + 1)))
    my_font2 = pygame.font.SysFont("monospace", 28)
    label1 = my_font2.render("Press M for MiniMax Algorithm", True, BLUE)
    label2 = my_font2.render("Any other key for Alpha-Beta", True, BLUE)
    screen.blit(label1, (20, 175))
    screen.blit(label2, (25, 275))
    pygame.display.update()

    # loop until a key is pressed
    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                sys.exit()

            # check the key
            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_m:
                    return MINIMAX
                else:
                    return ALPHA_BETA


# an empty 2d array to store the valid locations in which a piece can be dropped
initial_columns = [[] for _ in range(ROWS_COUNT)]
# set all valid columns to the first row
for i in range(COLUMNS_COUNT):
    initial_columns[0].append(i)

# create an instance of the game
root = C4Puzzle(numpy.zeros((ROWS_COUNT, COLUMNS_COUNT), int), deepcopy(initial_columns))

# intialize the gui
pygame.init()
size = (width, height)
RADIUS = int(SQR_SIZE / 2 - 5)
screen = pygame.display.set_mode(size)
my_font = pygame.font.SysFont("monospace", 50)
algorithm = get_algorithm()
pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))
root.draw_board()

# keep playing until the board is full
while not game_over:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # create the piece motion animation
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))
            pos_x = event.pos[0]

            if player_turn == PLAYER:
                pygame.draw.circle(screen, RED, (pos_x, int(SQR_SIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (pos_x, int(SQR_SIZE / 2)), RADIUS)

        pygame.display.update()

        # check if PLAYER dropped a coin
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, GRAY, (0, 0, width, SQR_SIZE))

            if player_turn == PLAYER:
                pos_x = event.pos[0]
                # get the column in which the coin was inserted
                insert_in_col = int(math.floor(pos_x / SQR_SIZE))

                # drop the coin the in the board
                valid, insert_in_row = root.drop_coin(insert_in_col, PLAYER_VALUE)
                # if the column was not a valid location , the turn goes back to PLAYER to drop coin again
                if valid:
                    player_turn = PLAYER
                else:
                    # else the turn goes to AI
                    player_turn = AI
                    root.draw_board()

                # choose which child of the tree was choose by PLAYER
                for children in root.children:
                    if children.board[insert_in_row][insert_in_col] == PLAYER_VALUE:
                        root = children
                        break

                # if the board is full , end the game
                if root.is_full():
                    game_over = True

    if player_turn == AI and not game_over:

        if algorithm == MINIMAX:
            # create the game tree for minimax algorithm
            root.create_tree(DEPTH_CUTOFF, AI)
            # get the best child
            root = root.minimax()
            # graph the game tree
            g = graphviz.Digraph('G')
            root.parent.create_graph(g, "Max\nRoot", root, GRAPH_DEPTH_CUTOFF, PLAYER)
            g.render()
        else:
            # create the game tree for alpha_beta algorithm
            root.create_tree(DEPTH_CUTOFF, AI)
            # get the best child
            root = root.alpha_beta(-math.inf, math.inf)
            # graph the game tree
            g = graphviz.Digraph('G')
            root.parent.create_graph(g, "Max\nRoot", root, GRAPH_DEPTH_CUTOFF, PLAYER)
            g.render()

        # if the board is full , end the game
        if root.is_full():
            game_over = True

        root.draw_board()
        player_turn = PLAYER

    # if the board is full , decide the winner
    if game_over:
        # get the connected 4s for PLAYER
        player_count = root.connections_count(PLAYER_VALUE)
        # get the connected 4s for AI
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
        # restart the game
        game_over = False
        pygame.time.wait(5000)
        root = C4Puzzle(numpy.zeros((ROWS_COUNT, COLUMNS_COUNT), int), deepcopy(initial_columns))
        algorithm = get_algorithm()
        root.draw_board()
