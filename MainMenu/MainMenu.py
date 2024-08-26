import pygame

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("TERRARIA CLONE", True, pygame.Color("white"))
        self.start_text = self.font.render("Start Game", True, pygame.Color("white"))
        self.exit_text = self.font.render("Exit Game", True, pygame.Color("white"))
        self.start_button = self.start_text.get_rect(center=(self.screen.get_width() // 2, 300))
        self.exit_button = self.exit_text.get_rect(center=(self.screen.get_width() // 2, 600))
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

    def update(self):
        pass

    def draw(self):
        self.screen.fill(pygame.Color("lightblue"))
        self.screen.blit(self.title_text, (self.screen.get_width() / 2 - self.title_text.get_width() / 2, 100))
        pygame.draw.rect(self.screen, pygame.Color("green"), self.start_button)
        self.screen.blit(self.start_text, self.start_button)
        pygame.draw.rect(self.screen, pygame.Color("grey"), self.exit_button)
        self.screen.blit(self.exit_text, self.exit_button)
        pygame.display.flip()
