import pygame
from entities.door import Door
from entities.lever import Lever

class Level:
    def __init__(self, level_map, tile_size):
        self.tile_size = tile_size
        self.platforms = []
        self.ladders = []
        self.door = None
        self.exit_rect = None
        self.lever = None
        self.player_start = (0, 0)

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
    def update(self):
        if self.door:
            self.door.update()
    def draw(self, screen, camera_x, camera_y):
        for platform in self.platforms:
            pygame.draw.rect(
                screen,
                (90, 80, 60),
                pygame.Rect(
                    platform.x - camera_x,
                    platform.y - camera_y,
                    platform.width,
                    platform.height
                )
            )
        # дверь
        if self.door:
            self.door.draw(screen, camera_x, camera_y)
        # рычаг
        if self.lever:
            self.lever.draw(screen, camera_x, camera_y)

