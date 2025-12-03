from Entities.Character import Personnage

class PlayerCharacter(Personnage):
    def __init__(self, nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks, healer, special_attack):
        super().__init__(nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks)
 
        self.is_healer = healer
        self.special_attack = special_attack
        self.inventory = []

    def use_special(self, target):
        pass

    def can_double_attack(self, target):
        pass