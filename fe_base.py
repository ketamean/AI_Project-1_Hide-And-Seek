import pyray as rl
import random
import fe_menu
import problem
import player

# -------------------ELEMENTS-------------------
MAP_TILE_SIZE = 20
PLAYER_SIZE = 20
PLAYER_TILE_VISIBILITY = 3  # Tiles around player that will be visible

# ----------------MAP STRUCTURES----------------
prob = problem.Problem(input_filename='map1_1.txt', allow_move_obstacles=False)
MAP_NUM_COL = prob.num_col
MAP_NUM_ROW = prob.num_row
SCREEN_WIDTH = MAP_TILE_SIZE * MAP_NUM_COL
SCREEN_HEIGHT = MAP_TILE_SIZE * MAP_NUM_ROW


class Map:
    def __init__(self):
        self.tiles_row = 0  # Number of tiles in row
        self.tiles_col = 0  # Number of tiles in col
        self.tileIds = None  # Tile ids (tiles_col*tiles_row), defines type of tile to draw
        self.tileFog = None  # Tile fog state (tiles_col*tiles_row), defines if a tile has fog or half-fog

    def draw(self):
        for row in range(self.tiles_row):
            for col in range(self.tiles_col):
                # Draw map tiles (depending on tile id)
                rl.draw_rectangle(col * MAP_TILE_SIZE, row * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                  rl.BLACK if self.tileIds[row * self.tiles_col + col] == 2  # Wall(s)
                                  else rl.GREEN if self.tileIds[row * self.tiles_col + col] == 3  # Hider(s)
                                  else rl.BLUE)  # Default tile
                # Draw grid
                rl.draw_rectangle_lines(col * MAP_TILE_SIZE, row * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                        rl.fade(rl.DARKBLUE, 0.5))


class Obstacle:
    def __init__(self, id_r_topleft, id_c_topleft, id_r_botright, id_c_botright) -> None:
        self.id_row_topleft = id_r_topleft
        self.id_col_topleft = id_c_topleft
        self.id_row_botright = id_r_botright
        self.id_col_botright = id_c_botright


@staticmethod
class Seeker:
    def __init__(self, row, col):
        # col and row are the pixel coordinates of the seeker (ex: tile 2,2 -> col=40, row=40)
        # Convert pixel coordinates to tile coordinates
        tilecol = col * MAP_TILE_SIZE
        tilerow = row * MAP_TILE_SIZE
        self.position = rl.Vector2(tilecol, tilerow)
        self.tile_col = col
        self.tile_row = row

    def move(self, dx, dy, my_map: Map):
        self.position.x += dx
        self.position.y += dy

        # Ensure player stays within the map boundaries
        self.position.x = max(0, min(self.position.x, my_map.tiles_col * MAP_TILE_SIZE - PLAYER_SIZE))
        self.position.y = max(0, min(self.position.y, my_map.tiles_row * MAP_TILE_SIZE - PLAYER_SIZE))

        # Update player tile position
        self.tile_col = int((self.position.x + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)
        self.tile_row = int((self.position.y + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)

    def draw(self):
        rl.draw_rectangle_v(self.position, rl.Vector2(PLAYER_SIZE, PLAYER_SIZE), rl.RED)


class Hider:
    def __init__(self, row, col):
        self.position = rl.Vector2(col, row)
        tilecol = col * MAP_TILE_SIZE
        tilerow = row * MAP_TILE_SIZE
        self.position = rl.Vector2(tilecol, tilerow)
        self.tile_col = col
        self.tile_row = row

    def draw(self, if_found):
        rl.draw_rectangle_v(self.position, rl.Vector2(PLAYER_SIZE, PLAYER_SIZE), rl.ORANGE if if_found else rl.GREEN)
    
    def if_found(self, seeker):
        if self.tile_col == seeker.tile_col and self.tile_row == seeker.tile_row:
            return True


def handle_input(map, seeker) -> None:
    if rl.is_key_pressed(rl.KEY_RIGHT) and rl.is_key_pressed(rl.KEY_DOWN):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col + 1] != 2:
            seeker.move(PLAYER_SIZE, PLAYER_SIZE, map)
    elif rl.is_key_pressed(rl.KEY_RIGHT) and rl.is_key_pressed(rl.KEY_UP):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col + 1] != 2:
            seeker.move(PLAYER_SIZE, -PLAYER_SIZE, map)
    elif rl.is_key_pressed(rl.KEY_LEFT) and rl.is_key_pressed(rl.KEY_DOWN):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col - 1] != 2:
            seeker.move(-PLAYER_SIZE, PLAYER_SIZE, map)
    elif rl.is_key_pressed(rl.KEY_LEFT) and rl.is_key_pressed(rl.KEY_UP):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col - 1] != 2:
            seeker.move(-PLAYER_SIZE, -PLAYER_SIZE, map)
    elif rl.is_key_pressed(rl.KEY_RIGHT):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col + 1] != 2:
            seeker.move(PLAYER_SIZE, 0, map)
    elif rl.is_key_pressed(rl.KEY_LEFT):
        if map.tileIds[seeker.tile_row * map.tiles_col + seeker.tile_col - 1] != 2:
            seeker.move(-PLAYER_SIZE, 0, map)
    elif rl.is_key_pressed(rl.KEY_DOWN):
        # for going down, a bonus list index out of range check is needed
        if (seeker.tile_row + 1) < map.tiles_row and map.tileIds[
            (seeker.tile_row + 1) * map.tiles_col + seeker.tile_col] != 2:
            seeker.move(0, PLAYER_SIZE, map)
    elif rl.is_key_pressed(rl.KEY_UP):
        if map.tileIds[(seeker.tile_row - 1) * map.tiles_col + seeker.tile_col] != 2:
            seeker.move(0, -PLAYER_SIZE, map)
def main():
    screenWidth = SCREEN_WIDTH
    screenHeight = SCREEN_HEIGHT

    rl.init_window(screenWidth, screenHeight, "Hide and Seek")

    rl.set_target_fps(30)
    map = Map()
    map.tiles_col = MAP_NUM_COL
    map.tiles_row = MAP_NUM_ROW

    # Opt for a list of 0s instead of calloc
    map.tileIds = [0] * (map.tiles_col * map.tiles_row)
    map.tileFog = [0] * (map.tiles_col * map.tiles_row)

    # NOTE: Map tile ids should be probably loaded from an external map file (by definition: 0: empty, 1: obstacle (
    # yellow), 2: wall (static, black)) Load map tiles (generating 2 random tile ids for testing)
    hiders = []
    for i in range(0, prob.num_row):
        for j in range(0, prob.num_col):
            if prob.map_list[i][j][0] == 1000:
                map.tileIds[i * prob.num_col + j] = 0
            elif prob.map_list[i][j][0] == -1:
                map.tileIds[i * prob.num_col + j] = 2
            elif type(prob.map_list[i][j][0]) == player.Seeker:
                seeker = Seeker(i, j)
            elif type(prob.map_list[i][j][0]) == player.Hider:
                hiders.append(Hider(i, j))

    # Seeker position in the map (default tile: 0,0)

    # Create a render texture to store the fog of war
    fogOfWar = rl.load_render_texture(map.tiles_col, map.tiles_row)
    rl.set_texture_filter(fogOfWar.texture, rl.TEXTURE_FILTER_BILINEAR)

    rl.set_target_fps(30)

    while not rl.window_should_close():
        # --------USER CONTROL MOVEMENT (ONLY FOR DEBUGGING) --------
        user_control = True
        if user_control:
            handle_input(map, seeker)
        # --------FILE INPUT MOVEMENT--------

        # Previous visited tiles are set to partial fog
        for i in range(map.tiles_row * map.tiles_col):
            if map.tileFog[i] == 1:
                map.tileFog[i] = 2 

        # Check visibility and update fog
        # NOTE: It is important to check tilemap limits to avoid processing tiles out-of-array-bounds (it could crash program)
        for row in range(max(0, seeker.tile_row - PLAYER_TILE_VISIBILITY), min(map.tiles_row, seeker.tile_row + PLAYER_TILE_VISIBILITY + 1)):
            for col in range(max(0, seeker.tile_col - PLAYER_TILE_VISIBILITY), min(map.tiles_col, seeker.tile_col + PLAYER_TILE_VISIBILITY + 1)):
                map.tileFog[row * map.tiles_col + col] = 1  # Set tile to visible
                # Due to a problem with x and y cords turned into tiles, 
                # the edge of the map is visible when seeker is at the edge on the opposite side
                # CURRENTLY UNFIXABLE
                    
        # -----------------------------RENDERING-----------------------------
        # TEXTURE
        rl.begin_texture_mode(fogOfWar)
        rl.clear_background(rl.BLANK)
        for row in range(map.tiles_row):
            for col in range(map.tiles_col):
                if map.tileFog[row * map.tiles_col + col] == 0:
                    rl.draw_rectangle(col, row, 1, 1, rl.fade(rl.BLACK, 0.8))
                elif map.tileFog[row * map.tiles_col + col] == 2:
                    rl.draw_rectangle(col, row, 1, 1, rl.fade(rl.BLACK, 0.6))
        rl.end_texture_mode()

        # DRAWING ELEMENTS
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        map.draw()
        seeker.draw()

        # Draw fog (scaled to full map, bilinear filtering)
        rl.draw_texture_pro(fogOfWar.texture, rl.Rectangle(0, 0, fogOfWar.texture.width, -fogOfWar.texture.height),
                            rl.Rectangle(0, 0, map.tiles_col * MAP_TILE_SIZE, map.tiles_row * MAP_TILE_SIZE),
                            rl.Vector2(0, 0), 0.0, rl.WHITE)

        # Write current player position tile
        rl.draw_text(f"Current tile: [{seeker.tile_row},{seeker.tile_col}]", 10, 10, 20, rl.RAYWHITE)

        # Check if hider is found
        for hider in hiders:
            if hider.if_found(seeker):
                hider.draw(True)
            else:
                hider.draw(False)
        
        if user_control:
            rl.draw_text("ARROW KEYS to move", 10, screenHeight - 25, 20, rl.RAYWHITE)
        else:
            rl.draw_text("FILE INPUT to move", 10, screenHeight - 25, 20, rl.RAYWHITE)

        rl.end_drawing()

    rl.unload_render_texture(fogOfWar)
    rl.close_window()


if __name__ == "__main__":
    # Menu
    fe_menu.main_menu()
    main()