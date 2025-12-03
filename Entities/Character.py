from Entities.Attack import Attack

class Personnage:
    def __init__(self, name,level, hp, hp_max, attack, defense, speed, position, attacks):
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
        '''Réduit les points de vie du personnage en fonction des dégâts reçus'''
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        '''Soigne le personnage d'une certaine quantité'''
        self.hp += amount
        if self.hp > self.hp_max:
            self.hp = self.hp_max
    
    def is_alive(self):
        '''Retourne True si le personnage est en vie, False sinon'''
        return self.hp > 0
    
    def do_attack(self, target, attack_obj):
        '''Faire une attaque'''
        pass  # À implémenter

    def is_in_range(self, target, attack_obj):
        '''Vérifie si la cible est dans la portée de l'attaque'''
        distance = abs(self.position[0] - target.position[0]) +abs(self.position[1] - target.position[1])
        return distance <= attack_obj.range