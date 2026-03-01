import pygame
import math
import random
import time
from queue import PriorityQueue

pygame.init()

ROWS = int(input("Enter number of rows: "))
COLS = int(input("Enter number of columns: "))

WIDTH = 700
GRID_SIZE = 600
CELL = GRID_SIZE // max(ROWS, COLS)

screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("23F-0618")

myfont = pygame.font.SysFont("Courier New", 17)


BACKGROUND = (245, 245, 245)
EMPTY_COLOR = (0, 255, 255)     
WALL_COLOR = (50, 50, 50)       
VISITED_COLOR = (255, 165, 0)    
FRONTIER_COLOR = (0, 255, 255)   
PATH_COLOR = (0, 255, 0)         
START_COLOR = (255, 0, 255)     
END_COLOR = (0, 255, 0)          
LINE_COLOR = (180, 180, 180)   
TEXT_COLOR = (50, 50, 50)  


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * CELL
        self.y = col * CELL
        self.color = EMPTY_COLOR
        self.parent = None

    def get_pos(self):
        return (self.row, self.col)

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x + 1, self.y + 1, CELL - 2, CELL - 2))
        pygame.draw.rect(screen, LINE_COLOR, (self.x, self.y, CELL, CELL), 1)

    def __eq__(self, other):
        return isinstance(other, Node) and self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))


def make_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(COLS):
            grid[i].append(Node(i, j))
    return grid


def draw_grid(grid):
    for row in grid:
        for node in row:
            node.draw()


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def neighbors(grid, node):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    result = []
    for d in dirs:
        r = node.row + d[0]
        c = node.col + d[1]
        if 0 <= r < ROWS and 0 <= c < COLS:
            if grid[r][c].color != WALL_COLOR:
                result.append(grid[r][c])
    return result


def reconstruct(node):
    path = []
    while node.parent:
        path.append(node)
        node = node.parent
    return path[::-1]


def search(grid, start, goal, algo, heuristic):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    g_score = {start: 0}
    visited = set()
    frontier = set([start])
    visited_count = 0

    while not open_set.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        current = open_set.get()[2]
        frontier.discard(current)

        if current == goal:
            return reconstruct(goal), visited_count

        visited.add(current)
        visited_count += 1

        if current != start:
            current.color = VISITED_COLOR

        for n in neighbors(grid, current):
            temp_g = g_score[current] + 1

            if n not in g_score or temp_g < g_score[n]:
                g_score[n] = temp_g
                n.parent = current

                h = heuristic(n.get_pos(), goal.get_pos())
                if algo == "astar":
                    f = temp_g + h
                else:
                    f = h

                count += 1
                open_set.put((f, count, n))
                frontier.add(n)

        for fnode in frontier:
            if fnode not in visited and fnode != start:
                fnode.color = FRONTIER_COLOR

        draw_grid(grid)
        pygame.display.update()
        pygame.time.delay(5)

    return None, visited_count


def main():
    grid = make_grid()
    start = grid[0][0]
    goal = grid[ROWS - 1][COLS - 1]
    start.color = START_COLOR
    goal.color = END_COLOR

    algo = "astar"
    heuristic = manhattan
    dynamic = False

    running = True
    while running:
        screen.fill(BACKGROUND)
        draw_grid(grid)

        info = myfont.render(
            f"Algo: {algo}  |  H: {heuristic.__name__}  |  Dynamic: {dynamic}",
            True,
            TEXT_COLOR,
        )
        screen.blit(info, (10, 612))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                r = pos[0] // CELL
                c = pos[1] // CELL
                if r < ROWS and c < COLS:
                    node = grid[r][c]
                    if node not in [start, goal]:
                        node.color = WALL_COLOR if node.color != WALL_COLOR else EMPTY_COLOR

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    algo = "greedy"
                if event.key == pygame.K_2:
                    algo = "astar"
                if event.key == pygame.K_h:
                    heuristic = euclidean if heuristic == manhattan else manhattan
                if event.key == pygame.K_r:
                    for row in grid:
                        for node in row:
                            if node not in [start, goal]:
                                node.color = WALL_COLOR if random.random() < 0.3 else EMPTY_COLOR
                if event.key == pygame.K_d:
                    dynamic = not dynamic

                if event.key == pygame.K_SPACE:
                    t1 = time.time()
                    path, visited = search(grid, start, goal, algo, heuristic)
                    t2 = time.time()

                    if path:
                        for node in path:
                            if node not in [start, goal]:
                                node.color = PATH_COLOR

                    exec_time = round((t2 - t1) * 1000, 2)

                    dashboard = [
                        f"Nodes Visited: {visited}",
                        f"Path Cost: {len(path) if path else 0}",
                        f"Time (ms): {exec_time}",
                    ]

                    for i, text in enumerate(dashboard):
                        label = myfont.render(text, True, TEXT_COLOR)
                        screen.blit(label, (350, 612 + i * 20))

                    pygame.display.update()

                    if dynamic and path:
                        current = start
                        for step in path:
                            if random.random() < 0.1:
                                r = random.randint(0, ROWS - 1)
                                c = random.randint(0, COLS - 1)
                                if grid[r][c] not in [start, goal]:
                                    grid[r][c].color = WALL_COLOR

                            if step.color == WALL_COLOR:
                                print("Path Blocked -> Replanning")
                                path, _ = search(grid, current, goal, algo, heuristic)

                            current = step
                            pygame.time.delay(100)

    pygame.quit()


if __name__ == "__main__":
    main()