# import ez_profile
# import shutil
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

        self.menu_active = True
        self.menu_font = pygame.font.Font(filename=None, size=40)
        self.game_font = pygame.font.Font(filename=None, size=60)
        self.text_input = TextInput()
        self.__client = Client()
        self.__username = None

        self.__clock = pygame.time.Clock()
        self.start_time = 0
        self.running = True
        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)

        self.__menu_state_stack = ["main menu"]  # TODO: change to "login or register"

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

            if elapsed_time >= buffer_time:
                dt = self.__clock.tick(FRAMES_PER_SECOND) / 1000

            player = self.__scene.get_player()

            if current_time <= invincibility_end_time:
                player.set_health(health=MAX_HEALTH)

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                    self.__quit_game()

            if player.get_health() <= 0:
                player.death_screen(game=self)
                self.__quit_game()

            self.__scene.update_draw(dt=dt)
            self.screen.fblits([(self.game_font.render(text=f"FPS: {math.floor(self.__clock.get_fps())}", antialias=True, color="white"), (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 50))])
            pygame.display.update()
            self.__clock.tick()

    def __quit_game(self):
        # TODO: uncomment code
        self.running = False
        if self.__player_name is not None and self.__world_name is not None:
            inventory = self.__scene.get_inventory()
            inventory.save_inventory_to_json()
            self.__scene.save_world_to_json()
            # self.__client.upload_files(username=self.__username, player_file_path=self.__player_name, world_file_path=self.__world_name)
        # shutil.rmtree(WORLD_SAVE_FOLDER)
        # shutil.rmtree(PLAYER_SAVE_FOLDER)
        pygame.quit()
        sys.exit()

    def __menu_events(self):
        while self.menu_active:
            if self.__menu_state_stack[-1] == "login or register":
                self.login_register_selection()

            elif self.__menu_state_stack[-1] == "login username":
                self.login_username_menu()
                if self.__menu_state_stack[-1] == "login password":
                    self.login_password_menu()
                    if "login username" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("login username")
                    if "login password" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("login password")

            elif self.__menu_state_stack[-1] == "register username":
                self.register_username_menu()
                if self.__menu_state_stack[-1] == "register password":
                    self.register_password_menu()
                    if "register username" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("register username")
                    if "register password" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("register password")

            elif self.__menu_state_stack[-1] == "main menu":
                self.main_menu_selection()

            elif self.__menu_state_stack[-1] == "player selection":
                self.player_menu_selection()
                if self.__menu_state_stack[-1] == "create new player":
                    self.new_player_menu_creation()
                    if "create new player" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("create new player")

            elif self.__menu_state_stack[-1] == "world selection":
                self.world_menu_selection()
                if self.__menu_state_stack[-1] == "create new world":
                    self.new_world_menu_creation()
                    if "create new world" in self.__menu_state_stack:
                        self.__menu_state_stack.remove("create new world")

            elif self.__menu_state_stack[-1] == "game":
                self.menu_active = False
                self.__scene = Scene(game=self)

    def menu_draw(self, menu_options, selected_option, menu_type=None):
        self.screen.fill((0, 0, 0))

        if menu_type:
            text = self.menu_font.render(text=f"{menu_type}", antialias=True, color="#39a5d4")
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.fblits([(text, text_rect)])

        for number, option in enumerate(menu_options):
            colour = (255, 255, 255) if number == selected_option else (128, 128, 128)
            text = self.menu_font.render(text=option, antialias=True, color=colour)
            text_rect = text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)) if option == "Back" else text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + number * 50))
            self.screen.fblits([(text, text_rect)])
        pygame.display.flip()

    def sub_menu_draw(self, menu_options, selected_option, menu_type, detail_type=None):
        self.screen.fill((0, 0, 0))

        text = self.menu_font.render(text=menu_type, antialias=True, color="#39a5d4")
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.fblits([(text, text_rect)])

        if detail_type is not None:
            text = self.menu_font.render(text=f"Enter {menu_type} {detail_type}:", antialias=True,
                                         color=(255, 255, 255))
        else:
            text = self.menu_font.render(text=f"Enter New {menu_type}:", antialias=True, color=(255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - WINDOW_HEIGHT // 5))
        self.screen.fblits([(text, text_rect)])

        for number, option in enumerate(menu_options):
            if option == "Text Box":
                self.text_input.draw(screen=self.screen)
            elif option == "Back":
                colour = (255, 255, 255) if number == selected_option else (128, 128, 128)
                text = self.menu_font.render(text=option, antialias=True, color=colour)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
                self.screen.fblits([(text, text_rect)])
        pygame.display.flip()

    def login_register_selection(self):
        menu_options = ["Login", "Register", "Quit"]
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
                        elif selected_option == 2:  # Quit
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
                            self.__username = self.text_input.input_text.strip()
                            self.__menu_state_stack.append("login password")
                            return

            self.text_input.update()

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
                            password = self.text_input.input_text.strip()
                            if self.__client.authenticate_user(username=self.__username, password=password):
                                if password:
                                    self.__client.download_files(username=self.__username)
                                    self.__menu_state_stack.append("main menu")
                                    return
                            else:
                                self.__menu_state_stack.pop()  # removes "login password"
                                self.__menu_state_stack.pop()  # removes "login username"
                                return

            self.text_input.update()

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
                            self.__username = self.text_input.input_text.strip()
                            self.__menu_state_stack.append("register password")
                            return

            self.text_input.update()

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
                            password = self.text_input.input_text.strip()
                            if self.__client.register_user(username=self.__username, password=password):
                                self.__menu_state_stack.append("login or register")
                                return
                            else:
                                self.__menu_state_stack.pop()  # removes "register password"
                                self.__menu_state_stack.pop()  # removes "register username"
                                return

            self.text_input.update()

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
                            self.__menu_state_stack.append("player selection")
                            return
                        elif selected_option == 1:
                            self.__quit_game()

    def player_menu_selection(self):
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

    def new_player_menu_creation(self):
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
                            self.__player_name = self.text_input.input_text.strip()
                            self.__menu_state_stack.append("world selection")
                            return

            self.text_input.update()

    def world_menu_selection(self):
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

    def new_world_menu_creation(self):
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
                            self.__world_name = self.text_input.input_text.strip()
                            self.__menu_state_stack.append("game")
                            return

            self.text_input.update()


if __name__ == "__main__":
    game = Game()
    game.run()
