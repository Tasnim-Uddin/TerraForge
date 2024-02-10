import pygame as pygame
import os
import math
import sys
import re

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

        self.world_name = self.world_choice()
        self.inventory_name = self.inventory_choice()

        self.scene = Scene(screen=self.screen, world_name=self.world_name, inventory_name=self.inventory_name)

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

                    self.scene.save_world_to_json(world_name=self.world_name)  # Save all chunks before quitting

                    self.scene.inventory.save_inventory_to_json(inventory_name=self.inventory_name)  # Save inventory before quitting

                    sys.exit()

            self.scene.draw(dt=dt)
            self.screen.blit(
                self.font.render(text=f"FPS: {math.floor(self.clock.get_fps())}", antialias=True, color="white"),
                dest=(WINDOW_WIDTH - 200, 10))
            pygame.display.update()
            self.clock.tick(FRAMES_PER_SECOND)

    @staticmethod
    def world_choice():
        world_files = os.listdir("world_save_files")

        print("Available world files:")
        for i, file in enumerate(world_files, start=1):
            print(f"{i}. {file}")

        world_choice = input("\nChoose a world file (press Enter for new world): ")
        if world_choice.strip() == "":
            world_name = input("\nEnter new world name: ")
            while world_name == "":
                print("\nInvalid new world name")
                world_name = input("\nEnter new world name: ")
        else:
            world_choice_index = int(world_choice) - 1
            world_name = world_files[world_choice_index]
            world_name = re.split(pattern=r'\.json', string=world_name)[0]

        return world_name

    @staticmethod
    def inventory_choice():
        inventory_files = os.listdir("player_save_files")
        print("\nAvailable inventory files:")
        for i, file in enumerate(inventory_files, start=1):
            print(f"{i}. {file}")

        inventory_choice = input("\nChoose a player file (press Enter for new inventory): ")
        if inventory_choice.strip() == "":
            inventory_name = input("\nEnter new player name: ")
            while inventory_name == "":
                print("\nInvalid new player name")
                inventory_name = input("\nEnter new player name: ")
        else:
            inventory_choice_index = int(inventory_choice) - 1
            inventory_name = inventory_files[inventory_choice_index]
            inventory_name = re.split(pattern=r'\.json', string=inventory_name)[0]

        return inventory_name


if __name__ == "__main__":
    Game().run()
