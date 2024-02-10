import pygame as pygame
import os
import math
import sys

from global_constants import *
from event_manager import EventManager
from scene import Scene


class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()
        self.start_time = 0

        self.running = True

        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)

        world_file_path, inventory_file_path = self.choose_world_and_inventory_files()

        self.scene = Scene(screen=self.screen, world_file_path=world_file_path, inventory_file_path=inventory_file_path)

        self.font = pygame.font.Font(filename=None, size=60)

    def run(self):
        dt = 0
        while self.running:
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

                    pygame.quit()

                    save_world = input("Do you want to save the world? (yes/no): ")
                    if save_world.lower() == "yes" or save_world.lower() == "y":
                        self.scene.save_world_to_json()  # Save chunks before quitting

                    save_inventory = input("Do you want to save the inventory? (yes/no): ")
                    if save_inventory.lower() == "yes" or save_inventory.lower() == "y":
                        self.scene.inventory.save_inventory_to_json()  # Save inventory before quitting

                    sys.exit()

            self.scene.draw(dt=dt)
            self.screen.blit(
                self.font.render(text=f"FPS: {math.floor(self.clock.get_fps())}", antialias=True, color="white"),
                dest=(WINDOW_WIDTH - 200, 10))
            pygame.display.update()
            self.clock.tick(FRAMES_PER_SECOND)

    @staticmethod
    def choose_world_and_inventory_files():
        world_files = os.listdir('world_save_files')
        inventory_files = os.listdir('inventory_save_files')

        print("Available world files:")
        for i, file in enumerate(world_files, start=1):
            print(f"{i}. {file}")

        print("\nAvailable inventory files:")
        for i, file in enumerate(inventory_files, start=1):
            print(f"{i}. {file}")

        world_choice = input("\nChoose a world file (press Enter for new world): ")
        if world_choice.strip() == "":
            world_file_path = None
        else:
            world_choice_index = int(world_choice) - 1
            world_file_path = os.path.join('world_save_files', world_files[world_choice_index])

        inventory_choice = input("\nChoose an inventory file (press Enter for new inventory): ")
        if inventory_choice.strip() == "":
            inventory_file_path = None
        else:
            inventory_choice_index = int(inventory_choice) - 1
            inventory_file_path = os.path.join('inventory_save_files', inventory_files[inventory_choice_index])

        return world_file_path, inventory_file_path


if __name__ == "__main__":
    Game().run()
