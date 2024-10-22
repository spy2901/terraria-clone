import pygame
from globals import *
from world.sprite import Entity, Mob
from world.texturedata import solo_texture_data,atlas_texture_data
from world.player import Player
from opensimplex import OpenSimplex
from camera import Camera
from inventory.inventory import Inventory
from world.items import *
import random

class Scene:
    def __init__(self,app) -> None:
        self.app = app


        self.textures = self.gen_solo_textures()
        self.textures.update(self.gen_atlas_textures('res/owatlas.png'))

        self.sprites = Camera()
        self.blocks = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.group_list: dict[str,pygame.sprite.Group] = {
            'sprites': self.sprites,
            'block_group': self.blocks,
            'enemy_group': self.enemy_group

        }

        #inventory
        self.inventory = Inventory(self.app,self.textures)

        # day/night cycle
        self.time_of_day = 0.0  # A value between 0.0 and 1.0
        self.day_length = 3600  # Number of frames per full day-night cycle (adjust as needed)


        self.entity = Entity([self.sprites],image=self.textures['grass'])
        # Entity([self.sprites],position=(200,200),image=self.atlas_textures['stone'])
        
        
        spawn_x, spawn_y = TILESIZE * 1, TILESIZE * 1  
        self.player = Player([self.sprites],self.textures['player_static'],(spawn_x,spawn_y),parameters={
                                                                                    'textures':self.textures,
                                                                                    'group_list':self.group_list,
                                                                                    'inventory': self.inventory,
                                                                                    'health': 3
                                                                                            })
        
        # Entity([self.sprites,self.blocks],pygame.Surface((TILESIZE,TILESIZE*30)),(700,-500))
        Mob([self.sprites, self.enemy_group],self.textures['zombie_static'],(800,-500),parameters={'block_group':self.blocks, 'player':self.player, 'damage':1})

        self.chunks: dict[tuple[int,int],Chunk] = {}
        self.active_chunks: dict[tuple[int,int],Chunk] = {}

        # self.gen_world()
    def gen_solo_textures(self) -> dict:
        textures = {}

        for name,data in solo_texture_data.items():
            textures[name] = pygame.transform.scale(pygame.image.load(data['file_path']).convert_alpha(), data['size'])

        return textures
    def gen_atlas_textures(self,file_path):
        textures = {}
        atlas_img = pygame.transform.scale(pygame.image.load(file_path).convert_alpha(),(TILESIZE*16,TILESIZE*16)) 


        for name,data in atlas_texture_data.items():
            textures[name] = pygame.Surface.subsurface(atlas_img,pygame.Rect(data['position'][0]*TILESIZE,
                                                                             data['position'][1]*TILESIZE,
                                                                             data['size'][0],data['size'][1]))
        return textures
    

    # def gen_world(self):
    #     pass

    def draw_player_pos(self):
        player_x = self.player.rect.x // TILESIZE 
        player_y = self.player.rect.y // TILESIZE 
        location_text = f"Player Location: ({player_x}, {player_y})"

        self.font = pygame.font.Font(None,30)

        location_surface = self.font.render(location_text, True, "white")

        self.app.screen.blit(location_surface, (10,10))


    def update(self):
        self.sprites.update()
        self.inventory.update()
        self.draw_player_pos()

        player_chunk_pos = Chunk.get_chunk_pos(self.player.rect.center)

        positions = [
            player_chunk_pos,
            (player_chunk_pos[0]-1, player_chunk_pos[1]),
            (player_chunk_pos[0]+1, player_chunk_pos[1]),
            
            
            (player_chunk_pos[0]-1, player_chunk_pos[1]-1),
            (player_chunk_pos[0]+1, player_chunk_pos[1]-1),
            (player_chunk_pos[0], player_chunk_pos[1]-1),

            (player_chunk_pos[0]-1, player_chunk_pos[1]+1),
            (player_chunk_pos[0]+1, player_chunk_pos[1]+1),
            (player_chunk_pos[0], player_chunk_pos[1]+1),

        ]


        for position in positions:
            if position not in self.active_chunks:
                if position in self.chunks:
                    self.chunks[position].load_chunk()
                    self.active_chunks[position] = self.chunks[position]
                else:
                    self.chunks[position] = Chunk(position,self.group_list,self.textures)
                    self.active_chunks[position] = self.chunks[position]

        target = None
        for pos,chunk in self.active_chunks.items():
            if pos not in positions:
                target = pos

        if target:
            self.active_chunks[target].unload_chunk()
            self.active_chunks.pop(target)

         # Update time of day
        self.time_of_day += 1 / self.day_length
        if self.time_of_day > 1.0:
            self.time_of_day = 0.0

        # Simulate day/night by adjusting the screen tint
        self.update_day_night_cycle()

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
        self.sprites.draw(self.player,self.app.screen)
        self.inventory.draw()
        self.draw_time()

class Chunk:
    CHUNKSIZE = 30
    CHUNKPIXELSIZE = CHUNKSIZE * TILESIZE



    def __init__(self,
                 position: tuple[int,int],
                 group_list: dict[str, pygame.sprite.Group],
                 textures: dict[str,pygame.Surface]) -> None:
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
        for y in range(Chunk.CHUNKSIZE * self.position[0],Chunk.CHUNKSIZE * self.position[0] + Chunk.CHUNKSIZE):
            noise_value = noise_generator.noise2(y*0.05,0)
            height = int((noise_value+1) * 4 + 5)
            heightmap.append(height)
        
        for x in range(len(heightmap)):
            if self.position[1] > 0:
                height_val = Chunk.CHUNKSIZE
            elif self.position[1] < 0:
                height_val = 0
            else:
                height_val = heightmap[x]

            for y in range(height_val):
                y_offset = 5 - y + 6
                block_type = 'dirt'
                if  y == heightmap[x]-1:
                    block_type = 'grass'
                if y < heightmap[x] - 5:
                    block_type = 'stone'

                if self.position[1] > 0:
                    block_type = 'stone'
                
                # Cave generation logic below the surface
                if y < heightmap[x] - 5:
                    cave_value = cave_noise.noise2(
                        (x + self.position[0] * Chunk.CHUNKSIZE) * 0.1,
                        (y + self.position[1] * Chunk.CHUNKSIZE) * 0.1,
                    )
                    tunnel_value = tunnel_noise.noise2(
                        (x + self.position[0] * Chunk.CHUNKSIZE) * 0.05,
                        (y + self.position[1] * Chunk.CHUNKSIZE) * 0.05,
                        
                    )

                    # Determine if the point should be part of a cave
                    if -0.2 < cave_value < 0.2 or -0.15 < tunnel_value < 0.15:
                        continue  # Skip placing a block to create a cave/tunnel




                # ORE GENERATION LOGIC
                if block_type == 'stone':
                    if y > 3 and y < height_val-5:
                        if random.random() < COALSPAWNCHANCE:
                            block_type = 'coal'
                    if y > 6 and y < height_val - 10:
                        if random.random() < IRONSPAWNCHANCE:
                            block_type = 'iron'
                    if y > 9 and y < height_val - 14:
                        if random.random() < GOLDSPAWNCHANCE:
                            block_type = 'gold'

                use_type = items[block_type].use_type
                groups = [self.group_list[group] for group in items[block_type].groups]
                self.blocks.append(use_type(groups,
                                            self.textures[block_type],
                                            (x*TILESIZE+(Chunk.CHUNKPIXELSIZE* self.position[0]),
                                            (Chunk.CHUNKSIZE-y)*TILESIZE+(Chunk.CHUNKPIXELSIZE* self.position[1])),
                                            block_type))
                

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
        return (position[0]//Chunk.CHUNKPIXELSIZE, position[1]//Chunk.CHUNKPIXELSIZE)