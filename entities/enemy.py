import pygame
import os

TILE_SIZE = 48  # можно поменять под твой размер тайла

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.state = "idle"
        self.frame = 0
        self.anim_speed = 0.15
        self.alive = True

        # движение
        self.direction = 1  # 1 = вправо, -1 = влево
        self.speed = 1
        self.velocity_y = 0
        self.on_ground = False

        # Анимации
        self.animations = {
            "idle": self.load_images("assets/enemies/idle"),
            "jump": self.load_images("assets/enemies/jump"),
            "attack": self.load_images("assets/enemies/attack"),
        }

        # Если нет картинок, создаём пустой спрайт
        if self.animations[self.state]:
            self.image = self.animations[self.state][0]
        else:
            self.image = pygame.Surface((45, 60))
            self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect(topleft=(x, y))

        self.hp = 3
        self.alive = True
        self.dying = False
        self.knockback = 0
        self.max_hp = 3
        self.hp = self.max_hp
        self.hit_cooldown = 300  # мс
        self.last_hit_time = 0

        self.dying = False
        self.death_timer = 0
        self.DEATH_DELAY = 300  # миллисекунды

        self.knockback = 0
        self.hit_flash_timer = 0

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

    def apply_gravity(self):
        """Простая гравитация"""
        self.velocity_y += 0.5  # сила гравитации
        if self.velocity_y > 10:
            self.velocity_y = 10
        self.rect.y += self.velocity_y

    def move(self, platforms, player):
        # двигаем врага по горизонтали всегда
        self.rect.x += self.speed * self.direction

        # проверяем, есть ли платформа впереди (чуть ниже ног)
        feet_x = self.rect.centerx + (self.rect.width // 2) * self.direction
        feet_y = self.rect.bottom + 5  # смещаем проверку вниз, чтобы точно поймать платформу
        check_rect = pygame.Rect(feet_x, feet_y, 2, 2)
        on_platform_ahead = any(check_rect.colliderect(p) for p in platforms)

        # проверка стены
        wall_rect = self.rect.move(self.direction * 2, 0)
        hit_wall = any(wall_rect.colliderect(p) for p in platforms)

        # если впереди нет платформы или стена — разворачиваемся
        if not on_platform_ahead or hit_wall:
            self.direction *= -1

        if self.state == "attack":
            return

        if self.state == "attack" and int(self.frame) == 2:
            attack_rect = pygame.Rect(
                self.rect.centerx + self.direction * 40,
                self.rect.y + 10,
                40, 40
            )
            if attack_rect.colliderect(player.rect):
                player.take_damage()

        if player.rect.centerx < self.rect.centerx:
            self.direction = -1
        else:
            self.direction = 1

    def check_collisions(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                # Если враг падает или стоит на платформе
                if self.velocity_y >= 0:
                    # ставим врага на верх платформы
                    self.rect.bottom = plat.top
                    self.velocity_y = 0
                    self.on_ground = True

    def animate(self):
        """Анимация врага"""
        self.frame += self.anim_speed
        if self.animations[self.state]:
            if self.frame >= len(self.animations[self.state]):
                self.frame = 0
            self.image = self.animations[self.state][int(self.frame)]

    def update(self, platforms, player):
        if not self.alive:
            return

        # 💥 отбрасывание
        if self.knockback != 0:
            self.rect.x += self.knockback
            self.knockback *= 0.8
            if abs(self.knockback) < 0.5:
                self.knockback = 0

        if self.dying:
            self.alive = False
            return

        self.apply_gravity()
        self.check_collisions(platforms)
        self.move(platforms, player)
        self.animate()

    def take_damage(self, amount):
        if not self.alive or self.dying:
            return

        self.hp -= amount
        print("ENEMY HP:", self.hp)

        # 💥 отбрасывание
        self.knockback = -10 if self.direction == 1 else 10
        self.hit_flash_timer = pygame.time.get_ticks()

        if self.hp <= 0:
            self.dying = True

    def draw(self, screen, cam_x, cam_y):
        if self.alive:
            screen.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

