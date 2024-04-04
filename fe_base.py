import pyray as rl
import random
import fe_menu
import problem
import player

#-------------------ELEMENTS-------------------
MAP_TILE_SIZE = 20
PLAYER_SIZE = 20
PLAYER_TILE_VISIBILITY = 3 # Tiles around player that will be visible

#----------------MAP STRUCTURES----------------
MAP_TILE_X = 15
MAP_TILE_Y = 20
SCREEN_WIDTH = MAP_TILE_SIZE * MAP_TILE_X
SCREEN_HEIGHT = MAP_TILE_SIZE * MAP_TILE_Y
prob = problem.Problem(input_filename='map1_1.txt',allow_move_obstacles=False)
class Map:
    def __init__(self):
        self.tilesX = 0 # Number of tiles in X axis
        self.tilesY = 0 # Number of tiles in Y axis
        self.tileIds = None # Tile ids (tilesX*tilesY), defines type of tile to draw 
        self.tileFog = None # Tile fog state (tilesX*tilesY), defines if a tile has fog or half-fog
        
    def draw(self):
        for y in range(self.tilesY):
            for x in range(self.tilesX):
                # Draw map tiles (depending on tile id)
                rl.draw_rectangle(x * MAP_TILE_SIZE, y * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                  rl.BLUE if self.tileIds[y * self.tilesX + x] == 0 # Default tile
                                  else rl.BLACK if self.tileIds[y * self.tilesX + x] == 2 # Wall(s)
                                  else rl.GREEN if self.tileIds[y * self.tilesX + x] == 3 # Hider(s)
                                  else rl.fade(rl.BLUE, 0.9)) # Default tile (but faded for asthetics)
                # Draw grid
                rl.draw_rectangle_lines(x * MAP_TILE_SIZE, y * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                         rl.fade(rl.DARKBLUE, 0.5))
    
class Obstacle:
    def __init__(self, id_r_topleft, id_c_topleft, id_r_botright, id_c_botright) -> None:
        self.id_row_topleft = id_r_topleft
        self.id_col_topleft = id_c_topleft
        self.id_row_botright = id_r_botright
        self.id_col_botright = id_c_botright
    
@staticmethod
class Seeker:
    def __init__(self, x, y):
        # x and y are the pixel coordinates of the seeker (ex: tile 2,2 -> x=40, y=40)
        # Convert pixel coordinates to tile coordinates
        tilex = x * MAP_TILE_SIZE
        tiley = y * MAP_TILE_SIZE
        self.position = rl.Vector2(tilex, tiley)
        self.tileX = x
        self.tileY = y

    def move(self, dx, dy, map: Map):
        self.position.x += dx
        self.position.y += dy

        # Ensure player stays within the map boundaries
        self.position.x = max(0, min(self.position.x, map.tilesX * MAP_TILE_SIZE - PLAYER_SIZE))
        self.position.y = max(0, min(self.position.y, map.tilesY * MAP_TILE_SIZE - PLAYER_SIZE))

        # Update player tile position
        self.tileX = int((self.position.x + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)
        self.tileY = int((self.position.y + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)
    
    def draw(self):
        rl.draw_rectangle_v(self.position, rl.Vector2(PLAYER_SIZE, PLAYER_SIZE), rl.RED)

class Hider:
    def __init__(self, x, y):
        self.position = rl.Vector2(x, y)
        self.tileX = 0
        self.tileY = 0
    
    def draw(self):
        rl.draw_rectangle_v(self.position, rl.Vector2(PLAYER_SIZE, PLAYER_SIZE), rl.GREEN)

def main():
    screenWidth = SCREEN_WIDTH
    screenHeight = SCREEN_HEIGHT

    rl.init_window(screenWidth, screenHeight, "Hide and Seek")

    rl.set_target_fps(30)
    map = Map()
    map.tilesX = MAP_TILE_X
    map.tilesY = MAP_TILE_Y

    # Opt for a list of 0s instead of calloc
    map.tileIds = [0] * (map.tilesX * map.tilesY)
    map.tileFog = [0] * (map.tilesX * map.tilesY)

    # NOTE: Map tile ids should be probably loaded from an external map file (by defination: 0: empty, 1: obstacle (yellow), 2: wall (static, black))
    # Load map tiles (generating 2 random tile ids for testing)
    # for i in range(map.tilesY * map.tilesX):
    #     map.tileIds[i] = random.randint(0, 2)
    for i in range(0, prob.num_row):
        for j in range(0, prob.num_col):
            if prob.map_list[i][j][0] == 1000:
                map.tileIds[i * prob.num_col + j] = 0
            elif prob.map_list[i][j][0] == -1:
                map.tileIds[i * prob.num_col + j] = 2
            elif type(prob.map_list[i][j][0]) == player.Seeker:
                seeker = Seeker(i, j)



    # Seeker position in the map (default tile: 0,0)
    seeker = Seeker(2, 1)
    hider1 = Hider(random.randint(0, 800), random.randint(0, 800))
    hider2 = Hider(random.randint(0, 800), random.randint(0, 800))

    # Create a render texture to store the fog of war
    fogOfWar = rl.load_render_texture(map.tilesX, map.tilesY)
    rl.set_texture_filter(fogOfWar.texture, rl.TEXTURE_FILTER_BILINEAR)

    rl.set_target_fps(30)

    while not rl.window_should_close():    
        #--------USER CONTROL MOVEMENT (ONLY FOR DEBUGGING) --------
        user_control = True
        if user_control:
            if rl.is_key_pressed(rl.KEY_RIGHT) and rl.is_key_pressed(rl.KEY_DOWN):
                if map.tileIds[(seeker.tileY + 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(PLAYER_SIZE, PLAYER_SIZE, map)
            elif rl.is_key_pressed(rl.KEY_RIGHT) and rl.is_key_pressed(rl.KEY_UP):
                if map.tileIds[(seeker.tileY - 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(PLAYER_SIZE, -PLAYER_SIZE, map)
            elif rl.is_key_pressed(rl.KEY_LEFT) and rl.is_key_pressed(rl.KEY_DOWN):
                if map.tileIds[(seeker.tileY + 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(-PLAYER_SIZE, PLAYER_SIZE, map)
            elif rl.is_key_pressed(rl.KEY_LEFT) and rl.is_key_pressed(rl.KEY_UP):
                if map.tileIds[(seeker.tileY - 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(-PLAYER_SIZE, -PLAYER_SIZE, map)
            elif rl.is_key_pressed(rl.KEY_RIGHT):
                if map.tileIds[seeker.tileY * map.tilesX + seeker.tileX + 1] != 2:
                    seeker.move(PLAYER_SIZE, 0, map)
            elif rl.is_key_pressed(rl.KEY_LEFT):
                if map.tileIds[seeker.tileY * map.tilesX + seeker.tileX - 1] != 2:
                    seeker.move(-PLAYER_SIZE, 0, map)
            elif rl.is_key_pressed(rl.KEY_DOWN):
                if map.tileIds[(seeker.tileY + 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(0, PLAYER_SIZE, map)
            elif rl.is_key_pressed(rl.KEY_UP):
                if map.tileIds[(seeker.tileY - 1) * map.tilesX + seeker.tileX] != 2:
                    seeker.move(0, -PLAYER_SIZE, map)
            
        #--------FILE INPUT MOVEMENT--------
        # file_input_movement = False

        # Previous visited tiles are set to partial fog
        for i in range(map.tilesY * map.tilesX):
            if map.tileFog[i] == 1:
                map.tileFog[i] = 2

        # Check visibility and update fog
        # NOTE: It is important to check tilemap limits to avoid processing tiles out-of-array-bounds (it could crash program)
        for y in range(seeker.tileY - PLAYER_TILE_VISIBILITY, seeker.tileY + PLAYER_TILE_VISIBILITY):
            for x in range(seeker.tileX - PLAYER_TILE_VISIBILITY, seeker.tileX + PLAYER_TILE_VISIBILITY):
                if 0 <= x < map.tilesX and 0 <= y < map.tilesY:
                    map.tileFog[y * map.tilesX + x] = 1


        #-----------------------------RENDERING-----------------------------
        # TEXTURE
        rl.begin_texture_mode(fogOfWar)
        rl.clear_background(rl.BLANK)
        for y in range(map.tilesY):
            for x in range(map.tilesX):
                if map.tileFog[y * map.tilesX + x] == 0:
                    rl.draw_rectangle(x, y, 1, 1, rl.fade(rl.BLACK, 0.8))
                elif map.tileFog[y * map.tilesX + x] == 2:
                    rl.draw_rectangle(x, y, 1, 1, rl.fade(rl.BLACK, 0.6))
        rl.end_texture_mode()
        
        # DRAWING ELEMENTS
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)             
                
        map.draw() 
        seeker.draw()
                
        # Draw fog (scaled to full map, bilinear filtering)
        rl.draw_texture_pro(fogOfWar.texture, rl.Rectangle(0, 0, fogOfWar.texture.width, -fogOfWar.texture.height),
                            rl.Rectangle(0, 0, map.tilesX * MAP_TILE_SIZE, map.tilesY * MAP_TILE_SIZE),
                            rl.Vector2(0, 0), 0.0, rl.WHITE)
        
        # Write current player position tile
        rl.draw_text(f"Current tile: [{seeker.tileX},{seeker.tileY}]", 10, 10, 20, rl.RAYWHITE)
        
        hider1.draw()
        hider2.draw()        
        
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
