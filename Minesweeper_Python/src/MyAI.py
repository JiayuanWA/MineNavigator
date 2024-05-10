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


from AI import AI
from Action import Action
from collections import defaultdict
import itertools

class MyAI(AI):
    def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
        self.rowDimension = rowDimension
        self.colDimension = colDimension
        self.totalMines = totalMines
        self.startX = startX
        self.startY = startY
        self.board = [['.' for _ in range(colDimension)] for _ in range(rowDimension)]
        self.uncovered = set()
        self.mines = set()
        self.queue = set()  # Initialize queue attribute
        self.initialize_board()
        self.previousX, self.previousY = startX, startY

    def initialize_board(self):
        self.board[self.startX][self.startY] = 0
        self.uncovered.add((self.startX, self.startY))
        self.enqueue(self.startX, self.startY)
        print("Queue after initialize", self.queue) 

    def getNeighbors(self, x, y):
        adjacency = [-1, 0, 1]
        neighbors = []
        for dx in adjacency:
            for dy in adjacency:
                if dx != 0 or dy != 0:  # Exclude the cell (x, y) itself
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rowDimension and 0 <= ny < self.colDimension:
                        neighbors.append((nx, ny))
        return neighbors


    def countAdjacentMines(self, x, y):
        count = 0
        for nx, ny in self.getNeighbors(x, y):
            if (nx, ny) in self.mines:
                count += 1
        return count

    def uncover(self, x, y):
        self.uncovered.add((x, y))
        print(f"Uncovering ({x}, {y}).")
        self.enqueue(x, y)
        print("Current queue:", self.queue) 
        return Action(AI.Action.UNCOVER, x, y)

    def flag(self, x, y):
        self.mines.add((x, y))
        return Action(AI.Action.FLAG, x, y)

    def solve(self, x, y):
        
        print(f"Solving cell ({x+1}, {y+1}) with value {self.board[x][y]}") 
        
        
        if (x, y) in self.uncovered:
            print("returned becuase is in self.uncovered")
            return
        
        print("In solve, added to uncovered")
        
        if self.board[x][y] == 0:
            self.uncovered.add((x, y))
            print("Enqueuing cell due to 0 value.")
            self.enqueue(x, y)
            for nx, ny in self.getNeighbors(x, y):
                self.solve(nx, ny)
        elif self.board[x][y] != '.' and self.board[x][y] > 0:  # Check if cell is not covered and is a number
            adjacent_mines = self.countAdjacentMines(x, y)
            if adjacent_mines == self.board[x][y]:
                for nx, ny in self.getNeighbors(x, y):
                    if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines:
                        self.mines.add((nx, ny))
                        return Action(AI.Action.FLAG, nx, ny)
            elif adjacent_mines > 0:
                for nx, ny in self.getNeighbors(x, y):
                    if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines:
                        return self.uncover(nx, ny)


    def enqueue(self, x, y):
        for nx, ny in self.getNeighbors(x, y):
            if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines:
                self.queue.add((nx, ny))
                print(f"Added cell ({nx}, {ny}) to the queue.")

                

    def getAction(self, number: int) -> "Action Object":
        
        #Get start
        x, y = self.previousX, self.previousY
        self.board[x][y] = number

        if len(self.uncovered) == (self.rowDimension * self.colDimension) - self.totalMines:
            return Action(AI.Action.LEAVE)
        
        print("Entering Solve")
        action = self.solve(x, y)
        
        print("Exiting Solve")
        
        if action:
            self.previousX, self.previousY = action.x, action.y
            return action

        if not self.queue:
            self.calculate_probabilities()

        x, y = self.queue.pop()
        self.previousX, self.previousY = x, y
        
        print("Before action:", self.uncovered) 
       # self.enqueue(x, y)
      
        return Action(AI.Action.UNCOVER, x, y)

    def calculate_probabilities(self):
        # not yet
        pass

    
    
    
    