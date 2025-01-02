import pygame
from globals import *
from events import EventHandler
from world.sprite import Entity, Mob


class Player(pygame.sprite.Sprite):
    char_name= 'spy2901'
    def __init__(self, groups, image=pygame.Surface, position=tuple, parameters=dict) -> None:
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

        # parameters
        self.textures = parameters['textures']
        self.group_list = parameters['group_list']
        self.block_group = self.group_list['block_group']
        self.enemy_group = self.group_list['enemy_group']
        self.inventory = parameters['inventory']
        self.char_name = parameters['char_name']

        # health parameters
        self.health = parameters['health']

        self.velocity = pygame.math.Vector2()
        self.mass = 5
        self.terminal_velocity = self.mass * TERMINALVELOCITY

        # is grounded ???
        self.grounded = True
        self.is_touching_tree = False

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.velocity.x = 1
        if keys[pygame.K_a]:
            self.velocity.x = -1
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            if self.velocity.x > 0:
                self.velocity.x -= 0.1
            elif self.velocity.x < 0:
                self.velocity.x += 0.1

            if abs(self.velocity.x) < 0.3:
                self.velocity.x = 0

    def move(self):
        self.velocity.y += GRAVITY * self.mass
        if self.velocity.y > self.terminal_velocity:
            self.velocity.y = self.terminal_velocity

        self.rect.x += self.velocity.x * PLAYERSPEED  # applying horizontal velocity
        self.check_collision('horizontal')
        self.rect.y += self.velocity.y  # applying vertical velocity
        self.check_collision('vertical')

        # jumping
        if self.grounded and (EventHandler.keydown(pygame.K_SPACE) or EventHandler.keydown(pygame.K_w)):
            self.grounded = False
            self.velocity.y = -PLAYERJUMPPOWER

        if EventHandler.clicked(1):
            for enemy in self.enemy_group:
                if enemy.rect.collidepoint(self.get_adjusted_mouse_position()):
                    self.inventory.slots[self.inventory.active_slot].attack(
                        self, enemy)

    def check_collision(self, direction):
        if direction == "horizontal":
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.x > 0:  # moving right
                        self.rect.right = block.rect.left
                    if self.velocity.x < 0:  # moving left
                        self.rect.left = block.rect.right

        elif direction == "vertical":
            collisions = 0
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.y > 0:  # moving down
                        collisions += 1

                        self.rect.bottom = block.rect.top
                    if self.velocity.y < 0:  # moving up
                        self.rect.top = block.rect.bottom
            if collisions > 0:
                self.grounded = True
            else:
                self.grounded = False

    def block_handling(self):
        placed = False
        collision = False
        mouse_pos = self.get_adjusted_mouse_position()
        if EventHandler.clicked_any():
            for block in self.block_group:
                if block.rect.collidepoint(mouse_pos):
                    collision = True
                    if EventHandler.clicked(1):  # breaking the block
                        # if block == "wood":
                        #     self.is_touching_tree = True
                        #     print("destroyed wood block")
                        self.inventory.add_item(block)
                        block.kill()
                if EventHandler.clicked(3):
                    if not collision:
                        placed = True
        if placed and not collision:
            self.inventory.use(self, self.get_block_pos(mouse_pos))

    def get_adjusted_mouse_position(self) -> tuple:
        mouse_pos = pygame.mouse.get_pos()

        player_offset = pygame.math.Vector2()
        player_offset.x = SCREENWIDTH // 2 - self.rect.centerx
        player_offset.y = SCREENHEIGHT // 2 - self.rect.centery

        return (mouse_pos[0] - player_offset.x, mouse_pos[1]-player_offset.y)

    def get_block_pos(self, mouse_pos: tuple):
        return ((int((mouse_pos[0]//TILESIZE)*TILESIZE), int((mouse_pos[1]//TILESIZE) * TILESIZE)))

    def update(self):
        self.input()
        self.move()
        self.block_handling()

        if self.health <= 0:
            Mob.stop_sound()
            self.kill()
