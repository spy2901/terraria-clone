# System libraries
import os

import pygame
from pygame import mixer
import sys
from time import time
from pypresence import Presence
from dotenv import load_dotenv
# game requirements
from globals import *
from scene import Scene
from events import EventHandler
from screens.MainMenu import MainMenu
from screens.SettingsMenu import SettingsMenu
from screens.PauseMenu import PauseMenu

# Discord Rich Presence
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID') # Replace with your Discord application's client ID
rpc = Presence(CLIENT_ID)
rpc.connect()
# Update the presence
def update_presence(state):
    rpc.update(
        state="Exploring the world",
        details="In the main game",
        large_image="blockspaceadventures",  # Name of the uploaded asset in the Discord Dev Portal
        large_text="Terraria-like Game",
        small_image="blockspacesmallimage",  # Optional, key of a small image
        small_text="Level 10",
        start=int(time()),  # Timestamp for session start
    )
    if state == "menu":
        rpc.update(
            state="Browsing the Menu",
            details="Exploring options",
            large_image="blockspaceadventures",
            large_text="Terraria-like Game",
        )
    elif state == "game":
        rpc.update(
            state="Exploring the world",
            details="In the main game",
            large_image="blockspaceadventures",
            large_text="Terraria-like Game",
            small_image="blockspacesmallimage",
            small_text="Adventuring",
            start=int(time()),
        )
    elif state == "settings":
        rpc.update(
            state="Adjusting Settings",
            details="Tinkering with preferences",
            large_image="blockspaceadventures",  # Name of the uploaded asset in the Discord Dev Portal
            large_text="Settings Menu",
        )
    elif state == "pause":
        rpc.update(
            state="Paused",
            details="Taking a break",
            large_image="blockspaceadventures",
            large_text="Terraria-like Game",
        )


class Game:

    def __init__(self):
        pygame.init()
        mixer.init()
        pygame.display.set_caption('Blosk Space adventures')
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

        self.clock = pygame.time.Clock()
        self.running = True
        self.music_running = True

        # State management
        self.state = "menu"
        self.scene = None
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.pause_menu = PauseMenu(self)  # Initialize pause menu to None

    def run(self):
        mixer.music.load('res/sound/music/bg25.wav')
        if self.music_running:
            mixer.music.play()
            mixer.music.set_volume(0.1)

        # Initial presence update
        update_presence(self.state)

        while self.running:
            if self.state == "menu":
                self.run_menu()
            elif self.state == "game":
                self.run_game()
        self.close()

    def run_pause(self):
        self.pause_menu.running = True
        while self.pause_menu.running and self.state == "pause":
            self.pause_menu.handle_events()  # Handle pause menu events
            self.pause_menu.update()  # Update pause menu (e.g., animations)
            self.pause_menu.draw()  # Draw the pause menu
            self.clock.tick(FPS)
    def run_game(self):
        self.scene = Scene(self)  # Initialize the scene
        events = pygame.event.get()  # Capture events for processing

        while self.running and self.state == "game":
            self.update()
            self.draw()
            for event in events:
                if event.type == pygame.QUIT:
                    # self.close()
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Press ESC to pause
                        self.state = "pause"
                        print()
                        update_presence("menu")  # Update presence for pause menu
                        self.run_pause()  # Run the pause menuÏ
        self.state = "menu"  # Return to the menu after game loop ends

    def run_menu(self):
        self.main_menu.running = True
        update_presence("menu")  # Update presence for menu screen

        while self.main_menu.running:
            self.main_menu.handle_events()
            self.main_menu.update()
            self.main_menu.draw()
            self.clock.tick(FPS)

        self.state = "game"
        update_presence("game")  # Update presence for menu screen

    def run_settings(self):
        self.settings_menu.running = True
        update_presence("settings")  # Update presence for settings screen

        while self.settings_menu.running:
            self.settings_menu.handle_events()
            self.settings_menu.update()
            self.settings_menu.draw()
            self.clock.tick(FPS)

        self.state = "menu"  # Transition back to menu
        update_presence("menu")  # Update presence for menu screenÏ

    def set_resolution(self, resolution):
        """Set the game screen resolution."""
        self.screen = pygame.display.set_mode(resolution)

    def update(self):
        EventHandler.poll_events()
        events = pygame.event.get()  # Capture events for processing

        # Handle quitting the game
        for event in events:
            if event.type == pygame.QUIT:
                self.close()
                self.running = False

        if EventHandler.keydown(pygame.K_0):
            self.scene.draw_player_pos_bool = not self.scene.draw_player_pos_bool
            # Save the game when S is pressed
        if EventHandler.keydown(pygame.K_p):
            self.scene.save_game()  # Call the save method
            print("Game saved.")

        self.scene.update()
        self.scene.draw()
        # Refresh the display
        pygame.display.update()
        self.clock.tick(FPS)  # Maintain frame rate

    def draw(self):
        if not self.pause_menu:  # Only draw the scene if the pause menu is not active
            self.scene.draw()
        else:
            self.pause_menu.draw()  # Draw the pause menu if active

    def close(self):
        self.scene.save_game()  # Save the game before quitting
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()