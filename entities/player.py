import pygame
import os

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = (200, 50, 50)

        # движение
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0

        # физика
        self.gravity = 0.8
        self.jump_power = -15
        self.on_ground = False
        self.on_ladder = False  # новый флаг для лестницы
        self.state = "idle"  # idle | run | jump | attack
        self.facing = "right"
        self.anim_frame = 0
        self.anim_speed = 0.15
        self.prev_state = self.state
        self.sliding = False

        self.animations = {
            "idle": self.load_images("assets/player/idle"),
            "run": self.load_images("assets/player/run"),
            "jump": self.load_images("assets/player/jump"),
            "attack": self.load_images("assets/player/attack"),
            "slide": self.load_images("assets/player/slide"),
        }

    def load_images(self, folder):
        images = []
        for file in sorted(os.listdir(folder)):
            if file.endswith(".png"):
                path = os.path.join(folder, file)
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (35, 55))
                images.append(image)
        return images

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        self.sliding = False
        # движение влево/вправо
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
        # прыжок
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
        # скольжение
        if keys[pygame.K_DOWN] and self.on_ground and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.sliding = True
            self.velocity_x *= 0.5  # ускоряем скольжение

    def move_x(self, platforms):
        self.rect.x += self.velocity_x

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_x > 0:
                    self.rect.right = platform.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.right

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def move_y(self, platforms):
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:  # падаем
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # бьёмся головой
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

    def update(self, platforms, ladders):
        self.handle_input()
        self.handle_ladder(ladders)   # проверка лестницы до движения
        self.move_x(platforms)
        if not self.on_ladder:        # гравитация только если не на лестнице
            self.apply_gravity()
        self.move_y(platforms)
        self.update_state()
        self.update_animation()

    def update_state(self):
        keys = pygame.key.get_pressed()

        if not self.on_ground:
            self.state = "jump"
        elif self.sliding:  # проверяем скольжение раньше, чем run
            self.state = "slide"
        elif keys[pygame.K_f]:
            self.state = "attack"
        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.state = "run"
        else:
            self.state = "idle"

        if keys[pygame.K_LEFT]:
            self.facing = "left"
        elif keys[pygame.K_RIGHT]:
            self.facing = "right"

        if self.state != self.prev_state:
            self.anim_frame = 0
            self.prev_state = self.state

    def update_animation(self):
        frames = self.animations.get(self.state, [])

        if not frames:
            return

        self.anim_frame += self.anim_speed
        if self.anim_frame >= len(frames):
            self.anim_frame = 0

    def draw(self, screen, camera_x, camera_y):
        frames = self.animations.get(self.state, [])

        if not frames:
            # ВРЕМЕННАЯ защита: рисуем прямоугольник
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                pygame.Rect(
                    self.rect.x - camera_x,
                    self.rect.y - camera_y,
                    self.rect.width,
                    self.rect.height
                )
            )
            return

        frame_index = int(self.anim_frame) % len(frames)
        image = frames[frame_index]

        if self.facing == "left":
            image = pygame.transform.flip(image, True, False)

        screen.blit(
            image,
            (self.rect.x - camera_x, self.rect.y - camera_y)
        )

    def handle_ladder(self, ladders):
        keys = pygame.key.get_pressed()
        self.on_ladder = False

        player_center = self.rect.center

        for ladder in ladders:
            if ladder.collidepoint(player_center):
                self.on_ladder = True
                break

        if self.on_ladder:
            self.velocity_y = 0
            self.gravity = 0

            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            elif keys[pygame.K_DOWN]:
                self.rect.y += self.speed
        else:
            self.gravity = 0.8


