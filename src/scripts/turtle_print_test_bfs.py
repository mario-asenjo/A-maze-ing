import turtle
import time

from mazegen import MazeGenerator, Maze

generator: MazeGenerator = MazeGenerator(
    width=10,
    height=10,
    entry_c=(0, 0),
    exit_c=(9, 4),
    perfect=True,
    seed=22,
    include_42=True
)
maze: Maze = generator.generate()

output = generator.build_output_sections(maze)
maze_rows = output[0]
entrada_str = output[1]
salida_str = output[2]
path = output[3]

ROWS = len(maze_rows)
COLS = len(maze_rows[0])


def parse_xy(s):
    x, y = s.split(",")
    return int(x), int(y)


entrada = parse_xy(entrada_str)
salida = parse_xy(salida_str)

# ====== TURTLE SETUP ======
screen = turtle.Screen()
screen.title("Laberinto por paredes (hex) + camino")
screen.setup(width=1920, height=1080)
screen.tracer(0, 0)
screen.update()

# ---- CONFIG DINÁMICA ----
MARGIN = 20
W = screen.window_width()
H = screen.window_height()

CELL = max(2, int(min((W - 2*MARGIN) / COLS, (H - 2*MARGIN) / ROWS)))

# centrado clásico (SIN setworldcoordinates)
origin_x = -(COLS * CELL) / 2
origin_y = (ROWS * CELL) / 2

pen = turtle.Turtle(visible=False)
pen.speed(0)
pen.pensize(max(1, CELL // 10))
pen.penup()

walker = turtle.Turtle()
walker.shape("circle")
walker.color("blue")
walker.shapesize(0.3, 0.3)  # pequeño en grids grandes
walker.penup()
walker.speed(0)


def cell_to_screen_center(x, y):
    sx = origin_x + x * CELL + CELL / 2
    sy = origin_y - y * CELL - CELL / 2
    return sx, sy


def draw_wall(x1, y1, x2, y2):
    pen.goto(x1, y1)
    pen.pendown()
    pen.goto(x2, y2)
    pen.penup()


def draw_cell_walls(x, y, hex_char):
    v = int(hex_char, 16)

    # bits: N(1), E(2), S(4), W(8)
    north = v & 1
    east  = v & 2
    south = v & 4
    west  = v & 8

    left   = origin_x + x * CELL
    right  = left + CELL
    top    = origin_y - y * CELL
    bottom = top - CELL

    if north: draw_wall(left, top, right, top)
    if east:  draw_wall(right, top, right, bottom)
    if south: draw_wall(left, bottom, right, bottom)
    if west:  draw_wall(left, top, left, bottom)


def draw_maze():
    pen.color("black")
    for y in range(ROWS):
        row = maze_rows[y]
        for x in range(COLS):
            draw_cell_walls(x, y, row[x])


def stamp_marker(x, y, color):
    marker = turtle.Turtle(visible=False)
    marker.penup()
    marker.speed(0)
    marker.shape("square")
    marker.color(color)
    scale = 0.6 if CELL >= 8 else 0.3
    marker.shapesize(scale, scale)
    marker.goto(cell_to_screen_center(x, y))
    marker.stamp()

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

def animate_path(delay=0.0):
    x, y = entrada
    walker.goto(cell_to_screen_center(x, y))
    walker.pendown()
    walker.pensize(max(1, CELL // 8))

    for step in path:
        if step not in DIRS:
            continue
        dx, dy = DIRS[step]
        x += dx
        y += dy
        walker.goto(cell_to_screen_center(x, y))
        screen.update()
        if delay:
            time.sleep(delay)

# ====== RUN ======
draw_maze()
stamp_marker(*entrada, "green")
stamp_marker(*salida, "red")
screen.update()
animate_path(delay=0.0)
turtle.done()
