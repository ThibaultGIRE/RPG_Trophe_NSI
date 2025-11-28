class Personnage:
    def __init__(self, nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks):
        '''Initialisation du personnage. Notes : position est un tuple (x,y) et attacks est une liste. Différencier attacks de attack'''
        self.nom = nom
        self.points_de_vie = points_de_vie
        self.niveau = niveau
        self.xp = 0
        self.pv = pv
        self.pv_max = pv_max
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.position = position #tuple (x,y)
        self.attacks = attacks #liste 

    def move(self, dx, dy):
        '''Déplace le personnage de dx en x et dy en y'''
        x, y = self.position
        self.position = (x + dx, y + dy)

    def take_damage(self, damage):
        '''Réduit les points de vie du personnage en fonction des dégâts reçus'''
        self.points_de_vie -= damage
        if self.points_de_vie < 0:
            self.points_de_vie = 0
    
    def is_alive(self):
        '''Retourne True si le personnage est en vie, False sinon'''
        return self.points_de_vie > 0
    
    def do_attack(self, target, attack_obj):
        '''Faire une attaque'''
        pass  # À implémenter

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

class Enemy(Personnage):
    def __init__(self, nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks):
        super().__init__(nom, points_de_vie, niveau, pv, pv_max, attack, defense, speed, position, attacks)

    def decide_action(self, map, player):
        pass

    def choose_target(self, players):
        pass

class Attack:
    def __init__(self, name, precision, special_effect, base_damage):
        self.name = name
        self.precision = precision
        self.special_effect = special_effect
        self.base_damage = base_damage

    def calculate_damage(self, enemy, target):
        pass