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

    def move(self, platforms):
        if not self.on_ground:
            return

        # двигаем врага
        self.rect.x += self.speed * self.direction

        # создаём "ножку" впереди, чтобы проверить есть ли платформа
        feet_x = self.rect.centerx + (self.rect.width // 2 + 1) * self.direction
        feet_y = self.rect.bottom + 1
        on_platform_ahead = False

        check_rect = pygame.Rect(feet_x, feet_y, 2, 2)
        for plat in platforms:
            if check_rect.colliderect(plat):
                on_platform_ahead = True
                break

        # проверка стены перед врагом
        hit_wall = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                hit_wall = True
                break

        # если впереди края нет или стена — разворачиваемся
        if not on_platform_ahead or hit_wall:
            self.direction *= -1

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

    def update(self, platforms):
        if not self.alive:
            return

        self.apply_gravity()
        self.move(platforms)
        self.check_collisions(platforms)
        self.animate()

    def draw(self, screen, cam_x, cam_y):
        if self.alive:
            screen.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

