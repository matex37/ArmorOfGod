import pygame


class AttackController:
    def __init__(self, player):
        self.player = player
        self.attacking = False
        self.attack_done = False
        self.attack_timer = 0
        self.attack_cooldown = 300

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RALT] and not self.attacking:
            now = pygame.time.get_ticks()

            if now - self.attack_timer >= self.attack_cooldown:
                self.attacking = True
                self.attack_done = False
                self.attack_timer = now
                self.player.animation.reset()

        if self.attacking and self.player.animation.finished():
            self.attacking = False

    def get_hitbox(self):
        if not self.attacking:
            return None

        offset = 40 if self.player.facing == "right" else -40

        return pygame.Rect(
            self.player.rect.centerx + offset,
            self.player.rect.y + 10,
            40,
            self.player.rect.height - 20
        )