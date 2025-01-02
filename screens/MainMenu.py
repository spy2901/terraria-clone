import pygame
import os
from globals import *

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 64)

        # background Image
        # Get the current directory of the script
        current_dir = os.path.dirname(__file__)

        # Construct the path to the image
        image_path = os.path.join(current_dir, "../res/mainMenuImage.jpg")

        # Load the image
        #Load the image with error handling
        try:
            self.bg_image = pygame.image.load(image_path)
            # print(image_path)
            # print("Image loaded succesfully")
        except pygame.error as e:
            print(f"Error loading image: {e}")
        self.screen_width, self.screen_height = self.screen.get_size()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))

        # self.screen.blit(self.bg_image,(0,0))

        # title
        self.title_text = self.font.render("Block Space Adventures", True, TEXT_COLOR)

        self.screen_center_x = self.screen.get_width() // 2

        # START BUTTON
        self.start_text = self.font.render("Start Game", True, BUTTON_TEXT_COLOR)
        text_rect = self.start_text.get_rect(center=(self.screen_center_x, 450))
        self.start_button = pygame.Rect(
            self.screen_center_x - FIXED_BUTTON_WIDTH // 2,  # Fixed width centered
            text_rect.y - PADDING_Y // 2,  # Adjust y-position for padding
            FIXED_BUTTON_WIDTH,  # Use fixed width
            text_rect.height + PADDING_Y  # Height based on text + padding
        )

        # SETTINGS BUTTON
        self.settings_text = self.font.render("Settings", True, BUTTON_TEXT_COLOR)
        text_rect = self.settings_text.get_rect(center=(self.screen_center_x, 550))
        self.settings_button = pygame.Rect(
            self.screen_center_x - FIXED_BUTTON_WIDTH // 2,
            text_rect.y - PADDING_Y// 2,
            FIXED_BUTTON_WIDTH,
            text_rect.height + PADDING_Y
        )

        # EXIT BUTTON
        self.exit_text = self.font.render("Exit Game", True, BUTTON_TEXT_COLOR)
        text_rect = self.exit_text.get_rect(center=(self.screen_center_x, 650))
        self.exit_button = pygame.Rect(
            self.screen_center_x - FIXED_BUTTON_WIDTH // 2,
            text_rect.y - PADDING_Y // 2,
            FIXED_BUTTON_WIDTH,
            text_rect.height + PADDING_Y
        )

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_button.collidepoint(event.pos):
                    self.running = False
                    self.game.running = False
                if self.start_button.collidepoint(event.pos):
                    self.running = False
                if self.settings_button.collidepoint(event.pos):
                    self.game.run_settings()  # Call to switch to Settings screen

    def update(self):
        pass

    def draw(self):
        self.screen.fill(pygame.Color("lightblue"))
        self.screen.blit(self.bg_image, (0,0))
        self.screen.blit(self.title_text, (self.screen.get_width() / 2 - self.title_text.get_width() / 2, 100))

        # Draw Start button
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND_COLOR, self.start_button)
        # Get the size of the Start text and center it within the Start button
        text_rect = self.start_text.get_rect(center=self.start_button.center)
        self.screen.blit(self.start_text, text_rect)

        # Draw Settings button
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND_COLOR, self.settings_button)
        # Get the size of the Settings text and center it within the Settings button
        text_rect = self.settings_text.get_rect(center=self.settings_button.center)
        self.screen.blit(self.settings_text, text_rect)

        # Draw Exit button
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND_COLOR, self.exit_button)
        # Get the size of the Exit text and center it within the Exit button
        text_rect = self.exit_text.get_rect(center=self.exit_button.center)
        self.screen.blit(self.exit_text, text_rect)

        pygame.display.flip()
