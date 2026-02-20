import pygame
import os

TILE_SIZE = 48

class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # === Состояние ===
        self.state = "idle"
        self.frame = 0
        self.anim_speed = 0.15
        self.alive = True
        self.dying = False

        # === Движение ===
        self.direction = 1
        self.speed = 1
        self.velocity_y = 0
        self.on_ground = False

        # === Бой ===
        self.max_hp = 3
        self.hp = self.max_hp
        self.knockback = 0
        self.attack_range = 60
        self.attack_cooldown = 800
        self.last_attack_time = 0

        # === Анимации ===
        self.animations = {
            "idle": self.load_images("assets/enemies/idle"),
            "jump": self.load_images("assets/enemies/jump"),
            "attack": self.load_images("assets/enemies/attack"),
        }

        self.image = self.animations["idle"][0] if self.animations["idle"] else pygame.Surface((45, 60))
        self.rect = self.image.get_rect(topleft=(x, y))

    # =========================

    def load_images(self, folder):
        images = []
        if not os.path.exists(folder):
            return images

        for file in sorted(os.listdir(folder)):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join(folder, file)).convert_alpha()
                img = pygame.transform.scale(img, (45, 60))
                images.append(img)

        return images

    # =========================

    def apply_gravity(self):
        self.velocity_y += 0.5
        self.velocity_y = min(self.velocity_y, 10)
        self.rect.y += self.velocity_y

    # =========================

    def decide_state(self, player):
        distance = abs(player.rect.centerx - self.rect.centerx)

        # смотрим на игрока
        self.direction = -1 if player.rect.centerx < self.rect.centerx else 1

        if distance < self.attack_range:
            if self.state != "attack":
                self.state = "attack"
                self.frame = 0
            return

        if self.state != "attack":
            self.state = "idle"

    # =========================

    def move(self, platforms):
        if self.state == "attack":
            return

        self.rect.x += self.speed * self.direction

        # проверка стены
        wall_rect = self.rect.move(self.direction * 2, 0)
        if any(wall_rect.colliderect(p) for p in platforms):
            self.direction *= -1

    # =========================

    def check_collisions(self, platforms):
        self.on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.velocity_y >= 0:
                    self.rect.bottom = plat.top
                    self.velocity_y = 0
                    self.on_ground = True

    # =========================

    def handle_attack(self, player):
        if self.state != "attack":
            return

        if int(self.frame) == 2:
            now = pygame.time.get_ticks()
            if now - self.last_attack_time > self.attack_cooldown:

                attack_rect = pygame.Rect(
                    self.rect.centerx + self.direction * 40,
                    self.rect.y + 10,
                    40, 40
                )

                if attack_rect.colliderect(player.rect):
                    if hasattr(player, "take_damage"):
                        player.take_damage(1)

                self.last_attack_time = now

    # =========================

    def animate(self):
        if not self.animations[self.state]:
            return

        self.frame += self.anim_speed

        if self.frame >= len(self.animations[self.state]):
            if self.state == "attack":
                self.state = "idle"
            self.frame = 0

        image = self.animations[self.state][int(self.frame)]

        # 👇 ВАЖНО — поворот
        if self.direction == -1:
            image = pygame.transform.flip(image, True, False)

        self.image = image

    # =========================

    def update(self, platforms, player):

        if not self.alive:
            return

        # knockback
        if self.knockback != 0:
            self.rect.x += self.knockback
            self.knockback *= 0.8
            if abs(self.knockback) < 0.5:
                self.knockback = 0

        self.apply_gravity()
        self.check_collisions(platforms)

        self.decide_state(player)
        self.move(platforms)

        self.handle_attack(player)
        self.animate()

    # =========================

    def take_damage(self, amount):
        if not self.alive:
            return

        self.hp -= amount
        self.knockback = -10 if self.direction == 1 else 10

        if self.hp <= 0:
            self.alive = False

    # =========================

    def draw(self, screen, cam_x, cam_y):
        if self.alive:
            screen.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))