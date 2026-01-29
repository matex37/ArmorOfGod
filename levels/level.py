import pygame
from entities.door import Door
from entities.lever import Lever
#images
wall_image = pygame.image.load("assets/tiles/rock/wall.png")
wall_break = pygame.image.load("assets/tiles/rock/wall_break.png")
cave_bg = pygame.image.load("assets/backgrounds/cave/cave_bg.png")


class Level:
    def __init__(self, level_map, tile_size):
        self.tile_size = tile_size
        self.level_map = level_map
        self.platforms = []
        self.ladders = []
        self.breakable = []
        self.moving = []
        self.door = None
        self.exit_rect = None
        self.lever = None
        self.player_start = (0, 0)
        # стены пещеры
        self.wall_image = wall_image.convert_alpha()
        self.wall_image = pygame.transform.scale(
            self.wall_image, (tile_size, tile_size)
        )
        # разрушаемая плитка
        self.breakable_image = wall_break.convert_alpha()
        self.breakable_image = pygame.transform.scale(
            self.breakable_image, (tile_size, tile_size)
        )
        # фон пещеры
        self.background = cave_bg.convert()
        self.bg_width = self.background.get_width()
        self.bg_height = self.background.get_height()

        for row_index, row in enumerate(level_map):
            for col_index, char in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if char == "#":
                    self.platforms.append(
                        pygame.Rect(x, y, tile_size, tile_size)
                    )

                elif char == "P":
                    self.player_start = (x, y)

                elif char == "D":
                    # дверь стоит НАД клеткой выхода
                    self.door = Door(x, y - tile_size, tile_size)
                    self.exit_rect = pygame.Rect(x, y, tile_size, tile_size)
                elif char == "L":
                    self.ladders.append(
                        pygame.Rect(x, y, tile_size, tile_size)
                    )
                elif char == "S":
                    self.lever = Lever(x, y + tile_size // 2, tile_size)
                elif char == "B":
                    self.breakable.append(pygame.Rect(x, y, tile_size, tile_size))
                elif char == "M":
                    self.moving.append({
                        "rect": pygame.Rect(x, y, tile_size, tile_size),
                        "dir": 1
                    })

    def update(self):
        if self.door:
            self.door.update()
        # движущиеся платформы
        for p in self.moving:
            p["rect"].x += p["dir"] * 2
            if p["rect"].left < 0 or p["rect"].right > 2000:
                p["dir"] *= -1
    def draw(self, screen, camera_x, camera_y):
        #  фон пещеры
        bg_x = -camera_x * 0.3
        bg_y = -camera_y * 0.3
        # сколько фонов нужно по X и Y, чтобы покрыть экран
        screen_width, screen_height = screen.get_size()
        x_repeat = (screen_width // self.bg_width) + 2
        y_repeat = (screen_height // self.bg_height) + 2

        for x in range(x_repeat):
            for y in range(y_repeat):
                screen.blit(
                    self.background,
                    (bg_x + x * self.bg_width, bg_y + y * self.bg_height)
                )
        # рисуем платформы
        for platform in self.platforms:
            screen.blit(
                self.wall_image,
                (platform.x - camera_x, platform.y - camera_y)
            )
        # дверь
        if self.door:
            self.door.draw(screen, camera_x, camera_y)
        # рычаг
        if self.lever:
            self.lever.draw(screen, camera_x, camera_y)

