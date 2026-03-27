import arcade
import random
import math

class GameMap:
    def __init__(self, width=12, height=10, tile_width=64, tile_height=64, obstacle_count=20):
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Extra rows usable only in combat around the map
        self.extra_rows_top = 0
        self.extra_rows_bottom = 0

        # Entities stored at grid coordinates
        self.entities = {}

        # Generate obstacles randomly for a simple map
        self.obstacles = set()
        self._generate_obstacles(obstacle_count)
        
        # Heal station position (green circle that restores heal potions)
        self.heal_station = None
        self._generate_heal_station()

    def _generate_obstacles(self, obstacle_count):
        for _ in range(obstacle_count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.obstacles:
                self.obstacles.add((x, y))
    
    def _generate_heal_station(self):
        """Generate a heal station at a random valid position."""
        for _ in range(100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.obstacles:
                self.heal_station = (x, y)
                return
        # Fallback: center of map if no valid position found
        self.heal_station = (self.width // 2, self.height // 2)

    def draw(self, origin_x=0, origin_y=0, draw_width=None, draw_height=None):
        total_rows = self.height + self.extra_rows_top + self.extra_rows_bottom
        if draw_width is None:
            draw_width = self.width * self.tile_width
        if draw_height is None:
            draw_height = total_rows * self.tile_height

        scale_x = draw_width / (self.width * self.tile_width)
        scale_y = draw_height / (total_rows * self.tile_height)
        scale = min(scale_x, scale_y)

        tile_w = self.tile_width * scale
        tile_h = self.tile_height * scale
        total_width = tile_w * self.width
        total_height = tile_h * total_rows

        # Center map in provided rect
        offset_x = origin_x + (draw_width - total_width) / 2
        offset_y = origin_y + (draw_height - total_height) / 2

        # Draw map background
        arcade.draw_lrbt_rectangle_filled(
            left=offset_x,
            right=offset_x + total_width,
            bottom=offset_y,
            top=offset_y + total_height,
            color=arcade.color.DARK_SLATE_GRAY,
        )

        # Draw each tile with dotted borders, including extra rows
        dot_color = arcade.color.LIGHT_GRAY
        for y in range(-self.extra_rows_bottom, self.height + self.extra_rows_top):
            for x in range(self.width):
                x1 = offset_x + x * tile_w
                y1 = offset_y + (y + self.extra_rows_bottom) * tile_h
                x2 = x1 + tile_w
                y2 = y1 + tile_h

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
                
                # Draw heal station (green circle)
                if self.heal_station and (x, y) == self.heal_station:
                    center_x = x1 + tile_w / 2
                    center_y = y1 + tile_h / 2
                    radius = min(tile_w, tile_h) / 3
                    arcade.draw_circle_filled(center_x, center_y, radius, arcade.color.LIGHT_GREEN)

    def get_draw_info(self, origin_x=0, origin_y=0, draw_width=None, draw_height=None):
        total_rows = self.height + self.extra_rows_top + self.extra_rows_bottom
        if draw_width is None:
            draw_width = self.width * self.tile_width
        if draw_height is None:
            draw_height = total_rows * self.tile_height

        scale_x = draw_width / (self.width * self.tile_width)
        scale_y = draw_height / (total_rows * self.tile_height)
        scale = min(scale_x, scale_y)

        tile_w = self.tile_width * scale
        tile_h = self.tile_height * scale
        total_width = tile_w * self.width
        total_height = tile_h * total_rows

        offset_x = origin_x + (draw_width - total_width) / 2
        offset_y = origin_y + (draw_height - total_height) / 2

        return {
            "scale": scale,
            "tile_w": tile_w,
            "tile_h": tile_h,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "total_width": total_width,
            "total_height": total_height,
        }

    def _draw_dotted_rect(self, x1, y1, x2, y2, color, dash=8, gap=6):
        # Draw dashed horizontal lines with float-safe iteration
        x = x1
        step = dash + gap
        while x < x2:
            x_end = min(x + dash, x2)
            arcade.draw_line(x, y1, x_end, y1, color)
            arcade.draw_line(x, y2, x_end, y2, color)
            x += step

        # Draw dashed vertical lines with float-safe iteration
        y = y1
        while y < y2:
            y_end = min(y + dash, y2)
            arcade.draw_line(x1, y, x1, y_end, color)
            arcade.draw_line(x2, y, x2, y_end, color)
            y += step

    def is_walkable(self, x, y):
        min_y = -self.extra_rows_bottom
        max_y = self.height + self.extra_rows_top - 1
        if (x, y) in self.obstacles:
            return False
        if x < 0 or x >= self.width or y < min_y or y > max_y:
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
        if not self.is_walkable(x, y):
            return False
        if (x, y) in self.entities:
            return False
        self.entities[(x, y)] = character
        character.position = (x, y)
        return True

    def set_combat_extra_rows(self, top_rows=0, bottom_rows=0):
        self.extra_rows_top = top_rows
        self.extra_rows_bottom = bottom_rows

    def clear_combat_extra_rows(self):
        self.extra_rows_top = 0
        self.extra_rows_bottom = 0

    def move_character(self, character, new_x, new_y):
        old_position = character.position
        if not self.is_walkable(new_x, new_y):
            return False
        if (new_x, new_y) in self.entities and self.entities[(new_x, new_y)] is not character:
            return False

        if old_position in self.entities and self.entities[old_position] is character:
            del self.entities[old_position]

        self.entities[(new_x, new_y)] = character
        character.position = (new_x, new_y)
        return True

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
