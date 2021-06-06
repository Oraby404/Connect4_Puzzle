from numpy import zeros
from copy import deepcopy
import time

class C4Puzzle:
    def __init__(self, board, valid_columns):
        self.board = board
        self.children = []
        self.valid_columns = valid_columns
        self.cutoff = 3

    def generate_children(self, attr):
        col_count = 0
        for i in range(5, -1, -1):
            if col_count < 7:
                for j in self.valid_columns[i]:
                    new_board = deepcopy(self.board)
                    new_valid_columns = deepcopy(self.valid_columns)
                    new_board[i][j] = attr
                    new_valid_columns[i].remove(j)
                    if i > 0:
                        new_valid_columns[i - 1].append(j)
                    new_node = C4Puzzle(new_board, new_valid_columns)
                    self.children.append(new_node)
                    col_count += 1
            else:
                break

    def create_tree(self, turn, depth):
        if depth < self.cutoff:
            # max turn
            if turn == 0:
                self.generate_children(1)
                for child in self.children:
                    child.create_tree(1, depth + 1)
            # min turn
            else:
                self.generate_children(-1)
                for child in self.children:
                    child.create_tree(0, depth + 1)

    def minimax(self):
        pass

    def alpha_beta(self):
        pass

    def heuristic(self):
        pass


root = C4Puzzle(zeros((6, 7), int), [[], [], [], [], [], [0, 1, 2, 3, 4, 5, 6]])

start_time = time.time()
root.create_tree(0, 0)
running_time = time.time() - start_time
print(running_time)

