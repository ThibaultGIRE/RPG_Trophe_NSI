from Entities.Character import Personnage
from random import randint as r

class Xp_system:

    @staticmethod
    def required_xp(level):
        return int(150 * level^2,2)
    
    @staticmethod
    def gain_xp(xp, character):
        requi_xp = Xp_system.required_xp(character.level)
        character.xp += xp
        if character.xp >= requi_xp:
            character.xp -= requi_xp
            Xp_system.level_up(character)


    @staticmethod
    def level_up(character):
        character.level += 1
        if r(0, 100) < 60:
            character.hp += 1
            character.hp_max += 1
        if r(0, 100) < 45:
            character.attack += 1
        if r(0,100) < 40:
            character.defense += 1
        if r(0, 100) < 50:
            character.speed += 1
        