import pyray as rl
import random
from obstacle import *
from player import *

#-------------------ELEMENTS-------------------
MAP_TILE_SIZE = 20
PLAYER_SIZE = 20
PLAYER_TILE_VISIBILITY = 3 # Tiles around player that will be visible

#----------------MAP STRUCTURES----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
MAP_TILE_X = 40
MAP_TILE_Y = 40

# map: the map read from the input file
#    -1: wall
#    2: hider
#    3: seeker
#    1000: an empty cell
#    obstacles: a list of Obstacle objects in the above map


class Map:
    def __init__(self):
        self.tilesX = 0
        self.tilesY = 0
        self.tileIds = None
        self.tileFog = None

def main():
    screenWidth = SCREEN_WIDTH
    screenHeight = SCREEN_HEIGHT

    rl.init_window(screenWidth, screenHeight, "raylib [textures] example - fog of war")

    map = Map()
    map.tilesX = MAP_TILE_X
    map.tilesY = MAP_TILE_Y

    #NOTE: We can have up to 256 values for tile ids and for tile fog state,
    #probably we don't need that many values for fog state, it can be optimized
    #to use only 2 bits per fog state (reducing size by 4) but logic will be a bit more complex
    #map.tileIds = (unsigned char *)calloc(map.tilesX*map.tilesY, sizeof(unsigned char));
    #map.tileFog = (unsigned char *)calloc(map.tilesX*map.tilesY, sizeof(unsigned char));

    # Opt for a list of 0s instead of calloc
    map.tileIds = [0] * (map.tilesX * map.tilesY)
    map.tileFog = [0] * (map.tilesX * map.tilesY)

    for i in range(map.tilesY * map.tilesX):
        map.tileIds[i] = random.randint(0, 1)

# Player position in the map (default tile: 0,0)
    playerPosition = rl.Vector2(0,0)
    playerTileX = 0
    playerTileY = 0

# Create a render texture to store the fog of war
    fogOfWar = rl.load_render_texture(map.tilesX, map.tilesY)
    rl.set_texture_filter(fogOfWar.texture, rl.TEXTURE_FILTER_BILINEAR) # Texture scale filter to use

    rl.set_target_fps(60) # Change this to 30 if you want to see the effect more clearly

    while not rl.window_should_close():
        if rl.is_key_pressed(rl.KEY_RIGHT):
            playerPosition.x += MAP_TILE_SIZE # Move player position by one tile (32 units)
        if rl.is_key_pressed(rl.KEY_LEFT):
            playerPosition.x -= MAP_TILE_SIZE
        if rl.is_key_pressed(rl.KEY_DOWN):
            playerPosition.y += MAP_TILE_SIZE
        if rl.is_key_pressed(rl.KEY_UP):
            playerPosition.y -= MAP_TILE_SIZE

        if playerPosition.x < 0:
            playerPosition.x = 0
        elif (playerPosition.x + PLAYER_SIZE) > (map.tilesX * MAP_TILE_SIZE):
            playerPosition.x = map.tilesX * MAP_TILE_SIZE - PLAYER_SIZE
        if playerPosition.y < 0:
            playerPosition.y = 0
        elif (playerPosition.y + PLAYER_SIZE) > (map.tilesY * MAP_TILE_SIZE):
            playerPosition.y = map.tilesY * MAP_TILE_SIZE - PLAYER_SIZE

        for i in range(map.tilesY * map.tilesX):
            if map.tileFog[i] == 1:
                map.tileFog[i] = 2

        playerTileX = int((playerPosition.x + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)
        playerTileY = int((playerPosition.y + MAP_TILE_SIZE / 2) / MAP_TILE_SIZE)

        for y in range(playerTileY - PLAYER_TILE_VISIBILITY, playerTileY + PLAYER_TILE_VISIBILITY):
            for x in range(playerTileX - PLAYER_TILE_VISIBILITY, playerTileX + PLAYER_TILE_VISIBILITY):
                if 0 <= x < map.tilesX and 0 <= y < map.tilesY:
                    map.tileFog[y * map.tilesX + x] = 1

        rl.begin_texture_mode(fogOfWar)
        rl.clear_background(rl.BLANK)
        for y in range(map.tilesY):
            for x in range(map.tilesX):
                if map.tileFog[y * map.tilesX + x] == 0:
                    rl.draw_rectangle(x, y, 1, 1, rl.BLACK)
                elif map.tileFog[y * map.tilesX + x] == 2:
                    rl.draw_rectangle(x, y, 1, 1, rl.fade(rl.BLACK, 0.8))
        rl.end_texture_mode()

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        for y in range(map.tilesY):
            for x in range(map.tilesX):
                rl.draw_rectangle(x * MAP_TILE_SIZE, y * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                  rl.BLUE if map.tileIds[y * map.tilesX + x] == 0 else rl.fade(rl.BLUE, 0.9))
                rl.draw_rectangle_lines(x * MAP_TILE_SIZE, y * MAP_TILE_SIZE, MAP_TILE_SIZE, MAP_TILE_SIZE,
                                         rl.fade(rl.DARKBLUE, 0.5))
        rl.draw_rectangle_v(playerPosition, rl.Vector2(PLAYER_SIZE, PLAYER_SIZE), rl.RED)
        rl.draw_texture_pro(fogOfWar.texture, rl.Rectangle(0, 0, fogOfWar.texture.width, -fogOfWar.texture.height),
                            rl.Rectangle(0, 0, map.tilesX * MAP_TILE_SIZE, map.tilesY * MAP_TILE_SIZE),
                            rl.Vector2(0, 0), 0.0, rl.WHITE)
        rl.draw_text(f"Current tile: [{playerTileX},{playerTileY}]", 10, 10, 20, rl.RAYWHITE)
        rl.draw_text("ARROW KEYS to move", 10, screenHeight - 25, 20, rl.RAYWHITE)
        rl.end_drawing()

    rl.unload_render_texture(fogOfWar)
    rl.close_window()

if __name__ == "__main__":
    main()
