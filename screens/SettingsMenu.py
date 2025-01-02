import pygame
import json
import os
from globals import BUTTON_BACKGROUND_COLOR,BUTTON_TEXT_COLOR,FIXED_BUTTON_WIDTH,PADDING_Y

class SettingsMenu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 64)
        self.screen_center_x = self.screen.get_width() // 2


        # Load settings from JSON
        self.settings_file = 'settings.json'
        self.settings = self.load_settings()
        # LOAD BACKGROUND IMAGE
        # Get the current directory of the script
        current_dir = os.path.dirname(__file__)

        # Construct the path to the image
        image_path = os.path.join(current_dir, "../res/mainMenuImage.jpg")

        try:
            self.bg_image = pygame.image.load(image_path)
            # print(image_path)
            # print("Image loaded succesfully")
        except pygame.error as e:
            print(f"Error loading image: {e}")
        self.screen_width, self.screen_height = self.screen.get_size()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        # Title
        self.title_text = self.font.render("SETTINGS", True, BUTTON_TEXT_COLOR)

        # Back button to return to main menu
        self.back_text = self.font.render("Back", True, BUTTON_TEXT_COLOR)
        # Get text rect for Exit button
        text_rect = self.back_text.get_rect(center=(self.screen_center_x, 650))
        self.back_button = pygame.Rect(
            self.screen_center_x - FIXED_BUTTON_WIDTH // 2,
            text_rect.y - PADDING_Y // 2,
            FIXED_BUTTON_WIDTH,
            text_rect.height + PADDING_Y
        )
        # Music Checkbox
        self.music_text = self.font.render("Music", True, BUTTON_TEXT_COLOR)
        self.checkbox_rect = pygame.Rect(self.screen.get_width() // 2 + 120, self.screen.get_height() // 2 - 200, 40, 40)
        self.checkbox_checked = self.settings.get("music", True)  # Default to music ON

        # Resolution Dropdown
        self.resolutions = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.resolution_text = self.font.render("Resolution", True, pygame.Color("white"))
        self.selected_resolution = tuple(self.settings.get("resolution", (800, 600)))  # Default resolution
        self.dropdown_active = False
        self.dropdown_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 + 50, 200,
                                         50)
        self.dropdown_items = [pygame.Rect(self.dropdown_rect.x, self.dropdown_rect.y + (i + 1) * 50, 200, 50)
                               for i in range(len(self.resolutions))]

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button.collidepoint(event.pos):
                    self.save_settings()  # Save settings when exiting
                    self.running = False  # Exit Settings Menu and go back to Main Menu
                elif self.checkbox_rect.collidepoint(event.pos):
                    # Toggle checkbox state
                    self.checkbox_checked = not self.checkbox_checked
                    # Update music state in the game
                    self.game.music_on = self.checkbox_checked
                    if self.game.music_on:
                        pygame.mixer.music.play(-1)  # Loop music
                    else:
                        pygame.mixer.music.stop()
                elif self.dropdown_rect.collidepoint(event.pos):
                    # Toggle dropdown active/inactive
                    self.dropdown_active = not self.dropdown_active
                elif self.dropdown_active:
                    for i, item in enumerate(self.dropdown_items):
                        if item.collidepoint(event.pos):
                            self.selected_resolution = self.resolutions[i]
                            self.game.set_resolution(self.selected_resolution)  # Set the game's resolution
                            self.dropdown_active = False  # Close dropdown after selection

    def update(self):
        pass

    def draw(self):
        self.screen.fill(pygame.Color("lightblue"))
        self.screen.blit(self.bg_image, (0,0))

        # Draw screen title
        self.screen.blit(self.title_text, (self.screen.get_width() / 2 - self.title_text.get_width() / 2, 50))

        # Draw Music Checkbox
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND_COLOR, self.checkbox_rect)
        if self.checkbox_checked:
            pygame.draw.line(self.screen, BUTTON_TEXT_COLOR, (self.checkbox_rect.left, self.checkbox_rect.top),
                             (self.checkbox_rect.right, self.checkbox_rect.bottom), 5)
            pygame.draw.line(self.screen, BUTTON_TEXT_COLOR, (self.checkbox_rect.left, self.checkbox_rect.bottom),
                             (self.checkbox_rect.right, self.checkbox_rect.top), 5)
        self.screen.blit(self.music_text,
                         (self.checkbox_rect.x - 220, self.checkbox_rect.y - 5))  # Adjust checkbox text position

        # Draw Resolution Dropdown
        # self.screen.blit(self.resolution_text, (self.dropdown_rect.x, self.dropdown_rect.y - 50))
        # pygame.draw.rect(self.screen, pygame.Color("grey"), self.dropdown_rect)
        # selected_text = self.font.render(f"{self.selected_resolution[0]}x{self.selected_resolution[1]}", True,
        #                                  pygame.Color("white"))
        # self.screen.blit(selected_text, (self.dropdown_rect.x + 10, self.dropdown_rect.y + 10))
        #
        # if self.dropdown_active:
        #     for i, item in enumerate(self.dropdown_items):
        #         pygame.draw.rect(self.screen, pygame.Color("lightgrey"), item)
        #         res_text = self.font.render(f"{self.resolutions[i][0]}x{self.resolutions[i][1]}", True,
        #                                     pygame.Color("black"))
        #         self.screen.blit(res_text, (item.x + 10, item.y + 10))

        # Draw Exit button
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND_COLOR, self.back_button)
        # Get the size of the Exit text and center it within the Exit button
        text_rect = self.back_text.get_rect(center=self.back_button.center)
        self.screen.blit(self.back_text, text_rect)

        pygame.display.flip()

    def load_settings(self):
        """Load settings from the JSON file."""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"music": True, "resolution": (800, 600)}  # Default settings

    def save_settings(self):
        """Save the current settings to a JSON file."""
        with open(self.settings_file, 'w') as f:
            json.dump({"music": self.checkbox_checked, "resolution": list(self.selected_resolution)}, f)
