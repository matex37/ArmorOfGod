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
        self.on_ladder = False

        # состояние и анимация
        self.state = "idle"
        self.prev_state = self.state
        self.facing = "right"
        self.anim_frame = 0
        self.anim_speed = 0.15

        self.attacking = True
        self.attack_hit = False
        
        self.attack_rect = None
        self.attack_timer = 0
        self.attack_duration = 150
        self.attack_cooldown = 300
        self.attacking = False
        self.attack_hit = False
        self.attack_done = False



        self.animations = {
            "idle": self.load_images("assets/player/idle"),
            "run": self.load_images("assets/player/run"),
            "jump": self.load_images("assets/player/jump"),
            "attack": self.load_images("assets/player/attack"),
            "slide": self.load_images("assets/player/slide"),
        }

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

    # ---------- INPUT ----------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed

        # прыжок ТОЛЬКО если не на лестнице
        if keys[pygame.K_SPACE] and self.on_ground and not self.on_ladder:
            self.velocity_y = self.jump_power
            self.on_ground = False

    # ---------- LADDER ----------
    def handle_ladder(self, ladders):
        keys = pygame.key.get_pressed()
        ladder_hit = None

        for ladder in ladders:
            if self.rect.colliderect(ladder):
                ladder_hit = ladder
                break

        # вход на лестницу
        if ladder_hit and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.on_ladder = True
            self.velocity_y = 0

        if self.on_ladder:
            self.velocity_y = 0  # отключаем гравитацию

            if keys[pygame.K_UP]:
                self.rect.y -= self.speed
            elif keys[pygame.K_DOWN]:
                self.rect.y += self.speed

            # спрыгивание
            if keys[pygame.K_SPACE]:
                self.on_ladder = False
                self.velocity_y = self.jump_power

            # выход, если лестницы больше нет
            if not ladder_hit:
                self.on_ladder = False

    # ---------- PHYSICS ----------
    def apply_gravity(self):
        if not self.on_ladder:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

    def move_x(self, platforms):
        self.rect.x += self.velocity_x
        for p in platforms:
            if self.rect.colliderect(p):
                if self.velocity_x > 0:
                    self.rect.right = p.left
                elif self.velocity_x < 0:
                    self.rect.left = p.right

    def move_y(self, platforms):
        self.on_ground = False
        if self.on_ladder:
            return

        for p in platforms:
            if self.rect.colliderect(p):
                if self.velocity_y > 0:
                    self.rect.bottom = p.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = p.bottom
                    self.velocity_y = 0

    # ---------- UPDATE ----------
    def update(self, platforms, ladders):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if keys[pygame.K_RALT] and not self.attacking:
            self.attack_done = False
            self.attacking = True
            self.attack_timer = now

        if self.attacking and now - self.attack_timer > self.attack_cooldown:
            self.attacking = False
        self.handle_input()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RALT] and not self.attacking:
            self.attack_done = False
            self.attacking = True
            self.attack_timer = pygame.time.get_ticks()
        self.handle_ladder(ladders)
        self.move_x(platforms)
        self.apply_gravity()
        self.move_y(platforms)
        self.update_state()
        self.update_animation()


    # ---------- STATE ----------
    def update_state(self):
        keys = pygame.key.get_pressed()

        # ===== АТАКА ИМЕЕТ ПРИОРИТЕТ =====
        if self.attacking:
            self.state = "attack"

        elif self.on_ladder:
            self.state = "idle"

        elif not self.on_ground:
            self.state = "jump"

        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.state = "run"

        else:
            self.state = "idle"

        # направление
        if keys[pygame.K_LEFT]:
            self.facing = "left"
        elif keys[pygame.K_RIGHT]:
            self.facing = "right"

        # сброс анимации при смене состояния
        if self.state != self.prev_state:
            self.anim_frame = 0
            self.prev_state = self.state

    # ---------- ANIMATION ----------
    def update_animation(self):
        frames = self.animations.get(self.state, [])
        if not frames:
            return

        self.anim_frame += self.anim_speed

        # Если это атака — не зацикливаем
        if self.state == "attack":
            if self.anim_frame >= len(frames):
                self.anim_frame = 0
                self.attacking = False
                self.state = "idle"
        else:
            self.anim_frame %= len(frames)

    # ---------- DRAW ----------
    def draw(self, screen, camera_x, camera_y):
        frames = self.animations.get(self.state, [])
        x, y = self.rect.x - camera_x, self.rect.y - camera_y

        if frames:
            img = frames[int(self.anim_frame)]
            if self.facing == "left":
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (x, y))
        else:
            pygame.draw.rect(screen, self.color, (x, y, self.rect.width, self.rect.height))

    def get_attack_rect(self):
        if not self.attacking:
            self.attacking = True
            self.anim_frame = 0
            self.attack_done = False

        offset = 40 if self.facing == "right" else -40

        return pygame.Rect(
            self.rect.centerx + offset,
            self.rect.y + 10,
            40,
            self.rect.height - 20
        )



