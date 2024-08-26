import pygame
from pygame import mixer
import sys
from globals import *
from scene import Scene
from events import EventHandler
from MainMenu.MainMenu import MainMenu


class Game:
    def __init__(self):
        pygame.init()
        mixer.init()
        pygame.display.set_caption('TERRARIA CLONE')
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True

        # State management
        self.state = "menu"
        self.scene = None
        self.main_menu = MainMenu(self)

    def run(self):
        mixer.music.load('res/sound/music/bg25.wav')
        mixer.music.play()
        mixer.music.set_volume(0.1)
        while self.running:
            if self.state == "menu":
                self.run_menu()
            elif self.state == "game":
                self.run_game()
        self.close()

    def run_game(self):
        while self.running and self.state == "game":
            self.update()
            self.draw()
        self.state = "menu"

    def run_menu(self):
        self.main_menu.running = True
        while self.main_menu.running:
            self.main_menu.handle_events()
            self.main_menu.update()
            self.main_menu.draw()
            self.clock.tick(FPS)
        self.state = "game"
        self.scene = Scene(self)

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
