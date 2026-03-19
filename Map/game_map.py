import arcade
import random
import math

class GameMap:
    def __init__(self, width=12, height=10, tile_width=64, tile_height=64, obstacle_count=20):
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Entities stored at grid coordinates
        self.entities = {}

        # Generate obstacles randomly for a simple map
        self.obstacles = set()
        self._generate_obstacles(obstacle_count)

    def _generate_obstacles(self, obstacle_count):
        for _ in range(obstacle_count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.obstacles:
                self.obstacles.add((x, y))

    def draw(self):
        # Draw map background
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=self.width * self.tile_width,
            bottom=0,
            top=self.height * self.tile_height,
            color=arcade.color.DARK_SLATE_GRAY,
        )

        # Draw each tile with dotted borders
        dot_color = arcade.color.LIGHT_GRAY
        for y in range(self.height):
            for x in range(self.width):
                x1 = x * self.tile_width
                y1 = y * self.tile_height
                x2 = x1 + self.tile_width
                y2 = y1 + self.tile_height

                # Draw dotted outline for each cell
                self._draw_dotted_rect(x1, y1, x2, y2, dot_color)

                # Obstacle fill
                if (x, y) in self.obstacles:
                    arcade.draw_lrbt_rectangle_filled(
                        left=x1 + 2,
                        right=x2 - 2,
                        bottom=y1 + 2,
                        top=y2 - 2,
                        color=arcade.color.GRAY,
                    )

    def _draw_dotted_rect(self, x1, y1, x2, y2, color, dash=8, gap=6):
        # Draw dashed horizontal lines
        for x in range(x1, x2, dash + gap):
            x_end = min(x + dash, x2)
            arcade.draw_line(x, y1, x_end, y1, color)
            arcade.draw_line(x, y2, x_end, y2, color)

        # Draw dashed vertical lines
        for y in range(y1, y2, dash + gap):
            y_end = min(y + dash, y2)
            arcade.draw_line(x1, y, x1, y_end, color)
            arcade.draw_line(x2, y, x2, y_end, color)

    def is_walkable(self, x, y):
        if (x, y) in self.obstacles or x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return True

    def get_neighbors(self, x, y):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

    def place_character(self, character, x, y):
        if self.is_walkable(x, y):
            self.entities[(x, y)] = character
            character.position = (x, y)

    def move_character(self, character, new_x, new_y):
        old_position = character.position
        if not self.is_walkable(new_x, new_y):
            return
        if (new_x, new_y) in self.entities and self.entities[(new_x, new_y)] is not character:
            return
        if old_position in self.entities:
            del self.entities[old_position]
        self.entities[(new_x, new_y)] = character
        character.position = (new_x, new_y)

    def in_attack_range(self, attacker, defender):
        distance = abs(attacker.position[0] - defender.position[0]) + abs(attacker.position[1] - defender.position[1])
        attack_range = attacker.attacks[0].range if attacker.attacks else 1
        return distance <= attack_range

    def pixel_to_grid(self, pixel_x, pixel_y):
        grid_x = int(pixel_x // self.tile_width)
        grid_y = int(pixel_y // self.tile_height)
        return (grid_x, grid_y)

    def grid_to_pixel(self, grid_x, grid_y):
        pixel_x = grid_x * self.tile_width + self.tile_width / 2
        pixel_y = grid_y * self.tile_height + self.tile_height / 2
        return (pixel_x, pixel_y)

    def is_occupied(self, x, y):
        return (x, y) in self.entities
