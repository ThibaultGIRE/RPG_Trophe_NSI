from Entities.Character import Personnage

class Enemy(Personnage):
    def __init__(self, nom, niveau, pv, pv_max, attack, defense, speed, position, attacks):
        super().__init__(nom, niveau, pv, pv_max, attack, defense, speed, position, attacks)

    def decide_action(self, map, player):
        pass

    def choose_target(self, players):
        pass