import pygame
import sys
import heapq
import random
import time
import os
import importlib.util

import json

SAVE_FILE = "save.json"

def save_progress(level_index):
    with open(SAVE_FILE, "w") as f:
        json.dump({"current_level": level_index}, f)

def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_level", 0)
    return 0

def reset_progress():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

pygame.init()

pygame.mixer.init()
death_sound = pygame.mixer.Sound("death.mp3")
win_sound = pygame.mixer.Sound("win.mp3")

def load_custom_levels(folder="custom_level"):
    level_files = sorted(
        [f for f in os.listdir(folder) if f.startswith("level_") and f.endswith(".py")],
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )

    custom_levels = []
    for filename in level_files:
        path = os.path.join(folder, filename)
        spec = importlib.util.spec_from_file_location("custom_level", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "level_data"):
            level = getattr(module, "level_data")
            if isinstance(level, list) and all(isinstance(row, str) for row in level):
                custom_levels.append(level)

    return custom_levels




WIDTH, HEIGHT = 720, 560
TILE_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 225, 0)
RED   = (225, 0, 0)
GREY  = (150, 150, 150)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

font = pygame.font.SysFont(None, 48)
game_state = "menu"
lives = 3

heart_img = pygame.image.load("heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))


default_levels = [
    [
        "BBBBBBBBBBBBBBBBBB",
        "B S              B",
        "B WWWWW WWWWW  WWB",
        "B     WHH        B",
        "B     HH   BB   WB",
        "BWWWWWW  WW   WWWB",
        "BW              WB",
        "B     WWW        B",
        "BWW  WWW  WW   WWB",
        "B WWW  WW WWW    B",
        "B       W W    WWB",
        "B   WW  WWW      B",
        "B ED        HH  WB",
        "BBBBBBBBBBBBBBBBBB"
    ],
    [
        "BBBBBBBBBBBBBBBBBB",
        "B S     W        B",
        "B WWW WWBWW  WW WB",
        "B B    HH   B    B",
        "BBB BBBBB B   WW B",
        "B B     B B   BB B",
        "B W H W W WWW    B",
        "B  HH W     B  WWB",
        "B BBBBBBBBB BB   B",
        "B      W        WB",
        "W  W W W  WW     W",
        "B  W        WW   B",
        "B  W   D     W   B",
        "BBBBBB EBBBBBBBBBB"
    ]
    # [
    #     "BBBBBBBBBBBBBBBBBB",
    #     "B  S     W     EBB",
    #     "B  WWWWWWWW  WWWBB",
    #     "BB W             B",
    #     "BH W   WW HHH    B",
    #     "BH               B",
    #     "BW WWWW   WWWWWWBB",
    #     "B                B",
    #     "B WW  WWWWWW  WWBB",
    #     "B  W             B",
    #     "B  W   BB BBB  EBB",
    #     "B  W W    B      B",
    #     "B    W HH        B",
    #     "BBBBBBBBBBBBBBBBBB"
    # ]
]
custom_levels = load_custom_levels()

# Combine all levels
levels = default_levels + custom_levels


current_level = load_progress()

enemy_speed = 1
player_speed = TILE_SIZE
walls, player_walls, hiding_spots, patrol_points = [], [], [], []
player = None
end_rect = None
enemies = []
maze_grid = []
enemy_move_timer = 0
enemy_move_delay = 10
hiding_start_time = None
hiding_duration = 5
level_start_time = None
boss_enemy = None

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(x, y, maze, allow_hiding=False):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[ny]):
            tile = maze[ny][nx]
            if tile not in ['B', 'W'] and (allow_hiding or tile != 'H'):
                neighbors.append((nx, ny))
    return neighbors

def astar(maze, start, goal, allow_hiding=False):
    queue = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for neighbor in get_neighbors(*current, maze, allow_hiding):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(queue, (priority, neighbor))
                came_from[neighbor] = current
    path = []
    current = goal
    while current != start:
        if current not in came_from:
            return []
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def pixel_to_grid(rect):
    return (rect.x // TILE_SIZE, rect.y // TILE_SIZE)

def grid_to_pixel(grid_pos):
    return pygame.Rect(grid_pos[0]*TILE_SIZE, grid_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)

def load_level(level_index):
    global walls, player_walls, hiding_spots, enemies, player, end_rect, patrol_points, maze_grid
    global hiding_start_time, level_start_time, boss_enemy
    walls, player_walls, hiding_spots, enemies, patrol_points = [], [], [], [], []
    hiding_start_time = None
    level_start_time = time.time()
    boss_enemy = None
    maze = levels[level_index]
    maze_grid = maze
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if tile == 'B':
                walls.append(rect)
                player_walls.append(rect)
            elif tile == 'W':
                player_walls.append(rect)
            elif tile == 'H':
                hiding_spots.append(rect)
            elif tile == 'S':
                player = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            elif tile == 'E':
                end_rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                # enemies.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == 'D':
                enemies.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == ' ':
                patrol_points.append((x, y))

def draw_lives():
    for i in range(lives):
        screen.blit(heart_img, (10 + i*35, 10))


# Load the first level
load_level(current_level)

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)
    dx = dy = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "playing"

        elif game_state in ["playing", "paused"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = "paused" if game_state == "playing" else "playing"

            if game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        dx, dy = -player_speed, 0
                    elif event.key == pygame.K_RIGHT:
                        dx, dy = player_speed, 0
                    elif event.key == pygame.K_UP:
                        dx, dy = 0, -player_speed
                    elif event.key == pygame.K_DOWN:
                        dx, dy = 0, player_speed

        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                lives = 3
                current_level = 0
                load_level(current_level)
                game_state = "menu"

    if game_state == "menu":
        title = font.render("Maze Game", True, BLACK)
        instruction = font.render("Press ENTER to Start", True, BLUE)
        screen.blit(title, (WIDTH//2 - 100, HEIGHT//2 - 40))
        screen.blit(instruction, (WIDTH//2 - 150, HEIGHT//2 + 10))

    elif game_state == "paused":
        paused_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        paused_overlay.fill((0, 0, 0, 100))
        screen.blit(paused_overlay, (0, 0))
        paused_text = font.render("⏸ Paused - Press 'P' to Resume", True, WHITE)
        screen.blit(paused_text, (WIDTH//2 - 200, HEIGHT//2 - 20))

    elif game_state == "game_over":
        over = font.render("Game Over!", True, RED)
        retry = font.render("Press ENTER to return to menu", True, BLACK)
        screen.blit(over, (WIDTH//2 - 100, HEIGHT//2 - 40))
        screen.blit(retry, (WIDTH//2 - 200, HEIGHT//2 + 10))

    elif game_state == "playing":
        new_player = player.move(dx, dy)
        if new_player.collidelist(player_walls) == -1:
            player = new_player

        player_hidden = any(player.colliderect(h) for h in hiding_spots)
        if player_hidden and hiding_start_time is None:
            hiding_start_time = time.time()
        elif not player_hidden:
            hiding_start_time = None
        if hiding_start_time and time.time() - hiding_start_time > hiding_duration:
            player_hidden = False

        enemy_move_timer += 1
        if enemy_move_timer >= enemy_move_delay:
            enemy_move_timer = 0
            targets = enemies + ([boss_enemy] if boss_enemy else [])
            for i in range(len(targets)):
                start = pixel_to_grid(targets[i])
                goal = pixel_to_grid(player)
                if not player_hidden:
                    path = astar(maze_grid, start, goal, allow_hiding=False)
                else:
                    attempts = 0
                    while attempts < 10:
                        patrol_target = random.choice(patrol_points)
                        if maze_grid[patrol_target[1]][patrol_target[0]] != 'H':
                            break
                        attempts += 1
                    else:
                        patrol_target = start
                    path = astar(maze_grid, start, patrol_target, allow_hiding=False)
                if path:
                    next_step = grid_to_pixel(path[0])
                    targets[i].x = next_step.x
                    targets[i].y = next_step.y

        for wall in player_walls:
            pygame.draw.rect(screen, BLACK, wall)
        for spot in hiding_spots:
            pygame.draw.rect(screen, GREY, spot)
        for wall in walls:
            pygame.draw.rect(screen, (30, 30, 30), wall, 2)

        pygame.draw.rect(screen, YELLOW if player_hidden else BLUE, player)
        pygame.draw.rect(screen, GREEN, end_rect)
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy)
        if boss_enemy:
            pygame.draw.rect(screen, PURPLE, boss_enemy)

        draw_lives()

        for enemy in enemies:
            if player.colliderect(enemy):
                death_sound.play()
                lives -= 1
                if lives > 0:
                    load_level(current_level)
                else:
                    game_state = "game_over"
                break


        if boss_enemy and player.colliderect(boss_enemy):
            lives -= 1
            if lives > 0:
                load_level(current_level)
            else:
                game_state = "game_over"

        if player.colliderect(end_rect):
            win_sound.play()
            elapsed_time = round(time.time() - level_start_time, 2)
            text = font.render(f"You Win! Time: {elapsed_time}s", True, GREEN)
            screen.blit(text, (WIDTH//2 - 180, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(2000)

            current_level += 1
            if current_level >= len(levels):
                current_level = 0
                reset_progress()  # Reset save after finishing all levels
            else:
                save_progress(current_level)

            load_level(current_level)



    pygame.display.flip()

pygame.quit()
sys.exit()
