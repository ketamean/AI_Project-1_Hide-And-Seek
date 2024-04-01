import pyray as rl


class Ball:
    def __init__(self, x, y, radius, speed_x, speed_y):
        self.radius = radius
        self.y = y
        self.x = x
        self.speed_x = speed_x
        self.speed_y = speed_y

    def draw(self) -> None:
        rl.draw_circle(self.x, self.y, self.radius, rl.WHITE)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Check for collision
        if self.y >= rl.get_screen_height() or self.y <= 0:
            self.speed_y *= -1
        if self.x >= rl.get_screen_width() or self.x <= 0:
            self.speed_x *= -1


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def draw(self):
        rl.draw_rectangle(self.x, self.y, self.width, self.height, rl.WHITE)

    def validate_xy(self):
        self.y = max(self.y, 0)
        self.y = min(self.y, screen_height - self.height)

    def handle_input(self):
        if rl.is_key_down(rl.KeyboardKey.KEY_UP):
            self.y -= self.speed
        elif rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            self.y += self.speed
        self.validate_xy()


class CPUPaddle(Paddle):
    def __init__(self, x, y, width, height, speed):
        super().__init__(x, y, width, height, speed)

    def update(self, ball_y):
        if self.y + self.height / 2 < ball_y:
            self.y += self.speed
        if self.y + self.height / 2 > ball_y:
            self.y -= self.speed
        self.validate_xy()


if __name__ == "__main__":
    screen_width = 1200
    screen_height = 800

    rl.init_window(screen_width, screen_height, "My Pong Game")
    rl.set_target_fps(60)

    ball = Ball(screen_width // 2, screen_height // 2, 20, 6, 7)
    player_paddle = Paddle(10, screen_height // 2 - 60, 25, 120, 6)
    cpu_paddle = CPUPaddle(screen_width - 10 - 25, screen_height // 2 - 60, 25, 120, 6)
    while not rl.window_should_close():
        # Event Handling

        # Update Positions
        ball.update()
        player_paddle.handle_input()
        cpu_paddle.update(ball.y)
        if rl.check_collision_circle_rec(rl.Vector2(ball.x, ball.y), ball.radius, rl.Rectangle(player_paddle.x, player_paddle.y, player_paddle.width, player_paddle.height)):
            ball.speed_x *= -1
        if rl.check_collision_circle_rec(rl.Vector2(ball.x, ball.y), ball.radius, rl.Rectangle(cpu_paddle.x, cpu_paddle.y, cpu_paddle.width, cpu_paddle.height)):
            ball.speed_x *= -1
        # Drawing
        rl.begin_drawing()
        player_paddle.draw()
        cpu_paddle.draw()
        rl.draw_line(screen_width // 2, 0, screen_width // 2, screen_height, rl.WHITE)
        ball.draw()
        rl.clear_background(rl.BLANK)
        rl.end_drawing()
    rl.close_window()
