# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

import random
from collections import deque
from AI import AI
from Action import Action

class Square:
    def __init__(self):
        self.x = None
        self.y = None
        self.constant = None
        self.original_constant = None
        self.nearby_bumb = 0
        self.uncovered = False
        self.flagged = False
        self.constraints = []

class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        #we have 16 rows
        #print(f"rows i have {rowDimension}")
        self.rowDimension = rowDimension
        #print(f"col i have {colDimension}")
        #we have 30 columns
        self.colDimension = colDimension
        self.totalMines = totalMines
        self.win = rowDimension*colDimension - totalMines
        self.starting_point = (startX, startY)
        self.board = {}

        for y in range(self.rowDimension):
            for x in range(self.colDimension):
                s = Square()
                s.x = x
                s.y = y
                s.constant = None
                s.original_constant = None
                s.nearby_bumb = 0
                s.constraints = self.get_neighbors(x, y)
                self.board[(x, y)] = s
                
        self.moves = []
        self.path_uncovered = []
        self.mines_flagged  = []
        self.marked_squares = set()
        self.marked_count = {}
        self.probed_squares = set()
        self.num_mines_flagged = 0
        self.squares_to_probe = [self.starting_point]
        self.previous_square = None

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx != 0 or dy != 0) and (0 <= x + dx < self.colDimension) and (0 <= y + dy < self.rowDimension):
                    neighbors.append((x + dx, y + dy))
        return neighbors

    
    def getAction(self, number: int) -> "Action":
        #print(f"total_mines {self.totalMines}")
        #print(f"path_uncovered {len(self.probed_squares)}")
        
        while len(self.probed_squares) < self.win: 
            
            if self.previous_square:
                self.straightforward(self.previous_square, number)
    
            while self.squares_to_probe:
   
                square = self.squares_to_probe.pop()
                x, y = square
                self.previous_square = (x, y)
                self.constraint_check()
                #print(f"Squares to probe: {self.squares_to_probe}")
                
                #print(f"self.mines_flagged: {self.mines_flagged}")
                #print(f"X is: {x}, y is {y}")
                return Action(AI.Action.UNCOVER, x, y)
            
            if not self.squares_to_probe:
                #print("probabilities logic")
                probabilities = self.calculate_probabilities()
                best_square = min(probabilities, key=probabilities.get)
                #print(f"Best pick based on probabilities: {best_square} with probability {probabilities[best_square]}")
                x, y = best_square
                self.previous_square = (x, y)
                self.constraint_check()
                
                if probabilities[best_square] == 1:
                    #print(f"Probability found a mine at {best_square}")
                    return Action(AI.Action.FLAG, x, y)
                else:
                    #print(f"Uncovering square {best_square} based on probability")
                    return Action(AI.Action.UNCOVER, x, y)
            
            if not self.squares_to_probe:
                if not self.moves:
                    #print("No more safe moves. Leaving the game.")
                    return Action(AI.Action.LEAVE)
    
        return Action(AI.Action.LEAVE)

    def straightforward(self, square, number):
        if square in self.probed_squares:
            return
        x, y = square
        
        self.probed_squares.add(square)
        self.path_uncovered.append((square, 'uncovered'))
        
        current = self.get_current_square(x, y)
        current.uncovered = True
        current.original_constant = number
        current.constant = number - current.nearby_bumb
        self.is_safe(square)
        if current.constant == 0:
            
            neighbors = self.get_neighbors(x, y)
            for n in neighbors:
                if n not in self.probed_squares and n not in self.squares_to_probe and n not in self.mines_flagged:
                    self.squares_to_probe.append(n)
                    #print(f"Adding neighbor {n} to probe list")
        else:
            if current not in self.moves:
                self.moves.append(current)


    def get_current_square(self, x, y):
        if (x, y) not in self.board:
            print(f"Error: Attempt to access out of bounds square ({x}, {y})")
            return None  # Add a return value to handle the error case
        return self.board[(x, y)]
    
        
    def is_safe(self, square):
        x, y = square
        current_square = self.get_current_square(x, y)
        current_square.uncovered = True

        neighbors = self.get_neighbors(x, y)
        for nx, ny in neighbors:
            neighbor_square = self.get_current_square(nx, ny)
            if square in neighbor_square.constraints:
                neighbor_square.constraints.remove(square)
    
    def is_mine(self, square):
        x, y = square
        current_square = self.get_current_square(x, y)

        if square not in self.mines_flagged:
            self.mines_flagged.append(square)
            self.path_uncovered.append((square,'flagged'))
            self.totalMines -= 1
            #print(f"i subtracting one from totalMine count {self.totalMines}")
            self.num_mines_flagged += 1
            self.mark_square(square,is_mine=True)
        return 



    def constraint_check(self):
        remove_list = set()
        for move in self.moves:
            if len(move.constraints) == move.constant:
                #print(f"These are mines around me {move}")
                while move.constraints:
                    square = move.constraints.pop()
                    self.is_mine(square)
                remove_list.add(move)
            elif move.constant == 0:
                #print("All safe")
                while move.constraints:
                    square = move.constraints.pop()
                    self.squares_to_probe.append(square)
                remove_list.add(move)
        for m in remove_list:
            self.moves.remove(m)

        remove_list = set()
        if len(self.moves) > 1:
            i = 0
            j = i + 1
            while i < len(self.moves):
                while j < len(self.moves):
                    a = self.moves[i]
                    b = self.moves[j]
                    to_remove = self.simplify(a, b)
                    if to_remove:
                        remove_list.update(to_remove)
                    j += 1
                i += 1
                j = i + 1
        for m in remove_list:
            self.moves.remove(m)
        return

    def simplify(self, a, b):
        if a == b:
            return
        to_remove = set()
        a_constraints = set(a.constraints)
        b_constraints = set(b.constraints)
        if a_constraints and b_constraints:
            if a_constraints.issubset(b_constraints):
                b.constraints = list(b_constraints - a_constraints)
                b.constant -= a.constant
                if b.constant == 0 and len(b.constraints) > 0:
                    while b.constraints:
                        c = b.constraints.pop()
                        if c not in self.squares_to_probe and c not in self.probed_squares:
                            self.squares_to_probe.append(c)
                    to_remove.add(b)
                elif b.constant > 0 and b.constant == len(b.constraints):
                    while b.constraints:
                        c = b.constraints.pop()
                        self.is_mine(c)
                    to_remove.add(b)
                if a.constant > 0 and a.constant == len(a.constraints):
                    while a.constraints:
                        c = a.constraints.pop()
                        self.is_mine(c)
                    to_remove.add(a)
                return to_remove
            elif b_constraints.issubset(a_constraints):
                return self.simplify(b, a)
        return to_remove
    
    
    def mark_square(self, square, is_mine=False):
        x, y = square
        if (x, y) not in self.marked_count:
            self.marked_count[(x, y)] = 1
        else:
            self.marked_count[(x, y)] += 1
        self.marked_squares.add(square)
        current_square = self.get_current_square(x, y)


        if is_mine:
            current_square.flagged = True
                
        else:
            current_square.uncovered = True

        neighbors = self.get_neighbors(x, y)
        for neighbor in neighbors:
            nx, ny = neighbor
            neighbor_square = self.get_current_square(nx, ny)
            if (x, y) in neighbor_square.constraints:
                neighbor_square.constraints.remove(square)
                if is_mine:
                    if neighbor_square.constant is not None:
                        neighbor_square.constant -= 1
                    else:
                        #print("nearby_bumb score +1")
                        neighbor_square.nearby_bumb += 1
        x, y = square
        current_square = self.get_current_square(x, y)

    def calculate_probabilities(self):
        remaining_mines = self.totalMines
        remaining_cells = (self.colDimension * self.rowDimension) - len(self.probed_squares)
        
        #print(f"Calculating probabilities: {remaining_mines} remaining mines, {remaining_cells} remaining cells")
        
        probabilities = {}
        for cell in self.get_unrevealed_cells():
            probabilities[cell] = remaining_mines / remaining_cells
        
        for cell in self.get_revealed_cells():
            if self.is_numbered(cell):
                self.adjust_probabilities_around_cell(cell, probabilities)
        
        return probabilities
    
    def adjust_probabilities_around_cell(self, cell, probabilities):
        x, y = cell
        adjacent_cells = self.get_neighbors(x, y)
        number = self.get_number(cell)
        flagged_adjacent = self.count_flagged(adjacent_cells)
        unflagged_adjacent = [c for c in adjacent_cells if not self.is_flagged(c) and not self.is_revealed(c)]
        

        if len(unflagged_adjacent) > 0:
            mine_probability = (number - flagged_adjacent) / len(unflagged_adjacent)
            for c in unflagged_adjacent:
                if c in probabilities:
                    probabilities[c] = max(probabilities[c], mine_probability)
        
    
    def get_unrevealed_cells(self):
        return [cell for cell in self.board if not self.board[cell].uncovered and cell not in self.mines_flagged]
        
    def get_revealed_cells(self):
        return [cell for cell in self.board if self.board[cell].uncovered]
        
    def is_numbered(self, cell):
        return self.board[cell].original_constant is not None
        
    def count_flagged(self, cells):
        return sum(1 for cell in cells if cell in self.board and self.board[cell].flagged)
        
    def is_flagged(self, cell):
        return cell in self.board and self.board[cell].flagged
        
    def is_revealed(self, cell):
        return cell in self.board and self.board[cell].uncovered
        
    def get_number(self, cell):
        return self.board[cell].original_constant if cell in self.board else None
