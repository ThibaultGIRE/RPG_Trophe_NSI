import arcade

class GameMap : 
    def __init__(self, tmx_file_path):
        #Note : entities is a dictionnary with the tuple (x,y) as key. tiles is a matrix, obstacles is a list
        self.tile_map = arcade.load_tilemap(
            tmx_file_path,
            scaling=1.0, 
            layer_options={"Obstacles": {"use_spatial_hash": True   }})
        self.width = self.tile_map.width
        self.height = self.tile_map.height
        self.tile_width = self.tile_map.tile_width
        self.tile_height = self.tile_map.tile_height

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.entities = {}

        self.obstacles = self._extract_obstacles()

    def _extract_obstacles(self):
        obstacles = ()

        if "Obstacles" in self.tile_map.name_mapping:
            obstacles_layer = self.scene["Obstacles"]

            for sprites in obstacles_layer:
                x = int(sprites.center_x // self.tile_width)
                y = int(sprites.center_y // self.tile_height)
                obstacles.append((x, y))

        return obstacles

    def is_walkable(self, x, y):
        """Check if the tile at (x,y) is walkable

        Args:
            x (int): x coordinate
            y (int): y coordinate

        """
        if (x, y) in self.obstacles or x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return True
    
    def get_neighbors(self, x, y):
        """Get the walkable neighbors of the tile at (x,y)

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Returns:
            list: list of walkable neighbors as (x,y) tuples
        """
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))

        return neighbors
    
    def place_character(self, character, x, y):
        """Place a character on the map at (x,y)

        Args:
            character (obj): character to place
            x (int): x coordinate
            y (int): y coordinate
        """
        if self.is_walkable(x, y):
            self.entities[(x, y)] = character
            character.position = (x, y)

    def move_character(self, character, new_x, new_y):
        """Move a character to a new position

        Args:
            character (obj): character to move
            new_x (int): new x coordinate
            new_y (int): new y coordinate
        """
        old_position = character.position
        if self.is_walkable(new_x, new_y):
            del self.entities[old_position]
            self.entities[(new_x, new_y)] = character
            character.position = (new_x, new_y)

        
    def in_attack_range(self, attacker, defender):
        distance = abs(attacker.position[0] - defender.position[0]) + abs(attacker.position[1] - defender.position[1])
        attack_range = attacker.attacks[0].range if attacker.attacks else 1
        return distance <= attack_range