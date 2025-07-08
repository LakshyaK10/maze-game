import pygame
import json
import os



# Initialize
pygame.init()
TILE_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 18, 14
PANEL_WIDTH = 200
WIDTH, HEIGHT = GRID_WIDTH * TILE_SIZE + PANEL_WIDTH, GRID_HEIGHT * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Level Editor")

# Colors
colors = {
    "B": (0, 0, 0),         # Wall
    "S": (0, 0, 255),       # Start
    "E": (0, 255, 0),       # End
    "H": (150, 150, 150),   # Hiding Spot
    "D": (255, 0, 0),       # Danger/Enemy
    " ": (255, 255, 255)    # Empty space
}

# Tile options with labels
tile_keys = {
    pygame.K_0: (" ", "0 - Empty"),
    pygame.K_1: ("B", "1 - Wall (B)"),
    pygame.K_2: ("S", "2 - Start (S)"),
    pygame.K_3: ("E", "3 - End (E)"),
    pygame.K_4: ("H", "4 - Hiding Spot (H)"),
    pygame.K_5: ("D", "5 - Enemy (D)")
}

tile_labels = list(tile_keys.values())
current_tile = "B"
grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
font = pygame.font.SysFont(None, 28)

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE + PANEL_WIDTH, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, colors[grid[y][x]], rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

def draw_panel():
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, PANEL_WIDTH, HEIGHT))
    y_offset = 20
    screen.blit(font.render("Tile Legend:", True, (0, 0, 0)), (10, y_offset))
    y_offset += 30
    for _, label in tile_labels:
        screen.blit(font.render(label, True, (0, 0, 0)), (10, y_offset))
        y_offset += 30

    screen.blit(font.render("Left click: place", True, (80, 0, 0)), (10, HEIGHT - 90))
    screen.blit(font.render("Right click: erase", True, (80, 0, 0)), (10, HEIGHT - 60))
    screen.blit(font.render("Press 'S' to Save", True, (0, 80, 0)), (10, HEIGHT - 30))

def count_tile(tile_char):
    return sum(row.count(tile_char) for row in grid)

import os

def save_as_txt(folder="custom_level"):
    os.makedirs(folder, exist_ok=True)

    # Find next available file name like level_1.py, level_2.py, etc.
    i = 1
    while os.path.exists(os.path.join(folder, f"level_{i}.py")):
        i += 1
    filename = os.path.join(folder, f"level_{i}.py")

    # Convert grid to Python list-of-strings format
    with open(filename, "w") as f:
        f.write("level_data = [\n")
        for row in grid:
            row_str = "".join(row).replace('"', '\\"')
            f.write(f'    "{row_str}",\n')
        f.write("]\n")

    print(f"Level saved as {filename}")


def save_as_json(filename="custom_level.json"):
    with open(filename, "w") as f:
        json.dump(grid, f)
    print(f"Saved as {filename}")

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))
    draw_panel()
    draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Select tile
        elif event.type == pygame.KEYDOWN:
            if event.key in tile_keys:
                current_tile = tile_keys[event.key][0]
            elif event.key == pygame.K_s:
                save_as_txt()
                save_as_json()

        # Place or erase
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x - PANEL_WIDTH) // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE

        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if pygame.mouse.get_pressed()[0]:  # Left click
                if current_tile == "S" and count_tile("S") >= 1:
                    print("Only one Start (S) allowed.")
                    continue
                elif current_tile == "E" and count_tile("E") >= 1:
                    print("Only one End (E) allowed.")
                    continue
                grid[grid_y][grid_x] = current_tile

            elif pygame.mouse.get_pressed()[2]:  # Right click
                grid[grid_y][grid_x] = " "

pygame.quit()

