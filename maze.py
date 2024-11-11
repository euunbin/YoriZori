import tkinter as tk
import random
from PIL import Image, ImageTk

MAZE_WIDTH = 15
MAZE_HEIGHT = 15
CELL_SIZE = 40

#DFS 활용 미로 생성
def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]

    stack = [(1, 1)]
    maze[1][1] = 0

    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)

        found_new_cell = False
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width-1 and 1 <= ny < height-1 and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy // 2][x + dx // 2] = 0
                stack.append((nx, ny))
                found_new_cell = True
                break

        if not found_new_cell:
            stack.pop()

    return maze

def display_maze(maze):
    root = tk.Tk()

    canvas_width = MAZE_WIDTH * CELL_SIZE
    canvas_height = MAZE_HEIGHT * CELL_SIZE
    root.geometry(f"{canvas_width + 100}x{canvas_height + 100}")

    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, background="white")
    canvas.pack(padx=50, pady=50)  # 여백 두고 중앙 배치

    wall_image = Image.open('wall.png').resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
    grass_image = Image.open('grass.jpg').resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)

    wall_image_tk = ImageTk.PhotoImage(wall_image)
    grass_image_tk = ImageTk.PhotoImage(grass_image)

    global wall_image_ref, grass_image_ref
    wall_image_ref = wall_image_tk
    grass_image_ref = grass_image_tk

    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:  # 벽
                canvas.create_image(x * CELL_SIZE, y * CELL_SIZE, anchor='nw', image=wall_image_tk)
            elif maze[y][x] == 0:  # 통로
                canvas.create_image(x * CELL_SIZE, y * CELL_SIZE, anchor='nw', image=grass_image_tk)

    root.mainloop()

if __name__ == "__main__":
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    display_maze(maze)