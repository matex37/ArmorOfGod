import pygame

class Level:
    def __init__(self, level_map, tile_size):
        self.tile_size = tile_size

        self.platforms = []
        self.exit_rect = None
        self.player_start = (0, 0)


        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):

                x = col_index * tile_size
                y = row_index * tile_size

                if tile == "1":
                    self.platforms.append(
                        pygame.Rect(x, y, tile_size, tile_size)
                    )

                elif tile == "P":
                    self.player_start = (x, y)

                elif tile == "D":
                    self.door_rect = pygame.Rect(
                        x, y, tile_size, tile_size
                    )

    def draw(self, screen, camera_x, camera_y):
        # стены
        for platform in self.platforms:
            pygame.draw.rect(
                screen,
                (100, 80, 50),
                platform.move(-camera_x, -camera_y)
            )

        # дверь  пока простая
        if self.door_rect:
            pygame.draw.rect(
                screen,
                (120, 60, 20),
                self.door_rect.move(-camera_x, -camera_y)
            )
