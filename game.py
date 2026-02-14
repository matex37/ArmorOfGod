import pygame
import sys
from settings import *
from entities.player import Player
from levels.loader import load_level
from levels.level import Level
from levels.levels_list import LEVEL_FILES  # список уровней
from entities.enemy import Enemy
TILE_SIZE = 48

# Загружаем изображение лестницы
ladder_img = pygame.image.load("assets/tiles/ladder/ladder_01.png")
SPIKE_RAW_FRAMES = [
    pygame.image.load(f"assets/tiles/spikes/spike_{i}.png")
    for i in range(1, 5)
]

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


        # Список уровней
        self.level_files = LEVEL_FILES
        self.level_index = 0

        # Создаём игрока
        self.player = Player(0, 0)

        # Лестница
        self.ladder_img = ladder_img.convert_alpha()
        self.ladder_img = pygame.transform.scale(self.ladder_img, (TILE_SIZE, TILE_SIZE))

        # шипы
        self.spike_frames = [
            pygame.transform.scale(img.convert_alpha(), (TILE_SIZE, TILE_SIZE))
            for img in SPIKE_RAW_FRAMES
        ]

        self.spike_anim_index = 0
        self.spike_anim_timer = 0


        # Загрузка первого уровня
        self.load_level()

    # ------------------ Загрузка и генерация уровня ------------------ #
    def load_level(self):
        """Загружаем карту уровня и создаём объекты"""
        level_map = load_level(self.level_files[self.level_index])
        self.level = Level(level_map, TILE_SIZE)
        self.player.rect.topleft = self.level.player_start
        self.generate_level_objects()

    def generate_level_objects(self):
        """Создание шипов, сокровищ и лестниц по карте уровня"""
        self.spikes = []
        self.treasures = []
        self.ladders = []
        self.level.enemies = []  # очищаем список врагов для уровня

        # В твоём Level атрибут с картой называется level_map
        level_map = self.level.level_map

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
                elif cell == "E":  # например, E = Enemy
                    enemy = Enemy(world_x, world_y)
                    self.level.enemies.append(enemy)

    def next_level(self):
        self.level_index += 1
        if self.level_index >= len(self.level_files):
            print("GAME COMPLETE")
            self.running = False
            return
        self.load_level()
        self.level_completed = False
        self.score = 0

    # ------------------ Главный цикл ------------------ #
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
        # ===== АТАКА ЧЕРЕЗ КАДР АНИМАЦИИ =====
        if self.player.attacking and not self.player.attack_done:

            frame_index = int(self.player.anim_frame)

            # удар происходит на 2 кадре анимации
            if frame_index == 1:

                hitbox = self.player.get_attack_rect()

                if hitbox:
                    for enemy in self.level.enemies:
                        if enemy.alive and hitbox.colliderect(enemy.rect):
                            enemy.take_damage(1)

                # чтобы удар не повторялся в этом же кадре
                self.player.attack_done = True
        self.level.update()
        self.level.player_rect = self.player.rect
        self.update_camera()
        self.check_death()
        self.check_treasure()
        self.check_door()


        #обновляем врагов через список уровня:
        for enemy in self.level.enemies:
            enemy.update(self.level.platforms, self.player)


        #анимация шипов
        self.spike_anim_timer += 1
        if self.spike_anim_timer >= 8:
            self.spike_anim_timer = 0
            self.spike_anim_index = (self.spike_anim_index + 1) % len(self.spike_frames)

        # Разрушаемые платформы (таймер)
        for b in self.level.breakable:
            if self.player.rect.colliderect(b):
                if self.player.velocity_y > 0 and self.player.rect.bottom - self.player.velocity_y <= b.top:
                    self.player.rect.bottom = b.top
                    self.player.velocity_y = 0
                    self.player.on_ground = True

                    # ⏱ запуск таймера ОДИН раз
                    bid = id(b)
                    now = pygame.time.get_ticks()
                    if bid not in self.level.break_timers:
                        self.level.break_timers[bid] = now
                    else:
                        self.level.break_timers[bid] += 500


        # Проверка выхода
        if (
            self.level.door
            and self.level.door.state == "OPEN"
            and self.player.rect.colliderect(self.level.exit_rect)
        ):
            self.next_level()

        for enemy in self.level.enemies:
            enemy.update(self.level.platforms, self.player)
        for enemy in self.level.enemies:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):

                # прыжок сверху — враг умирает
                if self.player.velocity_y > 0 and \
                        self.player.rect.bottom - enemy.rect.top < 20:
                    enemy.alive = False
                    self.player.velocity_y = -10
                else:
                    self.respawn()

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
        # Рисуем уровень
        self.level.draw(self.screen, self.camera_x, self.camera_y)

        # Рисуем врага
        for enemy in self.level.enemies:
            enemy.draw(self.screen, self.camera_x, self.camera_y)

        # Рисуем сокровища
        for treasure in self.treasures:
            pygame.draw.rect(self.screen, (255, 215, 0), self.apply_camera(treasure))

        # Рисуем шипы
        frame = self.spike_frames[self.spike_anim_index]

        for spike in self.spikes:
            r = self.apply_camera(spike)
            self.screen.blit(frame, (r.x, r.y - TILE_SIZE + 5))

        # Рисуем лестницы
        for ladder in self.ladders:
            rect = self.apply_camera(ladder)
            self.screen.blit(self.ladder_img, (rect.x, rect.y))

        # Рисуем игрока поверх лестниц
        self.player.draw(self.screen, self.camera_x, self.camera_y)

        # Разрушаемые платформы
        for b in self.level.breakable:
            rect = self.apply_camera(b)
            self.screen.blit(self.level.breakable_image, (rect.x, rect.y))

        # Движущиеся платформы
        for p in self.level.moving:
            pygame.draw.rect(self.screen, (120, 160, 200), self.apply_camera(p["rect"]))



        # HUD
        self.draw_hud()

    def draw_hud(self):
        text = self.font.render(f"Treasure: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

