# import ez_profile
import shutil
import string

import pygame
import sys
import re

from text_input import TextInput
from scene import *
from client import Client


class Game:
    def __init__(self):
        if not os.path.exists(path=PLAYER_SAVE_FOLDER):
            os.makedirs(name=PLAYER_SAVE_FOLDER)
        if not os.path.exists(path=WORLD_SAVE_FOLDER):
            os.makedirs(name=WORLD_SAVE_FOLDER)
        pygame.init()
        pygame.mixer.init()

        self.playing_menu_music = False
        self.playing_game_music = False
        self.menu_music = pygame.mixer.Sound(file="assets/sound/menu.mp3")
        self.game_music = pygame.mixer.Sound(file="assets/sound/background.mp3")

        self.menu_active = True
        self.menu_font = pygame.font.Font(filename=None, size=40)
        self.game_font = pygame.font.Font(filename=None, size=60)
        self.text_input = TextInput()
        self.__client = Client()
        self.__username = None

        self.__clock = pygame.time.Clock()
        self.start_time = 0
        self.running = True

        # self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        # TODO: uncomment code
        self.screen = pygame.display.set_mode(size=(0, 0), flags=pygame.FULLSCREEN, vsync=1)

        self.__menu_state_stack = ["login or register"]  # TODO: change to "login or register"

        self.__world_name = None
        self.__player_name = None

        self.__scene = None

    def get_player_name(self):
        return self.__player_name

    def get_world_name(self):
        return self.__world_name

    def run(self):
        dt = 0
        invincibility_duration = 1000  # Duration of invincibility
        invincibility_end_time = pygame.time.get_ticks() + invincibility_duration
        while self.running:
            self.__menu_events()

            if self.start_time == 0:
                self.start_time = pygame.time.get_ticks()  # Start the timer when the player selects world and inventory

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time

            buffer_time = 100  # To ensure player starts off above ground

            # if elapsed_time >= buffer_time:
            #     dt = self.__clock.tick(FRAMES_PER_SECOND) / 1000

            player = self.__scene.get_player()

            if current_time <= invincibility_end_time:
                player.set_health(health=MAX_HEALTH)

            dt = 1
            self.__scene.update_draw(dt=dt)
            self.screen.fblits([(self.game_font.render(text=f"FPS: {math.floor(self.__clock.get_fps())}", antialias=True, color="white"), (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 50))])
            pygame.display.update()
            self.__clock.tick(FRAMES_PER_SECOND)

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.return_to_main_menu()

            if player.get_health() <= 0:
                player.death_screen(screen=self.screen)
                self.return_to_main_menu()

    def __quit_game(self):
        # TODO: uncomment code
        self.running = False
        if self.__menu_state_stack[-1] == "game":
            inventory = self.__scene.get_inventory()
            inventory.save_inventory_to_json()
            self.__scene.save_world_to_json()
            self.__client.upload_files(username=self.__username, player_file_path=self.__player_name, world_file_path=self.__world_name)
        shutil.rmtree(WORLD_SAVE_FOLDER)
        shutil.rmtree(PLAYER_SAVE_FOLDER)
        pygame.quit()
        sys.exit()

    def return_to_main_menu(self):
        # TODO: uncomment code
        self.playing_game_music = False
        self.game_music.stop()

        self.__menu_state_stack.clear()
        self.__menu_state_stack.append("main menu")

        inventory = self.__scene.get_inventory()
        inventory.save_inventory_to_json()
        self.__scene.save_world_to_json()
        self.__client.upload_files(username=self.__username, player_file_path=self.__player_name,
                                   world_file_path=self.__world_name)

        self.__scene = None
        self.start_time = 0
        self.menu_active = True

    def __menu_events(self):
        while self.menu_active:
            if not self.playing_menu_music:
                self.menu_music.play(loops=-1)
                self.playing_menu_music = True

            if self.__menu_state_stack[-1] == "login or register":
                self.login_register_selection()

            elif self.__menu_state_stack[-1] == "login username":
                self.login_username_menu()
            elif self.__menu_state_stack[-1] == "login password":
                self.login_password_menu()

            elif self.__menu_state_stack[-1] == "register username":
                self.register_username_menu()
            elif self.__menu_state_stack[-1] == "register password":
                self.register_password_menu()

            elif self.__menu_state_stack[-1] == "reset password username":
                self.reset_password_username_menu()
            elif self.__menu_state_stack[-1] == "reset password recovery code":
                self.reset_password_recovery_code_menu()
            elif self.__menu_state_stack[-1] == "reset password new password":
                self.reset_password_new_password_menu()

            elif self.__menu_state_stack[-1] == "main menu":
                self.main_menu_selection()

            elif self.__menu_state_stack[-1] == "controls":
                self.controls_menu()

            elif self.__menu_state_stack[-1] == "player selection":
                self.player_menu()
            elif self.__menu_state_stack[-1] == "create new player":
                self.new_player_menu()

            elif self.__menu_state_stack[-1] == "world selection":
                self.world_menu()
            elif self.__menu_state_stack[-1] == "create new world":
                self.new_world_menu()

            elif self.__menu_state_stack[-1] == "game":
                self.menu_active = False
                self.__scene = Scene(game=self)
                if not self.playing_game_music:
                    self.playing_menu_music = False
                    self.menu_music.stop()
                    self.game_music.play(loops=-1)
                    self.playing_game_music = True

    def menu_draw(self, menu_options, selected_option, menu_type=None):
        self.screen.fill(color="black")

        if menu_type:
            text = self.menu_font.render(text=f"{menu_type}", antialias=True, color="#39a5d4")
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.fblits([(text, text_rect)])

        total_menu_height = len(menu_options) * 50
        start_y = (WINDOW_HEIGHT - total_menu_height) // 2

        for number, option in enumerate(menu_options):
            colour = "white" if number == selected_option else "#808080"
            text = self.menu_font.render(text=option, antialias=True, color=colour)
            if option == "Back":
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            else:
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, start_y + number * 50))
            self.screen.fblits([(text, text_rect)])
        pygame.display.flip()

    def sub_menu_draw(self, menu_options, selected_option, menu_type, detail_type=None):
        self.screen.fill(color="black")

        text = self.menu_font.render(text=menu_type, antialias=True, color="#39a5d4")
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.fblits([(text, text_rect)])

        if detail_type is not None:
            text = self.menu_font.render(text=f"Enter {menu_type} {detail_type}:", antialias=True,
                                         color="white")
        else:
            text = self.menu_font.render(text=f"Enter New {menu_type}:", antialias=True, color="white")
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - WINDOW_HEIGHT // 5))
        self.screen.fblits([(text, text_rect)])

        for number, option in enumerate(menu_options):
            if option == "Text Box":
                self.text_input.draw(screen=self.screen)
            elif option == "Back":
                colour = "white" if number == selected_option else "#808080"
                text = self.menu_font.render(text=option, antialias=True, color=colour)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                self.screen.fblits([(text, text_rect)])
        pygame.display.flip()

    def validate_username_text_input(self):
        if 5 <= len(self.__username) <= 20:
            return True

    @staticmethod
    def validate_password_text_input(password):
        create_password_lower = False
        create_password_upper = False
        create_password_number = False
        create_password_special = False
        if 5 <= len(password) <= 64:
            for character in password:
                if character in string.ascii_lowercase:
                    create_password_lower = True
                if character in string.ascii_uppercase:
                    create_password_upper = True
                if character in string.digits:
                    create_password_number = True
                if character in string.punctuation + " ":
                    create_password_special = True
        if create_password_lower and create_password_upper and create_password_number and create_password_special:
            return True

    def validate_player_text_input(self):
        if self.__player_name is not None:
            if 5 <= len(self.__player_name) <= 20:
                return True

    def validate_world_text_input(self):
        if self.__world_name is not None:
            if 5 <= len(self.__world_name) <= 20:
                return True
    def login_register_selection(self):
        menu_options = ["Login", "Register", "Forgot Password", "Quit"]
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
                        if selected_option == 0:  # Login
                            self.__menu_state_stack.append("login username")
                            return
                        elif selected_option == 1:  # Register
                            self.__menu_state_stack.append("register username")
                            return
                        elif selected_option == 2:
                            self.__menu_state_stack.append("reset password username")
                            return
                        elif selected_option == 3:  # Quit
                            self.__quit_game()

    def login_username_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Login", detail_type="Username")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.__username = self.text_input.input_text
                            self.__menu_state_stack.append("login password")
                            return

            self.text_input.update(validation_type="short")

    def login_password_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Login", detail_type="Password")

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            password = self.text_input.input_text
                            if self.__client.authenticate_user(username=self.__username, password=password):
                                # TODO: uncomment code
                                self.__client.download_files(username=self.__username)

                                success_text = self.menu_font.render(
                                    text="Login successful",
                                    antialias=True,
                                    color="green")
                                success_rect = success_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                self.screen.fill(color="black")
                                self.screen.fblits([(success_text, success_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.clear()
                                self.__menu_state_stack.append("main menu")
                                return
                            else:
                                success_text = self.menu_font.render(
                                    text="Invalid username and/or password",
                                    antialias=True,
                                    color="red")
                                success_rect = success_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                self.screen.fill(color="black")
                                self.screen.fblits([(success_text, success_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.pop()  # Removes "login password"
                                self.__menu_state_stack.pop()  # Removes "login username"
                                return

            self.text_input.update(validation_type="long")

    def register_username_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Register", detail_type="Username")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.__username = self.text_input.input_text
                            if self.validate_username_text_input():
                                self.__menu_state_stack.append("register password")
                                return
                            else:
                                criteria_fail_text = self.menu_font.render(
                                    text="Username does not meet the following criteria:",
                                    antialias=True,
                                    color="red")
                                criteria_fail_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))

                                criteria_text = self.menu_font.render(
                                    text="Between 5 and 20 characters",
                                    antialias=True, color="red")
                                criteria_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

                                self.screen.fill(color="black")
                                self.screen.fblits([(criteria_fail_text, criteria_fail_rect)])
                                self.screen.fblits([(criteria_text, criteria_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.pop()  # Removes "register username"
                                return

            self.text_input.update(validation_type="short")

    def register_password_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Register", detail_type="Password")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            password = self.text_input.input_text
                            if self.validate_password_text_input(password=password):
                                registration_successful, recovery_code = self.__client.register_user(username=self.__username, password=password)
                                if registration_successful and recovery_code is not None:
                                    success_text = self.menu_font.render(
                                        text="Registration successful",
                                        antialias=True,
                                        color="green")
                                    success_rect = success_text.get_rect(
                                        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))

                                    recovery_code_text = self.menu_font.render(
                                        text=f"Your recovery code is: {recovery_code}",
                                        antialias=True,
                                        color="green")
                                    recovery_code_rect = recovery_code_text.get_rect(
                                        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))

                                    self.screen.fill(color="black")
                                    self.screen.fblits([(success_text, success_rect)])
                                    self.screen.fblits([(recovery_code_text, recovery_code_rect)])
                                    pygame.display.flip()

                                    pygame.time.delay(8000)

                                    self.__menu_state_stack.pop()  # Removes "register password"
                                    self.__menu_state_stack.pop()  # Removes "register username"
                                else:
                                    success_text = self.menu_font.render(
                                        text="Username already exists",
                                        antialias=True,
                                        color="red")
                                    success_rect = success_text.get_rect(
                                        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                    self.screen.fill(color="black")
                                    self.screen.fblits([(success_text, success_rect)])
                                    pygame.display.flip()
                                    pygame.time.delay(2000)

                                    self.__menu_state_stack.pop()  # Removes "register password"
                                    self.__menu_state_stack.pop()  # Removes "register username"
                            else:
                                criteria_fail_text = self.menu_font.render(
                                    text="Password does not meet the following criteria:",
                                    antialias=True,
                                    color="red")
                                criteria_fail_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
                                criteria_text = self.menu_font.render(
                                    text="Between 5 and 64 characters\nLowercase letter\nUppercase letter\nNumber\nSpecial character",
                                    antialias=True, color="red")
                                criteria_rect = criteria_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
                                self.screen.fill(color="black")
                                self.screen.fblits([(criteria_fail_text,
                                                 criteria_fail_rect)])
                                self.screen.fblits([(criteria_text, criteria_rect)])
                                pygame.display.flip()
                                pygame.time.delay(5000)

                                self.__menu_state_stack.pop()  # Removes "register password"
                                self.__menu_state_stack.pop()  # Removes "register username"
                            return

            self.text_input.update(validation_type="long")

    def reset_password_username_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Reset Password", detail_type="Username")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.__username = self.text_input.input_text
                            self.__menu_state_stack.append("reset password recovery code")
                            return

            self.text_input.update(validation_type="short")

    def reset_password_recovery_code_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Reset Password", detail_type="Recovery Code")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            recovery_code = self.text_input.input_text
                            if self.__client.authenticate_recovery_code(username=self.__username, recovery_code=recovery_code):

                                success_text = self.menu_font.render(
                                    text="Recovery code valid",
                                    antialias=True,
                                    color="green")
                                success_rect = success_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                self.screen.fill(color="black")
                                self.screen.fblits([(success_text, success_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.append("reset password new password")
                            else:
                                success_text = self.menu_font.render(
                                    text="Username and/or recovery code invalid",
                                    antialias=True,
                                    color="red")
                                success_rect = success_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                                self.screen.fill(color="black")
                                self.screen.fblits([(success_text, success_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.pop()  # Removes "reset password recovery code"
                                self.__menu_state_stack.pop()  # Removes "reset password username"
                            return

            self.text_input.update(validation_type="long")

    def reset_password_new_password_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option,
                               menu_type="Reset Password", detail_type="New Password")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            new_password = self.text_input.input_text
                            if self.validate_password_text_input(password=new_password):
                                new_password_successful, recovery_code = self.__client.reset_password(username=self.__username, new_password=new_password)
                                if new_password_successful and recovery_code is not None:
                                    success_text = self.menu_font.render(
                                        text="Password reset",
                                        antialias=True,
                                        color="green")
                                    success_rect = success_text.get_rect(
                                        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))

                                    recovery_code_text = self.menu_font.render(
                                        text=f"Your new recovery code is: {recovery_code}",
                                        antialias=True,
                                        color="green")
                                    recovery_code_rect = recovery_code_text.get_rect(
                                        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))

                                    self.screen.fill(color="black")
                                    self.screen.fblits([(success_text, success_rect)])
                                    self.screen.fblits([(recovery_code_text, recovery_code_rect)])
                                    pygame.display.flip()
                                    pygame.time.delay(8000)

                                    self.__menu_state_stack.pop()  # Removes "reset password new password"
                                    self.__menu_state_stack.pop()  # Removes "reset password recovery code"
                                    self.__menu_state_stack.pop()  # Removes "reset password username"
                                return
                            else:
                                criteria_fail_text = self.menu_font.render(
                                    text="Password does not meet the following criteria:",
                                    antialias=True,
                                    color="red")
                                criteria_fail_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
                                criteria_text = self.menu_font.render(
                                    text="Between 5 and 64 characters\nLowercase letter\nUppercase letter\nNumber\nSpecial character",
                                    antialias=True, color="red")
                                criteria_rect = criteria_text.get_rect(
                                    # Use criteria_text here instead of criteria_fail_text
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
                                self.screen.fill(color="black")
                                self.screen.fblits([(criteria_fail_text,
                                                     criteria_fail_rect)])
                                self.screen.fblits([(criteria_text, criteria_rect)])
                                pygame.display.flip()
                                pygame.time.delay(5000)
                                return

            self.text_input.update(validation_type="long")

    def main_menu_selection(self):
        menu_options = ["Play", "Controls", "Quit"]
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
                            self.__menu_state_stack.append("player selection")
                            return
                        elif selected_option == 1:
                            self.__menu_state_stack.append("controls")
                            return
                        elif selected_option == 2:
                            self.__quit_game()

    def controls_menu(self):
        menu_options = ["Back"]
        selected_option = 0

        while True:
            self.controls_menu_draw(menu_options=menu_options, selected_option=selected_option)
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return

    def controls_menu_draw(self, menu_options, selected_option):
        self.screen.fill(color="black")

        text = self.menu_font.render(text="Controls", antialias=True, color="#39a5d4")
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.fblits([(text, text_rect)])

        all_controls = {
            "Move Left": "A",
            "Move Right": "D",
            "Jump": "SPACE",
            "Break Block": "Left Mouse Button",
            "Place Block": "Right Mouse Button",
            "Attack": "Right Mouse Button",
            "Eat": "Right Mouse Button",
            "Toggle Inventory": "E",
            "Navigate Inventory": "Scroll Wheel / 1-9",
            "Swap Items": "Right Mouse Button",
            "Quit Game": "ESCAPE"
        }

        # Calculate the maximum width of the action texts
        max_action_width = max(self.menu_font.size(action)[0] for action in all_controls.keys())

        x_left = WINDOW_WIDTH // 4  # Action column (left side)
        x_right = 3 * (WINDOW_WIDTH // 4)  # Button column (right side)
        line_height = 50

        total_height = len(all_controls) * line_height
        y_start = (WINDOW_HEIGHT - total_height) // 2

        for number, (action, button) in enumerate(all_controls.items()):
            y = y_start + number * line_height

            action_text = self.menu_font.render(text=action, antialias=True, color="white")
            action_rect = action_text.get_rect(midleft=(x_left, y))
            self.screen.fblits([(action_text, action_rect)])

            # Determine the x position for the button texts
            x_button = x_right - max_action_width  # Align buttons to the right side

            button_text = self.menu_font.render(text=button, antialias=True, color="white")
            button_rect = button_text.get_rect(midleft=(x_button, y))
            self.screen.fblits([(button_text, button_rect)])

        for number, option in enumerate(menu_options):
            if option == "Back":
                colour = "white" if number == selected_option else "#808080"
                text = self.menu_font.render(text=option, antialias=True, color=colour)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                self.screen.fblits([(text, text_rect)])

        pygame.display.flip()

    def player_menu(self):
        inventory_files = os.listdir(path=PLAYER_SAVE_FOLDER)
        inventory_files.append("Create New Player")
        inventory_files.append("Back")

        menu_options = [re.split(pattern=r"\.json", string=file)[0] for file in inventory_files]
        selected_option = 0

        while True:
            self.menu_draw(menu_options=menu_options, selected_option=selected_option, menu_type="Player")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == len(inventory_files) - 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == len(inventory_files) - 2:  # Create New Player
                            self.__menu_state_stack.append("create new player")
                            return
                        else:
                            self.__player_name = re.split(pattern=r"\.json", string=inventory_files[selected_option])[0]
                            self.__menu_state_stack.append("world selection")
                            return

    def new_player_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option, menu_type="Player")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.__player_name = self.text_input.input_text
                            if self.validate_player_text_input():
                                self.__menu_state_stack.append("world selection")
                            else:
                                criteria_fail_text = self.menu_font.render(
                                    text="Player name does not meet the following criteria:",
                                    antialias=True,
                                    color="red")
                                criteria_fail_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))

                                criteria_text = self.menu_font.render(
                                    text="Between 5 and 20 characters",
                                    antialias=True, color="red")
                                criteria_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

                                self.screen.fill(color="black")
                                self.screen.fblits([(criteria_fail_text, criteria_fail_rect)])
                                self.screen.fblits([(criteria_text, criteria_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.pop()
                            return

            self.text_input.update(validation_type="short")

    def world_menu(self):
        world_files = os.listdir(path=WORLD_SAVE_FOLDER)
        world_files.append("Create New World")
        world_files.append("Back")

        menu_options = [re.split(pattern=r"\.json", string=file)[0] for file in world_files]
        selected_option = 0

        while True:
            self.menu_draw(menu_options=menu_options, selected_option=selected_option, menu_type="World")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == len(world_files) - 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == len(world_files) - 2:  # Create New World
                            self.__menu_state_stack.append("create new world")
                            return
                        else:
                            self.__world_name = re.split(pattern=r"\.json", string=world_files[selected_option])[0]
                            self.__menu_state_stack.append("game")
                            return

    def new_world_menu(self):
        menu_options = ["Text Box", "Back"]
        selected_option = 0

        self.text_input.input_text = ""
        self.text_input.active = True

        while True:
            self.sub_menu_draw(menu_options=menu_options, selected_option=selected_option, menu_type="World")
            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = abs((selected_option - 1)) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = abs((selected_option + 1)) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 1:  # Back
                            self.__menu_state_stack.pop()  # Remove the last menu state from the stack
                            return
                        elif selected_option == 0:  # Text Box
                            self.__world_name = self.text_input.input_text
                            if self.validate_world_text_input():
                                self.__menu_state_stack.append("game")
                            else:
                                criteria_fail_text = self.menu_font.render(
                                    text="World name does not meet the following criteria:",
                                    antialias=True,
                                    color="red")
                                criteria_fail_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))

                                criteria_text = self.menu_font.render(
                                    text="Between 5 and 20 characters",
                                    antialias=True, color="red")
                                criteria_rect = criteria_fail_text.get_rect(
                                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))

                                self.screen.fill(color="black")
                                self.screen.fblits([(criteria_fail_text, criteria_fail_rect)])
                                self.screen.fblits([(criteria_text, criteria_rect)])
                                pygame.display.flip()
                                pygame.time.delay(2000)

                                self.__menu_state_stack.pop()
                            return

            self.text_input.update(validation_type="short")


if __name__ == "__main__":
    game = Game()
    game.run()
