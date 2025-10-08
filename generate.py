import random
import sys

class Generator():

    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.maze = [
            ["#" for _ in range(width)] for _ in range(height)
        ]

        start_row = random.randrange(self.height)
        start_col = random.randrange(self.width)
        self.start = (start_row, start_col)
        self.maze[start_row][start_col] = "A"

        self.explored = set()
        self.generate_paths()

        while True:
            goal_row = random.randrange(self.height)
            goal_col = random.randrange(self.width)
            if (goal_row, goal_col) != self.start:
                self.goal = (goal_row, goal_col)
                self.maze[goal_row][goal_col] = "B"
                break


    def find_neighbors(self, state):

        row, column = state

        acts = [
            ("up",   (row - 2, column)),
            ("down", (row + 2, column)),
            ("left", (row, column - 2)),
            ("right", (row, column + 2))
        ]

        states = []

        for act, state in acts:
            if 0<= state[0] < self.height and 0 <= state[1] < self.width:
                if state not in self.explored:
                    states.append(state)
        return states

    def generate_paths(self):

        stack = []
        stack.append(self.start)
        self.explored.add(self.start)

        while stack:
            state = stack[-1]
            neighbors = self.find_neighbors(state)

            if neighbors: 
                neighbor = random.choice(neighbors)
                row, col = neighbor

                wall_row = (state[0] + row) // 2
                wall_col = (state[1] + col) // 2
                self.maze[wall_row][wall_col] = " "
                self.maze[row][col] = " "
                
                self.explored.add(neighbor)
                stack.append(neighbor)
            else:
                stack.pop()

def main():
    if len(sys.argv) != 3:
        sys.exit("Too many arguments or too few arguments!")
    else:
        maze = Generator(int(sys.argv[1]), int(sys.argv[2]))
        
        maze.generate_paths()

        with open("mazerandom.txt", "w") as file:
            rows = ["".join(row) + '\n' for row in maze.maze]
            file.writelines(rows)

if __name__ == "__main__":
    main()

