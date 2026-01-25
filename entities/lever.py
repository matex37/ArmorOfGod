import pygame

class Lever:
    def __init__(self, x, y, size):
        self.size = size
        self.rect = pygame.Rect(x, y, size, size // 2)

        self.state = "IDLE"   # IDLE | ACTIVATING | ON
        self.frame = 0
        self.anim_speed = 0.2

        # ⚙️ "кадры" анимации (угол наклона)
        self.frames = [0, 10, 20, 30, 40]

    def activate(self):
        if self.state == "IDLE":
            self.state = "ACTIVATING"
            self.frame = 0
            print("LEVER ACTIVATING")

    def update(self):
        if self.state == "ACTIVATING":
            self.frame += self.anim_speed
            if int(self.frame) >= len(self.frames):
                self.state = "ON"
                self.frame = len(self.frames) - 1
                print("LEVER ON")

    def draw(self, screen, camera_x, camera_y):
        angle = self.frames[int(self.frame)]

        base_rect = pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        )

        # основание
        pygame.draw.rect(screen, (80, 80, 80), base_rect)

        # "ручка" рычага
        handle_length = self.size
        handle_x = base_rect.centerx
        handle_y = base_rect.top

        end_x = handle_x + handle_length * pygame.math.Vector2(1, 0).rotate(-angle).x
        end_y = handle_y + handle_length * pygame.math.Vector2(1, 0).rotate(-angle).y

        pygame.draw.line(
            screen,
            (220, 220, 0),
            (handle_x, handle_y),
            (end_x, end_y),
            4
        )

