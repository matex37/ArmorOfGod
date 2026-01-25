import pygame
import sys
from settings import *
from entities.player import Player
from levels.loader import load_level
from levels.level import Level

TILE_SIZE = 48
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"  # MENU | PLAY
        self.score = 0
        self.font = pygame.font.SysFont("arial", 24)
        self.camera_x = 0
        self.camera_y = 0
        self.level_completed = False

        # Загружаем уровень
        level_map = load_level("levels/maps/level_01.txt")
        self.level = Level(level_map, TILE_SIZE)

        # Создаём игрока
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)

        # Генерация объектов уровня
        self.spikes = []
        self.treasures = []
        self.ladders = []

        for y, row in enumerate(level_map):
            for x, cell in enumerate(row):
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE

                if cell == "^":
                    self.spikes.append(pygame.Rect(world_x, world_y + TILE_SIZE - 5, TILE_SIZE, 5))
                elif cell == "T":
                    self.treasures.append(pygame.Rect(world_x + 14, world_y + 14, 20, 20))
                elif cell == "L":
                    self.ladders.append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))

    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "PLAY":
                self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    # ------------------ События ------------------ #
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.start_game()

    def start_game(self):
        self.state = "PLAY"
        self.score = 0
        self.level_completed = False
        self.player.rect.topleft = self.level.player_start
        self.player.velocity_x = 0
        self.player.velocity_y = 0

    # ------------------ Камера ------------------ #
    def update_camera(self):
        self.camera_x = max(self.player.rect.centerx - WIDTH // 2, 0)
        self.camera_y = max(self.player.rect.centery - HEIGHT // 2, 0)

    def apply_camera(self, rect):
        return pygame.Rect(
            rect.x - self.camera_x,
            rect.y - self.camera_y,
            rect.width,
            rect.height
        )

    # ------------------ Логика игры ------------------ #
    def update(self):
        self.player.update(self.level.platforms, self.level.ladders)
        self.level.update()
        self.update_camera()
        self.check_death()
        self.check_treasure()
        self.check_door()

    def check_door(self):
        if self.level.door and self.player.rect.colliderect(self.level.door.rect):
            self.level.door.open()
        if (
            not self.level_completed
            and self.level.door
            and self.level.door.state == "OPEN"
            and self.player.rect.colliderect(self.level.exit_rect)
        ):
            self.level_completed = True
            print("LEVEL COMPLETE")

    def check_death(self):
        if any(self.player.rect.colliderect(spike) for spike in self.spikes):
            self.respawn()

    def check_treasure(self):
        for treasure in self.treasures[:]:
            if self.player.rect.colliderect(treasure):
                self.treasures.remove(treasure)
                self.score += 1

    def respawn(self):
        print("☠ Герой погиб")
        self.player.rect.topleft = self.level.player_start
        self.player.velocity_x = 0
        self.player.velocity_y = 0

    # ------------------ Рендер ------------------ #
    def draw(self):
        self.screen.fill((15, 15, 20))

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "PLAY":
            self.draw_game()

        pygame.display.flip()

    def draw_menu(self):
        title = self.font.render("ARMOR OF GOD", True, (255, 215, 0))
        start = self.font.render("Press ENTER to start", True, (200, 200, 200))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
        self.screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 260))

    def draw_game(self):
        self.level.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Рисуем сокровища
        for treasure in self.treasures:
            pygame.draw.rect(self.screen, (255, 215, 0), self.apply_camera(treasure))

        # Рисуем шипы
        for spike in self.spikes:
            pygame.draw.rect(self.screen, (255, 255, 255), self.apply_camera(spike))

        # Рисуем лестницы
        for ladder in self.ladders:
            pygame.draw.rect(self.screen, (255, 255, 255), self.apply_camera(ladder))

        # HUD
        self.draw_hud()

    def draw_hud(self):
        text = self.font.render(f"Treasure: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
