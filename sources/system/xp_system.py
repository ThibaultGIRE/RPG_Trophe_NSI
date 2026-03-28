from Entities.Character import Personnage
from random import randint

class XpSystem:

    @staticmethod
    def required_xp(level):
        # XP required grows quadratically with level
        return 150 * (level ** 2)
    
    @staticmethod
    def gain_xp(character, xp):
        character.xp += xp
        while character.xp >= XpSystem.required_xp(character.level):
            character.xp -= XpSystem.required_xp(character.level)
            XpSystem.level_up(character)


    @staticmethod
    def level_up(character):
        character.level += 1
        XpSystem.apply_stat_growth(character)

    @staticmethod
    def apply_stat_growth(character):

        growth_rates = {
            'hp' : 90,
            'attack' : 45,
            'defense' : 40,
            'speed' : 50
        }       

        if randint(0, 100) < growth_rates['hp']:
            character.hp += 1
            character.hp_max += 1

        if randint(0, 100) < growth_rates['attack']:
            character.attack += 1

        if randint(0,100) < growth_rates['defense']:
            character.defense += 1

        if randint(0, 100) < growth_rates['speed']:
            character.speed += 1
        