import sys
import heapq
import math
from PIL import Image, ImageDraw

class Node:
    """
    Lớp đại diện cho mỗi nút (một trạng thái) trong không gian tìm kiếm của mê cung
    Mỗi nút bao gồm:
        state : vị trí của nút hiện tại trong mê cung
        parent: nút cha dẫn đến nút hiện tại 
        action: hành động dẫn đến trạng thái hiện tại 
        f     : tổng khoảng cách của h và g
        h     : khoảng cách từ nút hiện tại đến đích
        g     : khoảng cách từ nút ban đầu đến hiện tại
    """
    def __init__(self, state, parent, action):
        self.parent = parent
        self.action = action
        self.state = state
        self.g = 0
        self.h = 0
        self.f = self.g + self.h
    
    # Phương thức so sánh nhỏ hơn giũa 2 nút 
    def __lt__(self, other):
        return self.f < other.f
 
class Maze():
    """
    Lớp chính xử lí mê cung:
        1. Đọc mê cung
        2. Tìm đường đi 
        3. Hiển thị kết quả
    """
    def __init__(self, maze_map):
        """
        Đọc file mê cung và thiết lập thông tin ban đầu
        """
        # Đọc mê cung
        with open(maze_map, "r") as file:
            maze = []
            self.maze = []
            rows = file.readlines()
            for row in rows:
                maze.append(list(row.strip('\n')))
                self.maze.append(list(row))
        self.width = max(len(line) for line in maze) 
        self.height = len(maze)
            
        # Lưu vị trí ban đầu, vị trí đích, và các bước tường
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

        # Lưu đường đi tối ưu
        self.solution = None

    def manhattan_distance(self, node):
        """
        Trả về khoảng cách Manhattan từ nút hiện tại đến đích
        """
        return abs(node.state[0] - self.goal[0]) + abs(node.state[1] - self.goal[1])
    
    def euclide_distance(self, node):
        """
        Trả về khoảng cách Euclide từ nút hiện tại đến đích
        """
        return math.sqrt(pow(node.state[0] - self.goal[0], 2) + pow(node.state[1] - self.goal[1], 2))
    
    def diagonal_distance(self, node):
        """
        Trả về khoảng cách Diagonal từ nút hiện tại đến đích
        """
        return max(abs(node.state[0] - self.goal[0]), abs(node.state[1] - self.goal[1]))
    
    def actions(self, node):
        """
        Trả về một danh sách các hành động và trạng thái hợp lệ có thể thực hiện từ node hiện tại.

        Mỗi phần tử trong danh sách trả về là một tuple (action, state) 
        Một hành động được coi là hợp lệ nếu trạng thái kết quả:
            1. Nằm trong phạm vi của mê cung.
            2. Không phải là một bức tường.
        """
        row, col = node.state
        acts = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        new_states = []
        for action, state in acts:
            if 0 <= state[0] < self.height and 0 <= state[1] < self.width:
                if state not in self.walls:
                    new_states.append((action, state))
        return new_states
    
    def Astar(self):
        """
        Thực hiện thuật toán A* tìm đường đi tối ưu
        """
        # Khởi tạo trạng thái ban đầu
        start = Node(self.start, parent = None, action = None)
        start.h = self.manhattan_distance(start)
        start.g = 0
        start.f = start.h

        self.frontier = [start]
        heapq.heapify(self.frontier)
        self.explored = set()

        # Vòng lặp tìm kiếm đường đi
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
                    for action, state in self.actions(node):
                        child = Node(state = state, parent = node, action = action)
                        child.h = self.manhattan_distance(child)
                        child.g = node.g + 1
                        child.f = child.h + child.g
                        if not any(node.state == child.state for node in self.frontier):
                            heapq.heappush(self.frontier, child)

    def result(self):
        """
        In ra đường đi nếu có
        """
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
        """
        Xuất ảnh hiện thị trực quan đường đi 
        """
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
    if len(sys.argv) != 2:
        sys.exit()
    else:
        maze = Maze(sys.argv[1])
        maze.Astar()
        maze.result()
        maze.output_image("mazeA.png")
if __name__ == "__main__":
    main()