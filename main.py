import math
import sys
import re

from global_constants import *
from event_manager import EventManager
from text_input import TextInput
from scene import *


class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.start_time = 0
        self.running = True
        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        self.font = pygame.font.Font(filename=None, size=60)

        self.menu_active = True
        self.menu_font = pygame.font.Font(filename=None, size=40)

        self.text_input = TextInput()

        # Add a stack to keep track of the menu states
        self.menu_state_stack = ["main menu"]

        self.world_name = None
        self.player_name = None

        self.scene = None

    def run(self):
        dt = 0
        while self.running:
            self.menu_events()

            if self.start_time == 0:
                self.start_time = pygame.time.get_ticks()  # Start the timer when the player selects world and inventory

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time

            buffer_time = 0.00000000000000000000000000001  # in ms (should make this as small as possible but not 0)

            if elapsed_time >= buffer_time:
                dt = self.clock.tick(FRAMES_PER_SECOND) / 1000

            if dt >= 1:
                dt = 1

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                    self.scene.save_world_to_json(world_name=self.world_name)
                    self.scene.inventory.save_inventory_to_json(inventory_name=self.player_name)
                    pygame.quit()
                    sys.exit()

            self.scene.draw(dt=dt)
            self.screen.blit(
                source=self.font.render(text=f"FPS: {math.floor(self.clock.get_fps())}", antialias=True, color="white"),
                dest=(WINDOW_WIDTH - 200, 10))
            pygame.display.update()
            self.clock.tick()

    def menu_events(self):
        while self.menu_active:
            if self.menu_state_stack[-1] == "main menu":
                self.main_menu_selection()
            elif self.menu_state_stack[-1] == "player selection":
                self.player_menu_selection()
            elif self.menu_state_stack[-1] == "create new player":
                self.new_player_menu_creation()
            elif "create new player" in self.menu_state_stack:
                self.menu_state_stack.remove("create new player")
            elif self.menu_state_stack[-1] == "world selection":
                self.world_menu_selection()
            elif self.menu_state_stack[-1] == "create new world":
                self.new_world_menu_creation()
            elif "create new world" in self.menu_state_stack:
                self.menu_state_stack.remove("create new world")

            elif self.menu_state_stack[-1] == "game":
                self.menu_active = False
                self.scene = Scene(screen=self.screen, world_name=self.world_name,
                                   inventory_name=self.player_name)

    def menu_draw(self, menu_options, selected_option):
        self.screen.fill((0, 0, 0))
        for number, option in enumerate(menu_options):
            colour = (255, 255, 255) if number == selected_option else (128, 128, 128)
            text = self.menu_font.render(text=option, antialias=True, color=colour)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)) if option == "Back" else text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + number * 50))
            self.screen.blit(source=text, dest=text_rect)
        pygame.display.flip()

    def main_menu_selection(self):
        menu_options = ["Play", "Quit"]
        selected_option = 0

        while True:
            self.menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:  # Enter key
                        if selected_option == 0:  # Play
                            self.menu_state_stack.append("player selection")
                            return
                        elif selected_option == 1:
                            self.running = False
                            pygame.quit()
                            sys.exit()

    def player_menu_selection(self):
        if not os.path.exists(path="player_save_files"):
            os.makedirs(name="player_save_files")

        inventory_files = os.listdir(path="player_save_files")
        inventory_files.append("Create New Player")
        inventory_files.append("Back")

        menu_options = [re.split(pattern=r'\.json', string=file)[0] for file in inventory_files]
        selected_option = 0

        while True:
            self.menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == len(inventory_files) - 1:  # Back
                            self.menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == len(inventory_files) - 2:  # Create New Player
                            self.menu_state_stack.append("create new player")
                            return
                        else:
                            self.player_name = re.split(pattern=r'\.json', string=inventory_files[selected_option])[0]
                            self.menu_state_stack.append("world selection")
                            return

    def new_player_menu_creation(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.new_player_menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.player_name = self.text_input.input_text.strip()
                            self.menu_state_stack.append("world selection")
                            return

            self.text_input.update()

    def new_player_menu_draw(self, menu_options, selected_option):
        self.screen.fill((0, 0, 0))
        text = self.menu_font.render(text="Enter new player name:", antialias=True, color=(255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - WINDOW_HEIGHT // 5))
        self.screen.blit(source=text, dest=text_rect)

        for number, option in enumerate(menu_options):
            if option == "Text Box":
                self.text_input.draw(screen=self.screen)
            elif option == "Back":
                colour = (255, 255, 255) if number == selected_option else (128, 128, 128)
                text = self.menu_font.render(text=option, antialias=True, color=colour)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                self.screen.blit(source=text, dest=text_rect)

        pygame.display.flip()

    def world_menu_selection(self):
        if not os.path.exists(path="world_save_files"):
            os.makedirs(name="world_save_files")

        world_files = os.listdir(path="world_save_files")
        world_files.append("Create New World")
        world_files.append("Back")

        menu_options = [re.split(pattern=r'\.json', string=file)[0] for file in world_files]
        selected_option = 0

        while True:
            self.menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == len(world_files) - 1:  # Back
                            self.menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == len(world_files) - 2:  # Create New World
                            self.menu_state_stack.append("create new world")
                            return
                        else:
                            self.world_name = re.split(pattern=r'\.json', string=world_files[selected_option])[0]
                            self.menu_state_stack.append("game")
                            return

    def new_world_menu_creation(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.new_world_menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.world_name = self.text_input.input_text.strip()
                            self.menu_state_stack.append("game")
                            return

            self.text_input.update()

    def new_world_menu_draw(self, menu_options, selected_option):
        self.screen.fill((0, 0, 0))
        text = self.menu_font.render(text="Enter new world name:", antialias=True, color=(255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - WINDOW_HEIGHT // 5))
        self.screen.blit(source=text, dest=text_rect)

        for number, option in enumerate(menu_options):
            if option == "Text Box":
                self.text_input.draw(screen=self.screen)
            elif option == "Back":
                colour = (255, 255, 255) if number == selected_option else (128, 128, 128)
                text = self.menu_font.render(text=option, antialias=True, color=colour)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                self.screen.blit(source=text, dest=text_rect)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
