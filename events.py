import pygame
class EventHandler:
    def __init__(self) -> None:
        EventHandler.events = pygame.event.get()
    def poll_events(self):
        EventHandler.events = pygame.event.get()
    def keydown (key) :
        for event in EventHandler.events:
            if event.type == pygame.KEYDOWN:
                if event.key ==key:
                     return True
        return False
    def clicked(leftright = 1) -> bool: # 1 - left click, 3 - right click
        for event in EventHandler.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == leftright: # left click
                    return True
        return False
    def clicked_any(self) -> bool:
        for event in EventHandler.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                    return True
        return False
        