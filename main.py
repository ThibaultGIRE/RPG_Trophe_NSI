from game import Game 
import arcade

def main():
    
    game = Game("maps_imgs/map_living_room_and_kitchen.tmx")
    arcade.run()

if __name__ == "__main__":
    main()