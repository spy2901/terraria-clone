import pygame
from pygame import mixer
from globals import *
from globals import TILESIZE
from math import sqrt

class Entity(pygame.sprite.Sprite):
    def __init__(self, groups,image = pygame.Surface((TILESIZE,TILESIZE)),position = (0,0),name: str = "default"):
        super().__init__(groups)
        self.name = name
        self.in_groups = groups
        self.image = image
        self.rect = self.image.get_rect(topleft = position)
    def update(self):
        pass

class Mob(Entity):
    
    mixer.init()
    attack_sound = pygame.mixer.Sound('res/sound/malehurteffect.mp3')
    attack_sound.set_volume(0.5)
    
    def __init__(self, groups, image=pygame.Surface((TILESIZE, TILESIZE)), position=(0, 0),parameters = {}):
        super().__init__(groups, image, position)

        if parameters:
            self.block_group = parameters['block_group']
            self.player = parameters['player']
            self.damage = parameters['damage']
            # self.health = parameters['health']
        self.velocity = pygame.math.Vector2()
        self.mass = 5
        self.speed = 0.5
        self.terminal_velocity = TERMINALVELOCITY * self.mass
        
        #sounds

        #states
        self.attacking = True
        self.attacked = False
        self.grounded = False

        # cooldowns
        self.attack_cooldown = 60
        self.counter = self.attack_cooldown

    def play_sound(self, sound):
        sound.play()

    def move(self):
        self.velocity.y += GRAVITY * self.mass
        # terminal velocity check
        if self.velocity.y > self.terminal_velocity:
            self.velocity.y = self.terminal_velocity

        if abs(sqrt((self.rect.x - self.player.rect.x)**2 + (self.rect.y - self.player.rect.y)**2)) < TILESIZE*10:
            # within range
            if self.rect.x > self.player.rect.x:
                self.velocity.x = -self.speed
            elif self.rect.x < self.player.rect.x:
                self.velocity.x = self.speed
            self.attacking = True
        else:
            self.attacking = False
            self.velocity.x = 0

        self.rect.x += self.velocity.x * PLAYERSPEED # applying horizontal velocity
        self.check_collision('horizontal')
        self.rect.y += self.velocity.y  # applying vertical velocity
        self.check_collision('vertical')

        if self.grounded and self.attacking and abs(self.velocity.x)<0.1:
            self.velocity.y = -10

    def check_collision(self, direction):
        if direction == "horizontal":    
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.x > 0: # moving right
                        self.rect.right = block.rect.left
                    if self.velocity.x < 0: # moving left
                        self.rect.left = block.rect.right
                    self.velocity.x = 0
        elif direction == "vertical":
            collisions = 0
            for block in self.block_group:
                if block.rect.colliderect(self.rect):
                    if self.velocity.y > 0: # moving down
                        collisions += 1
                       
                        self.rect.bottom = block.rect.top
                    if self.velocity.y < 0: # moving up
                        self.rect.top = block.rect.bottom
            if collisions > 0:
                self.grounded = True
            else: 
                self.grounded = False

    def check_player_collison(self):
        if self.player.health <= 0:
            Mob.attack_sound.stop()
             

        if self.attacking and not self.attacked:
            if self.rect.colliderect(self.player.rect):
                
                self.player.health -= self.damage
                self.play_sound(Mob.attack_sound)
                self.attacked = True
                self.counter  = self.attack_cooldown

                # knockback player
                if self.player.rect.centerx > self.rect.centerx:
                    self.player.velocity.x = 3
                elif self.player.rect.centerx < self.rect.centerx:
                    self.player.velocity.x = -3
                
                

    def update(self):
        self.move()
        self.check_player_collison()

        if self.attacked:
            self.counter -= 1
            if self.counter < 0:
                self.counter = self.attack_cooldown 
                self.attacked  = False

    @staticmethod
    def stop_sound():
        Mob.attack_sound.stop()