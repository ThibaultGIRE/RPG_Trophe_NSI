import os
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Entities.Attack import Attack

stat_de_base = {"base enemy":{"level": 1, 
                              "hp": 15, 
                              "hp_max": 15, 
                              "attack": 7, 
                              "defense": 3, 
                              "speed": 3}, 
                "boss":{"level": 1, 
                        "hp": 50, 
                        "hp_max": 40, 
                        "attack": 15, 
                        "defense": 10, 
                        "speed": 10},
                "player character":{"level": 1,
                                    "hp": 15,
                                    "hp max": 15,
                                    "attack": 5,
                                    "defense": 5,
                                    "speed": 5}
} 
                
class Personnage:
    def __init__(self, name, level, hp, hp_max, attack, defense, speed, position, attacks):
        '''Initialize a Charadter instance.

        Args:
            name (str): character's name
            level (int): current level
            hp (int): current health points
            hp_max (int): maximum health point
            attack (int): stat for attack power
            defense (int): stat for defense power
            speed (int): stat for speed
            position (tuple): character's positon as (x, y)
            attacks (list): list of Attack objects
        '''
        self.name = name
        self.level = level
        self.xp = 0
        self.hp = hp
        self.hp_max = hp_max
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.position = position #tuple (x,y)
        self.attacks = attacks #liste 

    def move(self, dx, dy):
        """move the character

        Args:
            dx (int): number of step in x direction
            dy (int): number of step in y direction
        """
        x, y = self.position
        self.position = (x + dx, y + dy)

    def take_damage(self, damage):
        """Take of damage to the character's hp

        Args:
            damage (int): number of damage to take of the character's hp
        """
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal_self(self, amount):
        """Heal the character 

        Args:
            amount (int): amount of hp to heal
        """
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max
    
    def is_alive(self):
        """Check if the character is alive

        Returns:
            bool: True if the character is alive, False otherwise
        """
        return self.hp > 0
    
    def do_attack(self, target, attack_obj):
        """_summary_

        Args:
            target (_type_): _description_
            attack_obj (_type_): _description_
        """
        pass  # À implémenter

    def is_in_range(self, target, attack_obj):
        """_summary_

        Args:
            target (_type_): _description_
            attack_obj (_type_): _description_

        Returns:
            _type_: _description_
        """
        distance = abs(self.position[0] - target.position[0]) +abs(self.position[1] - target.position[1])
        return distance <= attack_obj.range