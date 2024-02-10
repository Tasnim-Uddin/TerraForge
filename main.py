import math
import sys
import re
import os
import pygame
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
        self.menu_options = ["Play", "Quit Game"]
        self.selected_option = 0
        self.world_name = None
        self.inventory_name = None

    def run(self):
        dt = 0
        while self.running:
            if self.menu_active:
                self.handle_menu_events()
                self.draw_menu()
            else:
                if self.start_time == 0:
                    self.start_time = pygame.time.get_ticks()  # Start the timer when the player selects world and inventory

                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.start_time

                buffer_time = 1  # in ms

                if elapsed_time >= buffer_time:
                    dt = self.clock.tick(FRAMES_PER_SECOND) / 1000

                if dt >= 1:
                    dt = 1

                EventManager.queue_events()
                for event in EventManager.events:
                    if event.type == pygame.QUIT or EventManager.quit_game():
                        self.running = False
                        self.save_and_quit()  # Save world before quitting

                self.scene.draw(dt=dt)
                self.screen.blit(
                    self.font.render(text=f"FPS: {math.floor(self.clock.get_fps())}", antialias=True, color="white"),
                    dest=(WINDOW_WIDTH - 200, 10))
                pygame.display.update()
                self.clock.tick(FRAMES_PER_SECOND)

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:  # Play
                        self.menu_active = False
                        self.world_name = self.handle_world_choice()
                        self.inventory_name = self.handle_inventory_choice()
                        self.scene = Scene(screen=self.screen, world_name=self.world_name,
                                           inventory_name=self.inventory_name)
                    elif self.selected_option == 1:  # Quit Game
                        self.running = False
                        self.save_and_quit()  # Save world before quitting

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected_option else (128, 128, 128)
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 50))
            self.screen.blit(text, text_rect)
        pygame.display.flip()

    def handle_world_choice(self):
        world_files = os.listdir("world_save_files")
        world_files.append("Create New World")

        self.menu_options = world_files
        self.selected_option = 0

        while True:
            self.draw_world_menu()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == len(world_files) - 1:  # Create New World
                            world_name = self.get_new_world_name()
                            if world_name.strip() != "":
                                return world_name
                        else:
                            world_name = re.split(pattern=r'\.json', string=world_files[self.selected_option])[0]
                            return world_name

    def draw_world_menu(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected_option else (128, 128, 128)
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 50))
            self.screen.blit(text, text_rect)
        pygame.display.flip()

    def handle_inventory_choice(self):
        inventory_files = os.listdir("player_save_files")
        inventory_files.append("Create New Player")

        self.menu_options = inventory_files
        self.selected_option = 0

        while True:
            self.draw_inventory_menu()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == len(inventory_files) - 1:  # Create New Player
                            inventory_name = self.get_new_inventory_name()
                            if inventory_name.strip() != "":
                                return inventory_name
                        else:
                            inventory_name = re.split(pattern=r'\.json', string=inventory_files[self.selected_option])[0]
                            return inventory_name

    def draw_inventory_menu(self):
        self.screen.fill((0, 0, 0))
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.selected_option else (128, 128, 128)
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + i * 50))
            self.screen.blit(text, text_rect)
        pygame.display.flip()

    @staticmethod
    def get_new_world_name():
        world_name = input("\nEnter new world name: ")
        while world_name == "":
            print("\nInvalid new world name")
            world_name = input("\nEnter new world name: ")
        return world_name

    @staticmethod
    def get_new_inventory_name():
        inventory_name = input("\nEnter new player name: ")
        while inventory_name == "":
            print("\nInvalid new player name")
            inventory_name = input("\nEnter new player name: ")
        return inventory_name

    def save_and_quit(self):
        if not self.menu_active:
            self.scene.save_world_to_json(self.world_name)
            self.scene.inventory.save_inventory_to_json(self.inventory_name)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
