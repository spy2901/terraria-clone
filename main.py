import pygame
from pygame import mixer
import sys
from globals import *
from scene import Scene
from events import EventHandler
0
class Game:
    def __init__(self):
        pygame.init()
        mixer.init()
        pygame.display.set_caption('TERRARIA CLONE')
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        
        self.clock = pygame.time.Clock()
        # self.music = mixer.Sound('res/sound/music/bg25.wav')
        # self.music.set_volume(0.05)
        self.running = True

        self.scene = Scene(self)
    def run(self):
        mixer.music.load('res/sound/music/bg25.wav')
        mixer.music.play()
        mixer.music.set_volume(0.1)
        while self.running:
            # self.music.play(-1)

            self.update()
            self.draw()
        self.close()
    def update(self):
        EventHandler.poll_events()
        for event in EventHandler.events:
            if event.type == pygame.QUIT:
                self.running = False

        self.scene.update()

        pygame.display.update() 
        self.clock.tick(FPS)
    def draw(self):
        self.scene.draw()
    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 