import pygame


class MovementController:
    def __init__(self, player):
        self.player = player
        self.speed = 5
        self.gravity = 0.8
        self.jump_power = -15

    def update(self, platforms, ladders):
        self.handle_input()
        self.handle_ladder(ladders)
        self.move_x(platforms)
        self.apply_gravity()
        self.move_y(platforms)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.velocity_x = 0

        if keys[pygame.K_LEFT]:
            self.player.velocity_x = -self.speed
            self.player.facing = "left"

        if keys[pygame.K_RIGHT]:
            self.player.velocity_x = self.speed
            self.player.facing = "right"

        if keys[pygame.K_SPACE] and self.player.on_ground and not self.player.on_ladder:
            self.player.velocity_y = self.jump_power
            self.player.on_ground = False

    def handle_ladder(self, ladders):
        keys = pygame.key.get_pressed()
        ladder_hit = None

        for ladder in ladders:
            if self.player.rect.colliderect(ladder):
                ladder_hit = ladder
                break

        if ladder_hit and (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.player.on_ladder = True
            self.player.velocity_y = 0

        if self.player.on_ladder:
            self.player.velocity_y = 0

            if keys[pygame.K_UP]:
                self.player.rect.y -= self.speed
            elif keys[pygame.K_DOWN]:
                self.player.rect.y += self.speed

            if not ladder_hit:
                self.player.on_ladder = False

    def apply_gravity(self):
        if not self.player.on_ladder:
            self.player.velocity_y += self.gravity
            self.player.rect.y += self.player.velocity_y

    def move_x(self, platforms):
        self.player.rect.x += self.player.velocity_x
        for p in platforms:
            if self.player.rect.colliderect(p):
                if self.player.velocity_x > 0:
                    self.player.rect.right = p.left
                elif self.player.velocity_x < 0:
                    self.player.rect.left = p.right

    def move_y(self, platforms):
        if self.player.on_ladder:
            return

        self.player.on_ground = False

        for p in platforms:
            if self.player.rect.colliderect(p):
                if self.player.velocity_y > 0:
                    self.player.rect.bottom = p.top
                    self.player.velocity_y = 0
                    self.player.on_ground = True
                elif self.player.velocity_y < 0:
                    self.player.rect.top = p.bottom
                    self.player.velocity_y = 0