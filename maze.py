import sys
import time
import heapq
import math
from PIL import Image, ImageDraw

class Node:
    def __init__(self, state, parent, action):
        self.parent = parent
        self.action = action
        self.state = state
        self.g = 0
        self.h = 0
        self.f = self.g + self.h
    
    def __lt__(self, other):
        return self.f < other.f
 
class Maze():

    def __init__(self, maze_map, distance_method):
        with open(maze_map, "r") as file:
            maze = []
            self.maze = []
            rows = file.readlines()
            for row in rows:
                maze.append(list(row.strip('\n')))
                self.maze.append(list(row))
        self.width = max(len(line) for line in maze) 
        self.height = len(maze)
            
        self.walls = []
        for i, row in enumerate(maze):
            for j, char in enumerate(row):
                if char == 'A':
                    self.start = (i,j)
                if char == 'B':
                    self.goal = (i,j)
                if char == '#':
                    self.walls.append((i,j))

        if self.start is None or self.goal is None:
            sys.exit("Không tìm thẩy điểm bắt đầu hoặc điểm kết thúc !")

        if distance_method == "euclide" or distance_method == "chebyshev":
            self.allow_diagonal = True
        self.distance_method = getattr(self, distance_method)
        self.solution = None

    def manhattan(self, node):
        return abs(node.state[0] - self.goal[0]) + abs(node.state[1] - self.goal[1])
    
    def euclide(self, node):
        return math.sqrt(pow(node.state[0] - self.goal[0], 2) + pow(node.state[1] - self.goal[1], 2))
    
    def chebyshev(self, node):
        return max(abs(node.state[0] - self.goal[0]), abs(node.state[1] - self.goal[1]))
    
    def actions(self, node, diagonal = False):
 
        row, col = node.state
        acts = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]
        if diagonal:
            acts.extend(
                [
                    ("up-left", (row - 1, col - 1)),
                    ("down-left", (row + 1, col - 1)),
                    ("up-right", (row - 1, col + 1)),
                    ("down-right", (row + 1, col + 1))
                ]
            )
        new_states = []
        for action, state in acts:
            if 0 <= state[0] < self.height and 0 <= state[1] < self.width:
                if state not in self.walls:
                    new_states.append((action, state))
        return new_states
    
    def Astar(self):

        start = Node(self.start, parent = None, action = None)
        start.h = self.distance_method(start)
        start.g = 0
        start.f = start.h

        self.frontier = [start]
        heapq.heapify(self.frontier)
        self.explored = set()


        while True:
            if len(self.frontier) == 0:
                sys.exit("No solution!")
            else:
                node = heapq.heappop(self.frontier)
                if node.state == self.goal:
                        actions = []
                        path = []
                        while node.parent is not None:
                            actions.append(node.action)
                            path.append(node.state)
                            node = node.parent
                        actions.reverse()
                        path.reverse()
                        self.solution = (actions, path)
                        return
                else:
                    self.explored.add(node.state)
                    for action, state in self.actions(node, self.allow_diagonal):
                        child = Node(state = state, parent = node, action = action)
                        child.h = self.distance_method(child)
                        child.g = node.g + 1
                        child.f = child.h + child.g
                        if child.state not in self.explored and not any(node.state == child.state for node in self.frontier):
                            heapq.heappush(self.frontier, child)

    def result(self):
        if self.solution:
            for i, row in enumerate(self.maze):
                for j, char in enumerate(row):
                    if (i,j) in self.solution[1] and (i,j) != self.start and (i,j) != self.goal:
                        print("*", end = "")
                    elif (i,j) == self.start:
                        print("A", end="")
                    elif (i,j) == self.goal:
                        print("B", end="")
                    else:
                        print(char, end="")
        else:
            print("No Solution!")

    def output_image(self, filename, show_solution=True, show_explored=False):

        cell_size = 50
        cell_border = 2

        # Tạo một canvas trống
        img = Image.new("RGBA", (self.width * cell_size, self.height * cell_size), "black")
        draw = ImageDraw.Draw(img)
        
        for i, row in enumerate(self.maze):
            for j, char in enumerate(row):
                fill = None
                if char == '#':
                    fill = (40, 40, 40)  # Màu tường
                elif (i, j) == self.start:
                    fill = (255, 0, 0)  # Màu điểm bắt đầu
                elif (i, j) == self.goal:
                    fill = (0, 171, 28) # Màu điểm kết thúc
                elif self.solution is not None and show_solution and (i, j) in self.solution[1]:
                    fill = (220, 235, 113) # Màu đường đi
                elif show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85) # Màu các ô đã khám phá
                else:
                    fill = (237, 240, 252) # Màu ô trống

                # Vẽ ô vuông
                if fill:
                    draw.rectangle(
                        ([(j * cell_size + cell_border, i * cell_size + cell_border),
                          ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                        fill=fill
                    )
        # Lưu ảnh
        img.save(filename)

def main():
    '''
    Khởi tạo AI giải mã mê cung và hiển thị kết quả
    '''
    if len(sys.argv) != 3:
        sys.exit("Too many arguments or too few arguments!")
    else:
        maze = Maze(sys.argv[1], sys.argv[2])
        start = time.time()
        maze.Astar()
        end = time.time()
        print("=========Solved Maze=========")
        maze.result()
        maze.output_image("solution.png")
        print()
        print("=========Statistical=========")
        print(f"Number of explored states: {len(maze.explored)}")
        print(f"Past cost: {len(maze.solution[1])}")
        print(f"Run time: {end - start:.3f} secs")
if __name__ == "__main__":
    main()