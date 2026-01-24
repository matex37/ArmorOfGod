import pygame

class Door:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size * 2)
        self.state = "CLOSED"  # CLOSED | OPENING | OPEN
        self.open_progress = 0  # 0..1

    def open(self):
        if self.state == "CLOSED":
            self.state = "OPENING"

    def update(self):
        if self.state == "OPENING":
            self.open_progress += 0.02
            if self.open_progress >= 1:
                self.open_progress = 1
                self.state = "OPEN"

    def draw(self, screen, camera_x, camera_y):
        height = int(self.rect.height * (1 - self.open_progress))
        if height > 0:
            door_rect = pygame.Rect(
                self.rect.x - camera_x,
                self.rect.y - camera_y,
                self.rect.width,
                height
            )
            pygame.draw.rect(screen, (120, 80, 40), door_rect)
