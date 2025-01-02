import  pygame
class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.running = True
        self.back_button_rect = pygame.Rect(590, 335, 100, 50)  # "Back" button position and size

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
                self.running = False

            # If ESC is pressed, close the pause menu
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("Pause menu deactivated with ESC")
                self.running = False  # Exit pause menu
                self.game.pause_menu = None  # Resume the game

            # Handle mouse clicks on the back button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left-click
                    print(f"Mouse clicked at {event.pos}")
                    if self.back_button_rect.collidepoint(event.pos):
                        print("Back button clicked!")
                        self.running = False  # Close the pause menu
                        self.game.pause_menu = None  # Resume the game

    def draw(self):
        # Draw a semi-transparent overlay for the pause menu
        overlay = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black overlay
        self.game.screen.blit(overlay, (0, 0))

        # Draw the back button
        pygame.draw.rect(self.game.screen, (255, 0, 0), self.back_button_rect)  # Red back button
        # Add text to the button
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render("Back", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.back_button_rect.center)
        self.game.screen.blit(text_surface, text_rect)
    def update(self):
        pass
