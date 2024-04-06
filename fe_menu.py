import pyray as rl


BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = rl.BLUE
BUTTON_HOVER_COLOR = rl.DARKBLUE
BUTTON_TEXT_COLOR = rl.WHITE

# LEVEL 
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3

class Button:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.is_hovered = False
    
    def if_hovered(self, mouse_x, mouse_y):
        if mouse_x >= self.x and mouse_x <= self.x + BUTTON_WIDTH and mouse_y >= self.y and mouse_y <= self.y + BUTTON_HEIGHT:
            self.is_hovered = True
        else:
            self.is_hovered = False
        
    def draw(self):
        if self.is_hovered:
            rl.draw_rectangle(self.x, self.y, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_HOVER_COLOR)
        else:
            rl.draw_rectangle(self.x, self.y, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR)
        rl.draw_text(self.text, self.x + BUTTON_WIDTH // 2 - rl.measure_text(self.text, 20) // 2, self.y + 10, 20, BUTTON_TEXT_COLOR)

class Menu:
    def __init__(self, title, window_height, window_width):
        self.window_height = window_height
        self.window_width = window_width
        self.title = title
        self.buttons = []
        
    def draw(self):
        rl.draw_text(self.title, self.window_width // 2 - rl.measure_text(self.title, 40) // 2, 50, 40, rl.WHITE)
        level1_button = Button(self.window_width // 2 - BUTTON_WIDTH // 2, self.window_height // 2 - BUTTON_HEIGHT // 2, "Level 1")
        level2_button = Button(self.window_width // 2 - BUTTON_WIDTH // 2, self.window_height // 2 - BUTTON_HEIGHT // 2 + 100, "Level 2")
        level3_button = Button(self.window_width // 2 - BUTTON_WIDTH // 2, self.window_height // 2 - BUTTON_HEIGHT // 2 + 200, "Level 3")
        buttons = [level1_button, level2_button, level3_button]
        
        for button in buttons:
            button.draw()
        
        # Update button hover state
        mouse_x = rl.get_mouse_x()
        mouse_y = rl.get_mouse_y()
        for button in buttons:
            button.if_hovered(mouse_x, mouse_y)
            for button in buttons:
                button.draw()
            
        # Check if button is clicked
        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            for button in buttons:
                if button.is_hovered:
                    print(f"{button.text} was clicked")
                    return int(button.text[-1])
        
def main_menu() -> int:
    screenWidth = 800
    screenHeight = 450

    rl.init_window(screenWidth, screenHeight, "Menu")

    rl.set_target_fps(30)

    menu = Menu("Main Menu", screenHeight, screenWidth)
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        level = menu.draw()
        if level:
            break
        
        rl.end_drawing()

    rl.close_window()
    return level

if __name__ == "__main__":
    main_menu()