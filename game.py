import pygame
import sys
from settings import *
from entities.player import Player
from levels.level import Level
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
        self.door_opened = False

        # загружаем уровень
        level_map = load_level("levels/maps/level_01.txt")
        self.level = Level(level_map, TILE_SIZE)
        self.platforms = self.level.platforms

        # создаём игрока
        start_x, start_y = self.level.player_start
        self.player = Player(start_x, start_y)

        # шипы опасные зоны
        self.spikes = [
            pygame.Rect(350, HEIGHT - 20, 40, 10),
            pygame.Rect(540, 280, 40, 10),
        ]

        # сокровища
        self.treasures = [
            pygame.Rect(415, 50, 20, 20),
        ]

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
# Меню клавиша
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.start_game()

    def start_game(self):
        self.state = "PLAY"
        self.score = 0
        self.player.rect.topleft = (100, 100)

        # self.treasures = [
        #     pygame.Rect(320, 160, 30, 30),
        # ]

    def update_camera(self):
        self.camera_x = self.player.rect.centerx - WIDTH // 2
        self.camera_y = self.player.rect.centery - HEIGHT // 2

        # Не даём камере уйти в минус
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_y < 0:
            self.camera_y = 0

    def update(self):
        if self.state == "PLAY":
            self.player.update(self.platforms)
            self.update_camera()
            self.check_death()
            self.check_treasure()
        if (
                not self.level_completed
                and self.level.exit_rect
                and self.player.rect.colliderect(self.level.exit_rect)
        ):
            self.level_completed = True
            print("LEVEL COMPLETE")

        if (
                not self.door_opened
                and self.level.door_rect
                and self.player.rect.colliderect(self.level.door_rect)
        ):
            self.door_opened = True
            print("DOOR OPENED")
        if (
                self.level.exit_rect
                and self.player.rect.colliderect(self.level.exit_rect)
        ):
            print("LEVEL COMPLETE")

    def apply_camera(self, rect):
        return pygame.Rect(
            rect.x - self.camera_x,
            rect.y - self.camera_y,
            rect.width,
            rect.height
        )


    def draw_hud(self):
        text = self.font.render(f"Treasure: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

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
        for platform in self.platforms:
            pygame.draw.rect(
                self.screen,
                (90, 80, 60),
                self.apply_camera(platform)
            )

        for spike in self.spikes:
            pygame.draw.rect(
                self.screen,
                (200, 200, 200),
                self.apply_camera(spike)
            )

        for treasure in self.treasures:
            pygame.draw.rect(
                self.screen,
                (255, 215, 0),
                self.apply_camera(treasure)
            )
        self.level.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        self.draw_hud()

    def check_death(self):
        for spike in self.spikes:
            if self.player.rect.colliderect(spike):
                self.respawn()
    #сбор сокровищ
    def check_treasure(self):
        for treasure in self.treasures[:]:
            if self.player.rect.colliderect(treasure):
                self.treasures.remove(treasure)
                self.score += 1

    def respawn(self):
        print("☠ Герой погиб")
        self.player.rect.topleft = (100, 100)
        self.player.velocity_x = 0
        self.player.velocity_y = 0

