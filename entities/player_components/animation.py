import pygame
import os


class AnimationController:
    def __init__(self, player):
        self.player = player
        self.anim_frame = 0
        self.anim_speed = 0.15

        self.animations = {
            "idle": self.load("assets/player/idle"),
            "run": self.load("assets/player/run"),
            "jump": self.load("assets/player/jump"),
            "attack": self.load("assets/player/attack"),
        }

    def load(self, folder):
        images = []
        if not os.path.exists(folder):
            return images

        for file in sorted(os.listdir(folder)):
            if file.endswith(".png"):
                img = pygame.image.load(os.path.join(folder, file)).convert_alpha()
                img = pygame.transform.scale(img, (45, 60))
                images.append(img)

        return images

    def update(self):
        frames = self.animations.get(self.player.state, [])
        if not frames:
            return

        self.anim_frame += self.anim_speed

        if self.anim_frame >= len(frames):
            self.anim_frame = 0

    def draw(self, screen, camera_x, camera_y):
        frames = self.animations.get(self.player.state, [])
        if not frames:
            return

        img = frames[int(self.anim_frame)]

        if self.player.facing == "left":
            img = pygame.transform.flip(img, True, False)

        screen.blit(img, (
            self.player.rect.x - camera_x,
            self.player.rect.y - camera_y
        ))

    def reset(self):
        self.anim_frame = 0

    def finished(self):
        frames = self.animations.get(self.player.state, [])
        return self.anim_frame >= len(frames) - 1