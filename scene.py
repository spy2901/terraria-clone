# global modules
import pygame
import os
import json
import random
from opensimplex import OpenSimplex
# classes import
from globals import *
from world.sprite import Entity, Mob
from world.texturedata import solo_texture_data, atlas_texture_data
from world.player import Player
from camera import Camera
from inventory.inventory import Inventory
from world.items import *
from Structures.tree import *


class Scene:
    def __init__(self, app) -> None:
        self.app = app

        self.textures = self.gen_solo_textures()
        self.textures.update(self.gen_atlas_textures('res/owatlas.png'))

        self.sprites = Camera()
        self.blocks = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.group_list: dict[str, pygame.sprite.Group] = {
            'sprites': self.sprites,
            'block_group': self.blocks,
            'enemy_group': self.enemy_group

        }

        # inventory
        self.inventory = Inventory(self.app, self.textures)

        # draw player position
        self.draw_player_pos_bool = True

        # day/night cycle
        self.time_of_day = 0.0  # A value between 0.0 and 1.0
        self.day_length = 3600  # Number of frames per full day-night cycle (adjust as needed)

        # world data
        self.chunks: dict[tuple[int, int], Chunk] = {}
        self.active_chunks: dict[tuple[int, int], Chunk] = {}
        # self.entity = Entity([self.sprites],image=self.textures['grass'])
        # Entity([self.sprites],position=(200,200),image=self.atlas_textures['stone'])
        # player data loading
        # Load player data from save file
        player_data = self.load_game()

        if player_data:  # If player data is loaded from save file
            spawn_x, spawn_y = player_data["position"] # Get player position from saved data
            # print(f"{spawn_x} {spawn_y}")
            health = player_data["health"]  # Get player health from saved data
            inventory_items = player_data["inventory"]  # Get inventory items from saved data
            # Update inventory with saved items
            self.inventory.update_inventory(inventory_items)
        else:
            # Default values in case no save data is found
            spawn_x, spawn_y = TILESIZE * 17, TILESIZE * 17  # Default spawn position
            health = 3  # Default health


        # Initialize player with loaded or default data
        self.player = Player([self.sprites], self.textures['player_static'], (spawn_x, spawn_y),
                             parameters={
                                 'textures': self.textures,
                                 'group_list': self.group_list,
                                 'inventory': self.inventory,
                                 'health': health,
                                 'char_name': 'spy2901'
                             })

        # Entity([self.sprites,self.blocks],pygame.Surface((TILESIZE,TILESIZE*30)),(700,-500))
        Mob([self.sprites, self.enemy_group], self.textures['zombie_static'], (800, -500),
            parameters={'block_group': self.blocks, 'player': self.player, 'damage': 1})


        # self.gen_world()

    def save_game(self):
        # Save game state
        save_data = {
            'player': {
                'position': [self.player.rect.x, self.player.rect.y],
                'health': self.player.health,
                'inventory': self.inventory.serialize_inventory()
            },
            'time_of_day': self.time_of_day,
            'chunks': self.serialize_chunks()
        }

        # Write the data to a JSON file
        with open('savegame.json', 'w') as f:
            json.dump(save_data, f, indent=4)
        print("Game saved successfully.")

    def load_game(self):
        save_file = 'savegame.json'

        if os.path.exists(save_file):
            with open(save_file, 'r') as f:
                try:
                    save_data = json.load(f)
                    player_data = save_data.get('player', None)

                    if player_data:
                        self.time_of_day = save_data.get('time_of_day', 0.0)
                        self.deserialize_chunks(save_data.get('chunks', {}))  # Deserialize chunks after loading the player data
                        return player_data
                    else:
                        print("No player data found in save file.")
                        return None
                except json.JSONDecodeError:
                    print("Error: Failed to decode save file.")
                    return None
        else:
            print(f"No save file found at {save_file}. Starting a new game.")
            return None
    def serialize_chunks(self):
        serialized_chunks = {}

        for chunk_pos, chunk in self.active_chunks.items():
            serialized_chunks[str(chunk_pos)] = {
                "position": chunk.position,
                "blocks": [
                    {
                        "block_type": block.name,
                        "x": block.rect.x,
                        "y": block.rect.y
                    } for block in chunk.blocks
                ]
            }

        return serialized_chunks

    def deserialize_chunks(self, chunks_data):
        for chunk_pos_str, chunk_data in chunks_data.items():
            # Convert the chunk position string back into a tuple
            chunk_pos = eval(chunk_pos_str)

            # Create a new chunk instance at the given position
            chunk = Chunk(chunk_data['position'], self.group_list, self.textures)
            chunk.blocks = []

            # Iterate through each block in the chunk and recreate it
            for block_data in chunk_data["blocks"]:
                block_type = block_data["block_type"]
                x, y = block_data["x"], block_data["y"]

                # Determine the block use type and group
                use_type = items[block_type].use_type
                groups = [self.group_list[group] for group in items[block_type].groups]

                # Create and position the block
                block = use_type(groups, self.textures[block_type], (x, y), block_type)
                chunk.blocks.append(block)

            # Load the chunk into the active_chunks dictionary
            self.active_chunks[chunk_pos] = chunk
            chunk.load_chunk()  # Ensure blocks are added to the sprite groups

        print(f"Loaded {len(self.active_chunks)} chunks from save.")
    def autosave(self):
        if pygame.time.get_ticks() % (0.5 * 60 * 1000) == 0:  # Autosave every 5 minutes
            self.save_game()

    def gen_solo_textures(self) -> dict:
        textures = {}

        for name, data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), data['size'])

        return textures

    def gen_atlas_textures(self, file_path):
        textures = {}
        atlas_img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(), (TILESIZE * 16, TILESIZE * 16))

        for name, data in atlas_texture_data.items():
            textures[name] = pygame.Surface.subsurface(atlas_img, pygame.Rect(data['position'][0] * TILESIZE,
                                                                              data['position'][1] * TILESIZE,
                                                                              data['size'][0], data['size'][1]))
        return textures

    # def gen_world(self):
    #     pass

    def draw_player_pos(self):
        player_x = self.player.rect.x // TILESIZE
        player_y = self.player.rect.y // TILESIZE
        location_text = f"Player Location: ({player_x}, {player_y})"

        self.font = pygame.font.Font(None, 30)

        location_surface = self.font.render(location_text, True, "white")

        self.app.screen.blit(location_surface, (10, 10))

    def draw_player_username(self):
        offset = pygame.math.Vector2()
        offset.x = self.app.screen.get_width() / 2 - self.player.rect.centerx - 20
        offset.y = self.app.screen.get_height() / 2 - self.player.rect.centery - 15

        # Render the username
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.player.char_name, True, (255, 255, 255))
        self.app.screen.blit(text_surface,
                             (offset.x + self.player.rect.centerx, offset.y + self.player.rect.centery - 20))

    def update(self):
        self.sprites.update()
        self.inventory.update()
        self.draw_player_username()
        if self.draw_player_pos_bool:
            self.draw_player_pos()
        self.draw_player_pos()
        self.autosave()
        events = pygame.event.get()  # Capture events for processing

        # Handle quitting the game
        #
        player_chunk_pos = Chunk.get_chunk_pos(self.player.rect.center)

        positions = [
            player_chunk_pos,
            (player_chunk_pos[0] - 1, player_chunk_pos[1]),
            (player_chunk_pos[0] + 1, player_chunk_pos[1]),

            (player_chunk_pos[0] - 1, player_chunk_pos[1] - 1),
            (player_chunk_pos[0] + 1, player_chunk_pos[1] - 1),
            (player_chunk_pos[0], player_chunk_pos[1] - 1),

            (player_chunk_pos[0] - 1, player_chunk_pos[1] + 1),
            (player_chunk_pos[0] + 1, player_chunk_pos[1] + 1),
            (player_chunk_pos[0], player_chunk_pos[1] + 1),

        ]

        for position in positions:
            if position not in self.active_chunks:
                if position in self.chunks:
                    self.chunks[position].load_chunk()
                    self.active_chunks[position] = self.chunks[position]
                else:
                    self.chunks[position] = Chunk(position, self.group_list, self.textures)
                    self.active_chunks[position] = self.chunks[position]

        target = None
        for pos, chunk in self.active_chunks.items():
            if pos not in positions:
                target = pos

        if target:
            self.active_chunks[target].unload_chunk()
            self.active_chunks.pop(target)

        # Update time of day
        # self.time_of_day += 1 / self.day_length
        # if self.time_of_day > 1.0:
        #     self.time_of_day = 0.0
        #
        # # Simulate day/night by adjusting the screen tint
        # self.update_day_night_cycle()

    def update_day_night_cycle(self):
        # Adjust the tint based on the time of day
        min_brightness = 0.2  # Minimum brightness at night, ensure it's not completely dark
        if self.time_of_day < 0.5:
            # Daytime (0.0 to 0.5)
            brightness = 1.0 - 0.5 * abs(0.5 - self.time_of_day) / 0.5
        else:
            # Nighttime (0.5 to 1.0)
            brightness = 0.5 - 0.5 * abs(0.5 - self.time_of_day) / 0.5

        # Adjust brightness to ensure it doesn't go below min_brightness
        brightness = max(brightness, min_brightness)

        # Apply brightness to the screen color
        tint = pygame.Surface(self.app.screen.get_size())
        tint.fill((0, 0, 0))
        tint.set_alpha(int((1.0 - brightness) * 255))
        self.app.screen.blit(tint, (0, 0))

    def draw_time(self):
        # Display the current time on the top-right corner
        hours = int(self.time_of_day * 24)
        minutes = int((self.time_of_day * 24 - hours) * 60)
        time_text = f"Time: {hours:02}:{minutes:02}"

        self.font = pygame.font.Font(None, 30)
        time_surface = self.font.render(time_text, True, "white")
        self.app.screen.blit(time_surface, (self.app.screen.get_width() - time_surface.get_width() - 10, 10))

    def draw(self):
        self.app.screen.fill('skyblue')
        # background Image
        # Get the current directory of the script
        current_dir = os.path.dirname(__file__)

        # Construct the path to the image
        image_path = os.path.join(current_dir, "res/clouds.jpg")

        # Load the image
        # Load the image with error handling
        if not os.path.exists(image_path):
            print(f"Image not found at: {image_path}")
        else:
            try:
                self.bg_image = pygame.image.load(image_path)
                # print(image_path)
                # print("Image loaded succesfully")
            except pygame.error as e:
                print(f"Error loading image: {e}")
            self.screen_width, self.screen_height = self.app.screen.get_size()
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
            self.app.screen.blit(self.bg_image, (0, 0))
        if self.draw_player_pos_bool:
            self.draw_player_pos()
        self.sprites.draw(self.player, self.app.screen)
        self.inventory.draw()
        self.draw_time()


class Chunk:
    CHUNKSIZE = 30
    CHUNKPIXELSIZE = CHUNKSIZE * TILESIZE

    def __init__(self,
                 position: tuple[int, int],
                 group_list: dict[str, pygame.sprite.Group],
                 textures: dict[str, pygame.Surface]) -> None:
        self.position = position
        self.group_list = group_list
        self.textures = textures

        self.blocks: list[Entity] = []

        self.gen_chunk()

    def gen_chunk(self):
        noise_generator = OpenSimplex(seed=92392893)
        cave_noise = OpenSimplex(seed=72392893)
        tunnel_noise = OpenSimplex(seed=394857293)

        heightmap = []
        grass_positions = []  # List to store grass block positions for tree generation

        for y in range(Chunk.CHUNKSIZE * self.position[0], Chunk.CHUNKSIZE * self.position[0] + Chunk.CHUNKSIZE):
            noise_value = noise_generator.noise2(y * 0.05, 0)
            height = int((noise_value + 1) * 4 + 5)
            heightmap.append(height)

        for x in range(len(heightmap)):
            ground_level = heightmap[x]

            if self.position[1] > 0:
                height_val = Chunk.CHUNKSIZE
            elif self.position[1] < 0:
                height_val = 0
            else:
                height_val = ground_level

            # Generate blocks up to the ground level
            for y in range(height_val):
                block_type = 'dirt'
                if y == ground_level - 1:
                    block_type = 'grass'  # Topmost block becomes 'grass'
                    grass_positions.append((x, ground_level))  # Store position of grass blocks
                if y < ground_level - 5:
                    block_type = 'stone'

                if self.position[1] > 0:
                    block_type = 'stone'

                # Cave generation logic
                if y < ground_level - 5:
                    cave_value = cave_noise.noise2(
                        (x + self.position[0] * Chunk.CHUNKSIZE) * 0.08,
                        (y + self.position[1] * Chunk.CHUNKSIZE) * 0.08
                    )
                    tunnel_value = tunnel_noise.noise2(
                        (x + self.position[0] * Chunk.CHUNKSIZE) * 0.02,
                        (y + self.position[1] * Chunk.CHUNKSIZE) * 0.02
                    )

                    if cave_value > 0.2 or tunnel_value > 0.15:
                        continue  # Skip placing block for cave or tunnel
                # ORE GENERATION LOGIC
                if block_type == 'stone':
                    if 3 < y < height_val - 5:
                        if random.random() < COALSPAWNCHANCE:
                            block_type = 'coal'
                    if 6 < y < height_val - 10:
                        if random.random() < IRONSPAWNCHANCE:
                            block_type = 'iron'
                    if 9 < y < height_val - 14:
                        if random.random() < GOLDSPAWNCHANCE:
                            block_type = 'gold'

                # Add block to chunk
                use_type = items[block_type].use_type
                groups = [self.group_list[group] for group in items[block_type].groups]
                self.blocks.append(
                    use_type(
                        groups,
                        self.textures[block_type],
                        (
                            x * TILESIZE + (Chunk.CHUNKPIXELSIZE * self.position[0]),
                            (Chunk.CHUNKSIZE - y) * TILESIZE + (Chunk.CHUNKPIXELSIZE * self.position[1])
                        ),
                        block_type
                    )
                )

        # Tree Generation Logic (after blocks are placed)
        self.trees = []
        for grass_x, ground_level in grass_positions:
            if block_type == 'grass':
                if random.random() < 0.1:  # 10% chance to spawn a tree on grass
                    tree_x = grass_x + self.position[0] * Chunk.CHUNKSIZE  # Global x position of tree
                    tree_y = Chunk.CHUNKSIZE - ground_level + self.position[
                        1] * Chunk.CHUNKSIZE  # Global y position (top of grass)

                    # Spawn the tree directly on top of the grass block
                    tree = Tree(
                        x=tree_x,  # Correct global x-position
                        y=tree_y,  # Correct global y-position (top of grass)
                        trunk_height=random.randint(4, 4),  # Random tree height between 4 and 6 blocks
                        group_list=self.group_list,
                        textures=self.textures
                    )
                    # Append the created tree to the list of trees
                    self.trees.append(tree)

    def serialize(self):
        # Convert the chunk's data to a serializable format (e.g., block positions and types)
        return {
            "position": self.position,
            "blocks": [
                {
                    "block_type": block.name,
                    "x": block.rect.x,
                    "y": block.rect.y
                }
                for block in self.blocks
            ]
        }

    @classmethod
    def deserialize(cls, data, group_list, textures):
        # Create a new chunk with the deserialized data
        chunk = cls(data['position'], group_list, textures)
        chunk.blocks = []

        # Deserialize blocks and add them to the chunk
        for block_data in data["blocks"]:
            block_type = block_data["block_type"]
            x, y = block_data["x"], block_data["y"]
            use_type = items[block_type].use_type
            groups = [group_list[group] for group in items[block_type].groups]

            block = use_type(groups, textures[block_type], (x, y), block_type)
            chunk.blocks.append(block)

        return chunk

    def load_chunk(self):
        for block in self.blocks:
            groups = [self.group_list[group] for group in items[block.name].groups]
            for group in groups:
                group.add(block)

    def unload_chunk(self):
        for block in self.blocks:
            block.kill()

    @staticmethod
    def get_chunk_pos(position: tuple[int, int]) -> tuple[int, int]:
        return (position[0] // Chunk.CHUNKPIXELSIZE, position[1] // Chunk.CHUNKPIXELSIZE)

