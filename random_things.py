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
