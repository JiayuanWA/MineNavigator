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
        self.tobeflag = set()
        self.queue = set() 
        self.probability = set() 
        self.initialize_board()
        self.previousX, self.previousY = startX, startY
        self.queue_history = []
        self.check = 0
    def initialize_board(self):
        self.board[self.startX][self.startY] = 0
        self.uncovered.add((self.startX, self.startY))
        self.enqueue(self.startX, self.startY)
       # print("Queue after initialize", self.queue) 

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

    # def uncover(self, x, y):
    #     self.uncovered.add((x, y))
    #     print(f"Uncovering ({x}, {y}).")
    #     self.enqueue(x, y)
    #     print("Current queue:", self.queue) 
    #     return Action(AI.Action.UNCOVER, x, y)



    def solve(self, x, y):
        
       # print(f"Solving cell ({x+1}, {y+1}) with value {self.board[x][y]}") 
        

        
        if (x, y) in self.uncovered:
          #  print("returned becuase is in self.uncovered")
            return
        
        # print("In solve, added to uncovered")
        
        if self.board[x][y] == 0:
            self.uncovered.add((x, y))
            # print("Enqueuing cell due to 0 value.")
            self.enqueue(x, y)
            # for nx, ny in self.getNeighbors(x, y):
            #     self.solve(nx, ny)
        elif self.board[x][y] != 0:
           
            total_neighbors = len(self.getNeighbors(x, y))

            # Count the number of uncovered or queued neighbors
            adjacent_uncovered = sum(1 for nx, ny in self.getNeighbors(x, y) if (nx, ny) in self.uncovered or (nx, ny) in self.queue)

            # Calculate the number of covered neighbors
            adjacent_covered = total_neighbors - adjacent_uncovered


            adjacent_mines = self.countAdjacentMines(x, y)
            
#             print(f"adjacent_hidden ({adjacent_covered})")
            
#             print(f"adjacent_uncovered ({adjacent_uncovered})")
            
#             print(f"adjacent_mines ({adjacent_mines})")
            
            if self.board[x][y] == adjacent_mines:
                for nx, ny in self.getNeighbors(x, y):
                    if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines and (nx, ny) not in self.queue:
                        self.queue.add((nx, ny))
                
            
            if  adjacent_covered == self.board[x][y]:
               # print(f"niceeeeee")
                self.uncovered.add((x, y))
                for nx, ny in self.getNeighbors(x, y):
                    if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines and (nx, ny) not in self.queue:
                        self.mines.add((nx, ny))
                        self.tobeflag.add((nx, ny))
                      #  print(f"added to mines")
                    
                        
            else:
                self.queue.add((x, y))
            

    def enqueue(self, x, y):
        for nx, ny in self.getNeighbors(x, y):
            if (nx, ny) not in self.uncovered and (nx, ny) not in self.mines:
                self.queue.add((nx, ny))
                self.solve(nx, ny)
               
                # print(f"Added cell ({nx}, {ny}) to the queue.")

                

    def getAction(self, number: int) -> "Action Object":
        
        #Get start
        x, y = self.previousX, self.previousY
        self.board[x][y] = number
        
        # if len(self.mines) == self.totalMines:
        #     for nx in range(self.rowDimension):
        #         for ny in range(self.colDimension):
        #             if self.board[nx][ny] == '.':
        #                 self.enqueue(nx, ny)
                        
                    
            
        if len(self.uncovered) == (self.rowDimension * self.colDimension) - self.totalMines:
            return Action(AI.Action.LEAVE)
        
#             for nx in range(self.rowDimension):
#                 for ny in range(self.colDimension):
#                     if self.board[nx][ny] == '.':
#                      #   print("Not yet")
#                         self.check == 1
#                         self.queue.add((x, y))
#                         break
                        
    
#            # print("value:", self.check) 
#             if self.check == 0:
#               #  print("Goodbye")
#                 return Action(AI.Action.LEAVE)
        
        
        #print("Entering Solve")
        action = self.solve(x, y)
        
        #print("Exiting Solve")
        
        if action:
            self.previousX, self.previousY = action.x, action.y
            return action
        
        #Implement check self.queue length, if its been the same for 10 times then call calculate_probabilities(self):

        if not self.queue and len(self.uncovered) == (self.rowDimension * self.colDimension) - self.totalMines - 1:
           # print("TAKING MY CHANCESSSSSSSSSSSSS:")
            self.calculate_probabilities()
            
        if len(self.queue_history) >= 15 and all(length == self.queue_history[-1] for length in self.queue_history[-10:]):
          #  print("Queue length has remained the same for 15 consecutive times. Recalculating probabilities...")
            self.calculate_probabilities()
            
        
        
        for x, y in self.tobeflag:
            x, y = self.tobeflag.pop()
            return Action(AI.Action.FLAG, x, y)
            
    
        #print("len(self.probability)", len(self.probability) )
        if len(self.probability) > 0:
            x, y = self.probability.pop()
        else:
            if len(self.queue) > 0:
                x, y = self.queue.pop()
        
        self.previousX, self.previousY = x, y
        
       # print("The queue now contains:", self.queue) 
        # print("The mine now contains:", self.mines) 
      #  print("Tiles with all neibors uncovered = ", len(self.uncovered)) 
        
        
        self.queue_history.append(len(self.queue))
        
        #print("Before action:", self.uncovered)  
        self.score = (self.colDimension * self.rowDimension) - self.totalMines
       # print("Score should end with 1:", self.score)  
        return Action(AI.Action.UNCOVER, x, y)
    

    def calculate_probabilities(self):
        highest_probability = 0
        best_cell = None

        for x in range(self.rowDimension):
            for y in range(self.colDimension):
                if (x, y) not in self.uncovered and (x, y) not in self.mines and (x, y) not in self.queue:
                    total_neighbors = len(self.getNeighbors(x, y))

                    # Count the number of uncovered or queued neighbors
                    adjacent_uncovered = sum(1 for nx, ny in self.getNeighbors(x, y) if (nx, ny) in self.uncovered or (nx, ny) in self.queue)

                    # Calculate the number of covered neighbors
                    adjacent_covered = total_neighbors - adjacent_uncovered

                    adjacent_mines = self.countAdjacentMines(x, y)

                    if adjacent_covered > 0:
                        probability = (self.totalMines - len(self.mines)) / adjacent_covered
                        if probability > highest_probability:
                            highest_probability = probability
                            best_cell = (x, y)

        if best_cell:

            queue_list = list(self.probability)

            queue_list.insert(0, best_cell)

            self.probability = set(queue_list)

         #   print("My chances now contains:", best_cell) 
            
        else:
         #   print("All mines")
            return Action(AI.Action.LEAVE)
  
            
