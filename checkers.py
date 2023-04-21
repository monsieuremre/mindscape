# This file is part of Mindscape. <https://github.com/monsieuremre/mindscape>
# Mindscape is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. Mindscape is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details. You should have received a
# copy of the GNU General Public License along with Mindscape. If not, see
# <https://www.gnu.org/licenses/>.

import time
from copy import deepcopy


# The class where we implement the actual game.
class Checkers:
    # We initialize the board, and the first round is the human, which is red
    def __init__(self):
        self.board = Board()
        self.turn = "RED"
        # Prompt to set the difficulty of the AI
        print("""
How many layers should the AI algorithm have?
More layers means better AI but more computing power.
For decent and speedy results, use three. Higher values
might be slow depending on your system. But if you have
the computing power, you might as well go for it.
        """)
        self.layers = int(input("Number of layers: "))

    # Print winner if there is one and return True, else return False
    def print_winner(self):
        if self.board.winner():
            print("\033c", end="")
            self.board.print_board()
            print(f"{self.board.winner()} HAS WON!")
            return True
        return False

    # Prompt to human user to input their move
    def human_move(self):
        # Using a loop so we keep asking for input if the user gives some
        # invalid input
        while True:
            from_column = ord(input("Move from column(A-H): ")) - 65
            from_row = int(input("Move from row(1-8): ")) - 1
            if from_column < 0 or from_column > 7 or from_row > 7 or from_row < 0:
                print("Invalid input, try again!")
                time.sleep(2)
                continue
            checker = self.board.get_checker(from_row, from_column)
            if checker and (
                ((checker.is_red) and (
                    self.turn == "RED")) or (
                    (not checker.is_red) and (
                    self.turn == "WHITE"))):
                # Same logic here again, we keep asking until we get a valid
                # input
                while True:
                    possible_jumps = self.board.possible_jumps(checker)
                    to_column = ord(input("Move to column(A-H): ")) - 65
                    to_row = int(input("Move to row(1-8): ")) - 1
                    if to_column < 0 or to_column > 7 or to_row > 7 or to_row < 0:
                        print("Invalid input, try again!")
                        time.sleep(2)
                        continue
                    checker_in_destination = self.board.get_checker(
                        to_row, to_column)
                    if (not checker_in_destination) and (
                            (to_row, to_column) in possible_jumps):
                        self.board.make_jump(checker, to_row, to_column)
                        capture = possible_jumps[(to_row, to_column)]
                        if capture:
                            self.board.remove(capture)
                        self.turn_change()
                        return
                    else:
                        print("Invalid input, try again!")
                        time.sleep(2)
            else:
                print("Invalid input, try again!")
                # After printing we wait a little because every game step the
                # terminal is cleared
                time.sleep(2)

    # Changing the turn from white to red or vice versa
    # SIDENOTE: Actually the whites don't have to be necessarily white. They
    # are printed without color formatting on the terminal. That means on a
    # light themed terminal they would be black. But for convenience, they
    # will be referred to as white throughout the program
    def turn_change(self):
        if self.turn == "RED":
            self.turn = "WHITE"
        else:
            self.turn = "RED"

    # One game step
    def game_step(self):
        # We clear the terminal, print who's turn it is and print the board
        print("\033c", end="")
        print(f"\t{self.turn}'S TURN")
        self.board.print_board()
        # Depending on who's turn it is, take action
        if self.turn == "RED":
            self.human_move()
        else:
            self.machine_move()

    # Let the AI make its move
    def machine_move(self):
        print("AI is making a move")
        val, new_board = self.algorithm(
            self.board, self.layers, True, float('-inf'), float('inf'))
        self.board = new_board
        self.turn_change()

    # This is the notorious minimax algorithm
    # We also use alpha beta pruning for optimization
    def algorithm(self, current_config, layers, maximizing, alpha, beta):
        if layers == 0 or current_config.winner() is not None:
            return current_config.evaluation(), current_config
        if maximizing:
            max_val = float('-inf')
            best_choice = None
            for config in self.all_configs(current_config, True):
                val = self.algorithm(config, layers - 1, False, alpha, beta)[0]
                if val > max_val:
                    max_val = val
                    best_choice = config
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return max_val, best_choice
        else:
            min_val = float('inf')
            best_choice = None
            for config in self.all_configs(current_config, False):
                val = self.algorithm(config, layers - 1, True, alpha, beta)[0]
                if val < min_val:
                    min_val = val
                    best_choice = config
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return min_val, best_choice

    # Returns all possible future board configurations for the current state
    def all_configs(self, current_config, for_white):
        configs = []
        if for_white:
            for checker in current_config.get_white_checkers():
                checker_jumps = current_config.possible_jumps(checker)
                for jump, capture in checker_jumps.items():
                    temp = deepcopy(current_config)
                    temp.make_jump(
                        temp.get_checker(
                            checker.row,
                            checker.column),
                        jump[0],
                        jump[1])
                    if capture:
                        temp.remove(capture)
                    configs.append(temp)
        else:
            for checker in current_config.get_red_checkers():
                checker_jumps = current_config.possible_jumps(checker)
                for jump, capture in checker_jumps.items():
                    temp = deepcopy(current_config)
                    temp.make_jump(
                        temp.get_checker(
                            checker.row,
                            checker.column),
                        jump[0],
                        jump[1])
                    if capture:
                        temp.remove(capture)
                    configs.append(temp)
        return configs


# The class where we implement the board, which is the main aspect of the game
class Board:
    def __init__(self):
        # Define the board and initialize values
        self.board = []
        self.make_board()

    # Make a checker do a jump on the board
    def make_jump(self, checker, row, column):
        self.board[checker.row][checker.column], self.board[row][column] = self.board[row][column], self.board[checker.row][checker.column]
        checker.jump(row, column)
        if row == 7 or row == 0:
            checker.is_king = True
            checker.value *= 2

    # Get the checker that is in the given coordinates
    def get_checker(self, row, column):
        return self.board[row][column]

    # Set the default starting configuration on the board
    def make_board(self):
        for i in range(8):
            self.board.append([])
            for j in range(8):
                if j % 2 == ((i + 1) % 2):
                    if i < 3:
                        self.board[i].append(Checker(i, j, False))
                    elif i > 4:
                        self.board[i].append(Checker(i, j, True))
                    else:
                        self.board[i].append(False)
                else:
                    self.board[i].append(False)

    # Output the board to the terminal in a nice looking way
    def print_board(self):
        print("   A  B  C  D  E  F  G  H")
        for i in range(8):
            print(f"{i+1} ", end="")
            for j in range(8):
                checker = self.board[i][j]
                if checker:
                    if checker.is_red:
                        print("[\033[38;2;255;0;0mo\033[0m]", end="")
                    else:
                        print("[o]", end="")
                else:
                    print("[ ]", end="")
            print("\n", end="")

    # Remove checkers from the board
    def remove(self, checker_list):
        for checker in checker_list:
            self.board[checker.row][checker.column] = False

    # Get a list of all red checkers present on the board
    def get_red_checkers(self):
        reds = []
        for row in self.board:
            for checker in row:
                if checker and checker.is_red:
                    reds.append(checker)
        return reds

    # Get a list of all white checkers present on the board
    def get_white_checkers(self):
        whites = []
        for row in self.board:
            for checker in row:
                if checker and not checker.is_red:
                    whites.append(checker)
        return whites

    # Return the winner if any, else None
    def winner(self):
        if not len(self.get_red_checkers()):
            return "WHITE"
        elif not len(self.get_white_checkers()):
            return "RED"
        return None

    # Evaluate the board for the algorithm
    # We assign kings twice as much value as regular checkers
    def evaluation(self):
        return sum([sum([checker.value if checker else 0 for checker in row])
                   for row in self.board])

    # Return a dictionary of all possible jumps. The values of the keys in
    # this dictionary are the coordinates of the checkers that we would
    # capture if we actually made that jump
    def possible_jumps(self, checker):
        jumps_and_captures = {}
        if checker.is_red or checker.is_king:
            jumps_and_captures.update(self.look_children(
                checker.row - 1, max(checker.row - 3, -1), -1, checker.is_red, checker.column))
        if not checker.is_red or checker.is_king:
            jumps_and_captures.update(self.look_children(
                checker.row + 1, min(checker.row + 3, 8), 1, checker.is_red, checker.column))
        return jumps_and_captures

    # Look for children nodes in the abstract search tree for jumps. Children
    # here are the jumps that would follow our initial jump. We recursively
    # look for the current node's children and their children recursively
    # until we reach the end
    def look_children(self, start, end, direction, is_red, current):
        jumps_and_captures = {}
        jumps_and_captures.update(
            self.look_left_child(
                start,
                end,
                direction,
                is_red,
                current - 1))
        jumps_and_captures.update(
            self.look_right_child(
                start,
                end,
                direction,
                is_red,
                current + 1))
        return jumps_and_captures

    # Look for the children of the left child
    def look_left_child(
            self,
            start,
            end,
            direction,
            is_red,
            left,
            captured=[]):
        jumps_and_captures = {}
        new_captured = []
        for i in range(start, end, direction):
            if left < 0:
                break
            temp = self.board[i][left]
            if not temp:
                if captured and not new_captured:
                    break
                elif captured:
                    jumps_and_captures[(i, left)] = new_captured + captured
                else:
                    jumps_and_captures[(i, left)] = new_captured
                if new_captured:
                    if direction == -1:
                        y = max(i - 3, 0)
                    else:
                        y = min(i + 3, 7)
                    jumps_and_captures.update(
                        self.look_left_child(
                            i + direction,
                            y,
                            direction,
                            is_red,
                            left - 1,
                            captured=new_captured))
                    jumps_and_captures.update(
                        self.look_right_child(
                            i + direction,
                            y,
                            direction,
                            is_red,
                            left + 1,
                            captured=new_captured))
            elif (temp.is_red and is_red) or (not temp.is_red and not is_red):
                break
            else:
                new_captured = [temp]
            left -= 1
        return jumps_and_captures

    # Look for the children of the right child
    def look_right_child(
            self,
            start,
            end,
            direction,
            is_red,
            right,
            captured=[]):
        jumps_and_captures = {}
        new_captured = []
        for i in range(start, end, direction):
            if right >= 8:
                break
            temp = self.board[i][right]
            if not temp:
                if captured and not new_captured:
                    break
                elif captured:
                    jumps_and_captures[(i, right)] = new_captured + captured
                else:
                    jumps_and_captures[(i, right)] = new_captured

                if new_captured:
                    if direction == -1:
                        y = max(i - 3, 0)
                    else:
                        y = min(i + 3, 7)
                    jumps_and_captures.update(
                        self.look_left_child(
                            i + direction,
                            y,
                            direction,
                            is_red,
                            right - 1,
                            captured=new_captured))
                    jumps_and_captures.update(
                        self.look_right_child(
                            i + direction,
                            y,
                            direction,
                            is_red,
                            right + 1,
                            captured=new_captured))
            elif (temp.is_red and is_red) or (not temp.is_red and not is_red):
                break
            else:
                new_captured = [temp]
            right += 1
        return jumps_and_captures


# The checker class implemented for the checker pieces on the board
class Checker:
    # Initialize values
    def __init__(self, row, column, is_red):
        self.row = row
        self.column = column
        self.is_red = is_red
        self.is_king = False
        # Values are assigned for the minimax algorithm that the AI will use
        if is_red:
            self.value = -1
        else:
            self.value = 1

    # Make a jump
    def jump(self, row, column):
        self.row = row
        self.column = column
