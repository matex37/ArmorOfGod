class PlayerStateMachine:
    def __init__(self, player):
        self.player = player

    def update(self):
        if self.player.attack.attacking:
            self.player.state = "attack"
        elif self.player.on_ladder:
            self.player.state = "idle"
        elif not self.player.on_ground:
            self.player.state = "jump"
        elif self.player.velocity_x != 0:
            self.player.state = "run"
        else:
            self.player.state = "idle"