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
        self.val = None
        self.uncovered = False
        self.flagged = False
        self.constraints = []

class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.rowDimension = rowDimension
        self.colDimension = colDimension
        self.totalMines = totalMines
        self.starting_point = (startX, startY)
        self.board = {}

        for i in range(self.colDimension):
            for j in range(self.rowDimension):
                s = Square()
                s.x = i
                s.y = j
                s.constant = None
                s.original_constant = None
                s.nearby_bumb = 0
                s.constraints = self.get_neighbors(i, j)
                self.board[(i, j)] = s
                
        self.moves = []
        self.path_uncovered = []
        self.mines_flagged = set()
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
                if (dx != 0 or dy != 0) and (0 <= x + dx < self.rowDimension) and (0 <= y + dy < self.colDimension):
                    neighbors.append((x + dx, y + dy))
        return neighbors

    def getAction(self, number: int) -> "Action":
        if self.previous_square:
            self.uncover_square(self.previous_square, number)

        # Process straightforward uncovering until there are no more safe squares to uncover
        while self.squares_to_probe:
            square = self.squares_to_probe.pop()
            x, y = square
            self.previous_square = (x, y)
            print("Trying simplify_constraints")
            self.simplify_constraints()
            current_square = self.get_current_square(x, y)
            if current_square.flagged:
                return Action(AI.Action.FLAG, x, y)     
            return Action(AI.Action.UNCOVER, x, y)
        
        if len(self.moves) > 0 and self.totalMines > 0:
            print("Searching")
            self.search()
            

        if not self.squares_to_probe:
            if not self.moves:
                print("No more safe moves. Leaving the game.")
                return Action(AI.Action.LEAVE)




    def uncover_square(self, square, number):
        if square in self.probed_squares:
            return
        x, y = square
        
        self.probed_squares.add(square)
        self.path_uncovered.append((square, 'uncovered'))
        
        current = self.get_current_square(x, y)
        current.uncovered = True
        current.original_constant = number
        current.constant = number - current.nearby_bumb
        self.mark_square_as_safe(square)
        if current.constant == 0:
            
            neighbors = self.get_neighbors(x, y)
            for n in neighbors:
                if n not in self.probed_squares and n not in self.squares_to_probe and n not in self.mines_flagged:
                    self.squares_to_probe.append(n)
                    print(f"Adding neighbor {n} to probe list")
        else:
            if current not in self.moves:
                self.moves.append(current)


    def get_current_square(self, x, y):
        return self.board[(x, y)]
    
    def mark_square_as_safe(self, square):
        x, y = square
        current_square = self.get_current_square(x, y)
        current_square.val = 0
        current_square.uncovered = True

        neighbors = self.get_neighbors(x, y)
        for nx, ny in neighbors:
            neighbor_square = self.get_current_square(nx, ny)
            if square in neighbor_square.constraints:
                neighbor_square.constraints.remove(square)
    
    def mark_square_as_mine(self, square):
        self.path_uncovered.append((square,'flagged'))
        self.num_mines_flagged += 1
        self.totalMines -= 1
        self.mines_flagged.add(square)
        self.mark_square(square,is_mine=True)
        return




    def simplify_constraints(self):
        constraints_to_remove = set()
        for move in self.moves:
            if len(move.constraints) == move.constant:
                print("These are mines")
                while move.constraints:
                    square = move.constraints.pop()
                    self.mark_square_as_mine(square)
                constraints_to_remove.add(move)
            elif move.constant == 0:
                print("All safe")
                while move.constraints:
                    square = move.constraints.pop()
                    self.squares_to_probe.append(square)
                constraints_to_remove.add(move)
        for m in constraints_to_remove:
            self.moves.remove(m)

        constraints_to_remove = set()
        if len(self.moves) > 1:
            i = 0
            j = i + 1
            while i < len(self.moves):
                while j < len(self.moves):
                    c1 = self.moves[i]
                    c2 = self.moves[j]
                    to_remove = self.simplify(c1, c2)
                    if to_remove:
                        constraints_to_remove.update(to_remove)
                    j += 1
                i += 1
                j = i + 1
        for m in constraints_to_remove:
            self.moves.remove(m)
        return

    def simplify(self, c1, c2):
        if c1 == c2:
            return
        to_remove = set()
        c1_constraints = set(c1.constraints)
        c2_constraints = set(c2.constraints)
        if c1_constraints and c2_constraints:
            if c1_constraints.issubset(c2_constraints):
                c2.constraints = list(c2_constraints - c1_constraints)
                c2.constant -= c1.constant
                if c2.constant == 0 and len(c2.constraints) > 0:
                    while c2.constraints:
                        c = c2.constraints.pop()
                        if c not in self.squares_to_probe and c not in self.probed_squares:
                            self.squares_to_probe.append(c)
                    to_remove.add(c2)
                elif c2.constant > 0 and c2.constant == len(c2.constraints):
                    while c2.constraints:
                        c = c2.constraints.pop()
                        self.mark_square_as_mine(c)
                    to_remove.add(c2)
                if c1.constant > 0 and c1.constant == len(c1.constraints):
                    while c1.constraints:
                        c = c1.constraints.pop()
                        self.mark_square_as_mine(c)
                    to_remove.add(c1)
                return to_remove
            elif c2_constraints.issubset(c1_constraints):
                return self.simplify(c2, c1)
        return to_remove
    
    
    def mark_square(self, square, is_mine=False):
        x, y = square
        if (x, y) not in self.marked_count:
            self.marked_count[(x, y)] = 1
        else:
            self.marked_count[(x, y)] += 1
        self.marked_squares.add(square)
        current_square = self.get_current_square(x, y)

        if current_square.val is not None:
            return
        else:
            if is_mine:
                current_square.val = 1
                current_square.flagged = True
                
            else:
                current_square.val = 0
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
                            print("nearby_bumb +1")
                            neighbor_square.nearby_bumb += 1
            x, y = square
            current_square = self.get_current_square(x, y)
            if is_mine:
                return Action(AI.Action.FLAG, x, y)


    def search(self):
        # Backtracking for all solutions with the remaining squares
        leftovers = {}
        # Make a list of unknown constraints
        for m in self.moves:
            if m.constraints:
                for constraint in m.constraints:
                    if constraint not in leftovers:
                        leftovers[constraint] = 1
                    else:
                        leftovers[constraint] += 1
        squares = list(leftovers.keys())
        mines_left = self.totalMines - self.num_mines_flagged
        squares_left = len(squares)

        def backtrack(comb):
            if len(comb) > squares_left:
                return
            elif sum(comb) > mines_left:
                return
            else:    
                for choice in [0, 1]:
                    comb.append(choice)
                    if sum(comb) == mines_left and len(comb) == squares_left:
                        valid = self.check_solution_validity(squares, comb)
                        if valid:
                            # Only keep valid solutions
                            c = comb.copy()
                            solutions.append(c)
                    backtrack(comb)
                    comb.pop()

        solutions = []
        # Backtrack to find solutions if there are fewer mines than squares
        if mines_left < squares_left:
            backtrack([])

        if solutions:
            # Check if any squares are safe in all solutions
            square_solution_counts = {}
            for s in range(len(solutions)):
                for sq in range(len(solutions[s])):
                    current_square = squares[sq]
                    if current_square not in square_solution_counts:
                        square_solution_counts[current_square] = solutions[s][sq]
                    else:
                        square_solution_counts[current_square] += solutions[s][sq]
            added_safe_squares = False
            for square, count in square_solution_counts.items():
                if count == 0:
                    added_safe_squares = True
                    self.squares_to_probe.append(square)
            if not added_safe_squares:
                # Pick a random solution and probe safe squares
                random_solution = random.randint(0, len(solutions) - 1)
                comb = solutions[random_solution]
                for square, value in zip(squares, comb):
                    if value == 0:
                        # Currently just adding all squares marked as safe in the first solution in list
                        self.squares_to_probe.append(square)
        else:
            # No solutions, so pick a random square
            squares_left = list(set(self.board.keys()) - self.marked_squares)
            random_square = random.randint(0, len(squares_left) - 1)
            next_square = squares_left[random_square]
            self.squares_to_probe.append(next_square)

    def check_solution_validity(self,squares,comb):
        """check each solution from backtracking to make sure they don't violate constraints"""
        all_valid = False
        for square,value in zip(squares,comb):
            all_valid = self.meets_constraints(square,value)
        #after checking validity, set the square's val back to None
        for square in squares:
            x,y = square
            sq = self.get_current_square(x,y)
            sq.val = None
        return all_valid
    
    def meets_constraints(self, variable, val):
        """Sets the variable to the value {0,1} and checks to see if it violates constraints"""
        x, y = variable
        square = self.get_current_square(x, y)
        square.val = val
        neighbors = self.get_neighbors(x, y)

        print(f"Variable: {variable}, Value: {val}")
        print(f"Square: ({x}, {y}), Value set to: {square.val}")
        print(f"Neighbors: {neighbors}")

        for n in neighbors:
            nx, ny = n
            neighbor_square = self.get_current_square(nx, ny)
            neighbor_constant = neighbor_square.original_constant

            print(f"Neighbor: ({nx}, {ny}), Original Constant: {neighbor_constant}, Value: {neighbor_square.val}")

            # Only look at neighbors that are uncovered and aren't mines
            if neighbor_square.val is not None and neighbor_square.val != 1:
                mines, safe, unknown = self.get_neighbor_count((nx, ny))

                print(f"Neighbor Counts - Mines: {mines}, Safe: {safe}, Unknown: {unknown}")

                if mines > neighbor_constant:
                    # Violation: too many mines
                    print(f"Violation: Too many mines at ({nx}, {ny}). Mines: {mines}, Constant: {neighbor_constant}")
                    return False
                elif (neighbor_constant - mines) > unknown:
                    # Violation: not enough mines
                    print(f"Violation: Not enough mines at ({nx}, {ny}). Mines: {mines}, Unknown: {unknown}")
                    return False

        print("No violations found.")
        return True

    def get_neighbor_count(self, variable):
        """
        Return count of mines, safe squares, and unknown squares around the variable
        """
        nx, ny = variable
        # Get its neighbors
        nbors = self.ms.get_neighbors(nx, ny)
        mine_count = 0
        unknown_count = 0
        safe_count = 0

        print(f"Variable: {variable}")
        print(f"Neighbors: {nbors}")

        for nb in nbors:
            nbx, nby = nb
            nbor_square = self.get_current_square(nbx, nby)

            print(f"Neighbor: ({nbx}, {nby}), Value: {nbor_square.val}")

            # TODO - need to take into account unknowns
            if nbor_square.val == 1:
                mine_count += 1
            elif nbor_square.val == 0:
                safe_count += 1
            elif nbor_square.val is None:
                unknown_count += 1

        print(f"Mine Count: {mine_count}, Safe Count: {safe_count}, Unknown Count: {unknown_count}")

        return mine_count, safe_count, unknown_count
