# This is the corrected and animated version with smooth player movement setup
# I am replacing immediate tile movement with interpolation

# import pygame
# import sys
# import heapq
# import random
# import time

# pygame.init()
# pygame.mixer.init()

# death_sound = pygame.mixer.Sound("death.mp3")
# win_sound = pygame.mixer.Sound("win.mp3")

# WIDTH, HEIGHT = 720, 560
# TILE_SIZE = 40
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Maze Game")

# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# BLUE = (0, 0, 255)
# GREEN = (0, 225, 0)
# RED = (225, 0, 0)
# GREY = (150, 150, 150)
# YELLOW = (255, 255, 0)
# PURPLE = (128, 0, 128)

# font = pygame.font.SysFont(None, 48)
# game_state = "menu"
# lives = 3

# heart_img = pygame.image.load("heart.png").convert_alpha()
# heart_img = pygame.transform.scale(heart_img, (30, 30))

# levels = [...]  # Keep your original levels array here

# current_level = 0
# enemy_speed = 2
# player_speed = 5  # pixels per frame

# walls, player_walls, hiding_spots, patrol_points = [], [], [], []
# end_rect = None
# enemies = []
# maze_grid = []
# player_pos = None
# player_pixel_pos = None
# player_target_pos = None
# enemy_move_timer = 0
# enemy_move_delay = 10
# hiding_start_time = None
# hiding_duration = 5
# level_start_time = None
# boss_enemy = None

# # ... (same heuristic, astar, grid helpers)

# def load_level(level_index):
#     global walls, player_walls, hiding_spots, enemies, player_pos, player_pixel_pos
#     global player_target_pos, end_rect, patrol_points, maze_grid, hiding_start_time
#     walls, player_walls, hiding_spots, enemies, patrol_points = [], [], [], [], []
#     hiding_start_time = None
#     maze = levels[level_index]
#     maze_grid = maze
#     for y, row in enumerate(maze):
#         for x, tile in enumerate(row):
#             rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
#             if tile == 'B':
#                 walls.append(rect)
#                 player_walls.append(rect)
#             elif tile == 'W':
#                 player_walls.append(rect)
#             elif tile == 'H':
#                 hiding_spots.append(rect)
#             elif tile == 'S':
#                 player_pos = (x, y)
#                 player_pixel_pos = [x * TILE_SIZE, y * TILE_SIZE]
#                 player_target_pos = player_pos
#             elif tile == 'E':
#                 end_rect = rect
#                 enemies.append({'rect': rect.copy(), 'target': (x, y)})
#             elif tile == ' ':
#                 patrol_points.append((x, y))

# def draw_lives():
#     for i in range(lives):
#         screen.blit(heart_img, (10 + i*35, 10))

# def draw_player():
#     color = YELLOW if any(pygame.Rect(player_pixel_pos[0], player_pixel_pos[1], TILE_SIZE, TILE_SIZE).colliderect(h) for h in hiding_spots) else BLUE
#     pygame.draw.rect(screen, color, pygame.Rect(player_pixel_pos[0], player_pixel_pos[1], TILE_SIZE, TILE_SIZE))

# load_level(current_level)
# clock = pygame.time.Clock()
# running = True

# while running:
#     dt = clock.tick(60)
#     screen.fill(WHITE)
#     dx = dy = 0

#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         if game_state == "menu":
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
#                 game_state = "playing"

#         elif game_state in ["playing", "paused"]:
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
#                 game_state = "paused" if game_state == "playing" else "playing"

#             if game_state == "playing":
#                 if event.type == pygame.KEYDOWN and player_target_pos == player_pos:
#                     px, py = player_pos
#                     if event.key == pygame.K_LEFT: new_pos = (px-1, py)
#                     elif event.key == pygame.K_RIGHT: new_pos = (px+1, py)
#                     elif event.key == pygame.K_UP: new_pos = (px, py-1)
#                     elif event.key == pygame.K_DOWN: new_pos = (px, py+1)
#                     else: new_pos = player_pos

#                     new_rect = pygame.Rect(new_pos[0]*TILE_SIZE, new_pos[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
#                     if new_rect.collidelist(player_walls) == -1:
#                         player_target_pos = new_pos

#         elif game_state == "game_over":
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
#                 lives = 3
#                 current_level = 0
#                 load_level(current_level)
#                 game_state = "menu"

#     if game_state == "playing":
#         # Smooth interpolation of player movement
#         for i in [0, 1]:
#             target_pixel = player_target_pos[i]*TILE_SIZE
#             if player_pixel_pos[i] < target_pixel:
#                 player_pixel_pos[i] += player_speed
#                 if player_pixel_pos[i] > target_pixel:
#                     player_pixel_pos[i] = target_pixel
#             elif player_pixel_pos[i] > target_pixel:
#                 player_pixel_pos[i] -= player_speed
#                 if player_pixel_pos[i] < target_pixel:
#                     player_pixel_pos[i] = target_pixel
#         player_pos = (player_pixel_pos[0]//TILE_SIZE, player_pixel_pos[1]//TILE_SIZE)

#     # Drawing
#     if game_state == "menu":
#         screen.blit(font.render("Maze Game", True, BLACK), (WIDTH//2 - 100, HEIGHT//2 - 40))
#         screen.blit(font.render("Press ENTER to Start", True, BLUE), (WIDTH//2 - 150, HEIGHT//2 + 10))

#     elif game_state == "paused":
#         paused_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
#         paused_overlay.fill((0, 0, 0, 100))
#         screen.blit(paused_overlay, (0, 0))
#         screen.blit(font.render("\u23F8 Paused - Press 'P' to Resume", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 20))

#     elif game_state == "game_over":
#         screen.blit(font.render("Game Over!", True, RED), (WIDTH//2 - 100, HEIGHT//2 - 40))
#         screen.blit(font.render("Press ENTER to return to menu", True, BLACK), (WIDTH//2 - 200, HEIGHT//2 + 10))

#     elif game_state == "playing":
#         for wall in player_walls:
#             pygame.draw.rect(screen, BLACK, wall)
#         for spot in hiding_spots:
#             pygame.draw.rect(screen, GREY, spot)
#         for wall in walls:
#             pygame.draw.rect(screen, (30, 30, 30), wall, 2)
#         draw_player()
#         pygame.draw.rect(screen, GREEN, end_rect)

#         for enemy in enemies:
#             pygame.draw.rect(screen, RED, enemy['rect'])

#         draw_lives()

#         player_rect = pygame.Rect(player_pixel_pos[0], player_pixel_pos[1], TILE_SIZE, TILE_SIZE)
#         if player_rect.colliderect(end_rect):
#             win_sound.play()
#             current_level += 1
#             if current_level >= len(levels):
#                 current_level = 0
#             load_level(current_level)

#     pygame.display.flip()

# pygame.quit()
# sys.exit()
