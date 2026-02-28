import pygame
from entities.player_components.movement import MovementController
from entities.player_components.attack import AttackController
from entities.player_components.animation import AnimationController
from entities.player_components.state_machine import PlayerStateMachine


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 60)

        # базовые данные
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.on_ladder = False
        self.facing = "right"
        self.state = "idle"

        # компоненты
        self.movement = MovementController(self)
        self.attack = AttackController(self)
        self.animation = AnimationController(self)
        self.state_machine = PlayerStateMachine(self)

    def update(self, platforms, ladders):
        self.movement.update(platforms, ladders)
        self.attack.update()
        self.state_machine.update()
        self.animation.update()

    def draw(self, screen, camera_x, camera_y):
        self.animation.draw(screen, camera_x, camera_y)

    def get_attack_rect(self):
        return self.attack.get_hitbox()