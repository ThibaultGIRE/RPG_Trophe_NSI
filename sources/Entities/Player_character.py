from Entities.Character import Personnage

class PlayerCharacter(Personnage):
    def __init__(self, name, level, hp, hp_max, attack, defense, speed, position, attacks, healer=False, special_attack=None):
        """Initialize a PlayerCharacter instance

        Args:
            name (str): character's name
            level (int): current level
            hp (int): current health points
            hp_max (int): maximum health point
            attack (int): stat for attack power
            defense (_type_): _description_
            speed (_type_): _description_
            position (_type_): _description_
            attacks (_type_): _description_
            healer (_type_): _description_
            special_attack (_type_): _description_
        """
        super().__init__(name, level, hp, hp_max, attack, defense, speed, position, attacks)
 
        self.is_healer = healer
        self.special_attack = special_attack
        self.inventory = []

    def use_special(self, target):
        if self.special_attack:
            self.do_attack(target, self.special_attack)

    def can_double_attack(self, target):
        """Check if the character can double attack 

        Args:
            target (obj): represent the target character

        Returns:
            bool: True if the caracter can double attack, Fals otherwise
        """
        return (self.speed - target.speed) >= 5