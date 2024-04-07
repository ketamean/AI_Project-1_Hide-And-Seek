from problem import *
from obstacle import *
from player import *
from pq import *
from astar import *
from queue import PriorityQueue
from state_for_fe import StateForFE
class Level1:
    announcement = []
    def __init__(self, input_filepath:str) -> None:
        Level1._vision_convention = None
        self.problem = Problem(
            input_filename=input_filepath,
            allow_move_obstacles=False
        )
        seeker = self.problem.seeker
        seeker.origin_map = self.problem.map_list

        skeleton_map = []
        for row in self.problem.map_list:
            row_skelation = []
            for cell in row:
                if cell == -1:
                    row_skelation.append(-1)
                else:
                    row_skelation.append(1000)
            skeleton_map.append( row_skelation )

        from copy import deepcopy
        seeker.vision_map = deepcopy(skeleton_map)
        seeker.heuristic_map = deepcopy(skeleton_map)
        seeker.skeleton_map = deepcopy(skeleton_map)

    ADJACENT = [
        (-1,-1),    (-1,0),     (-1,1),
        (0,-1),                 (0,1),
        (1,-1),     (1,0),      (1,1)
    ]

    def __move_towards_target(self, target_coor: tuple):
            """
            Move the seeker towards the target cell until it reaches the target.

            Returns a list of steps (as coordinates) taken by the seeker.
            """
            seeker = self.problem.seeker
            seeker_coordinate = seeker.coordinate

            # Define a helper function to compute the Manhattan distance heuristic
            def manhattan_distance(coord1, coord2):
                return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

            # Initialize dictionaries to keep track of g-score and f-score for each node
            g_score = {seeker_coordinate: 0}
            f_score = {seeker_coordinate: manhattan_distance(seeker_coordinate, target_coor)}

            # Initialize a priority queue to store nodes to be evaluated
            open_list = PriorityQueue()
            open_list.put((f_score[seeker_coordinate], seeker_coordinate))

            # Initialize a dictionary to store parent nodes for path reconstruction
            came_from = {}

            while not open_list.empty():
                _, current = open_list.get()

                if current == target_coor:
                    # Reconstruct the path and return it
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.reverse()
                    return path

                for dr, dc in Level1.ADJACENT:
                    neighbor = (current[0] + dr, current[1] + dc)

                    # Check if the neighbor is valid
                    if (neighbor[0] < 0 or neighbor[0] >= len(self.problem.map_list) or
                        neighbor[1] < 0 or neighbor[1] >= len(self.problem.map_list[0]) or
                        -1 in self.problem.map_list[neighbor[0]][neighbor[1]]):
                        continue

                    # Compute the tentative g-score for the neighbor
                    tentative_g_score = g_score[current] + 1

                    # Update if this is a better path
                    if (neighbor not in g_score) or (tentative_g_score < g_score[neighbor]):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, target_coor)
                        open_list.put((f_score[neighbor], neighbor))

            # If the open list is empty and the goal is not reached, return an empty path
            return []
    
    def __choose_step_no_info(self):
        """
            let seeker take a step when there is no percept of Hider and Announcement

            returns False if end game (no cell to go); otherwise, a list of steps (as coordinates)
        """
        from copy import deepcopy
        seeker = self.problem.seeker
        cur_r,cur_c = seeker.coordinate     # current coordinate of the agent
        DIRECTIONS = [
            (cur_r-1, cur_c-1), (cur_r-1, cur_c),   (cur_r-1, cur_c+1),
            (cur_r, cur_c-1),                       (cur_r, cur_c+1),
            (cur_r+1, cur_c-1), (cur_r+1, cur_c),   (cur_r+1, cur_c+1)
        ]
        if len(self.moves_stack) == 0:
            # the first step => has no previous step
            pass
        else:
            # avoid steping back to the previous step
            last_r, last_c = self.moves_stack[-1]   # the previous coordinate of the agent
            max_coordinate = []     # list of coordinate of cells with the largest cnt value
            max_count_val = -1

            # traverse all potential coordinate of the next step
            for (idr, idc) in DIRECTIONS:
                
                if idr < 0 or idr >= len(seeker.vision_map) or idc < 0 or idc >= len(seeker.vision_map[0]):
                    # index out of range
                    continue
                if idr == last_r and idc == last_c:
                    # avoid steping back to the previous cell
                    continue
                if -1 in seeker.origin_map[idr][idc]:
                    # skip wall (cannot get through)
                    continue

                v_map = self.vision_maps.get( (idr, idc) )
                if v_map == None:
                    # check for the existence of the vision map of this cell
                    tmp_seeker = Seeker(
                        coordinate=(idr, idc)
                    )
                    tmp_seeker.origin_map = seeker.origin_map
                    tmp_seeker.skeleton_map = seeker.skeleton_map
                    tmp_seeker.vision()
                    v_map = deepcopy(tmp_seeker.vision_map)
                    self.vision_maps[ (idr, idc) ] = v_map
                cnt = 0

                # print debug
                #=============================================
                # print('vmap:', idr, idc)
                # for idrow in v_map:
                #     for cell in idrow:
                #         print(cell, end=' ')
                #         # if cell == True:
                #         #     print(1, end=' ')
                #         # else:
                #         #     print(0, end=' ')
                #     print()
                # print('seenmap:', idr, idc)
                # for idrow in self.seen_map:
                #     for cell in idrow:
                #         if cell == True:
                #             print(1, end=' ')
                #         else:
                #             print(0, end=' ')
                #     print()
                #=============================================

                # traverse vision map of the potentially next step
                for idrow in range(idr-seeker.radius, idr+seeker.radius + 1, +1):
                    # check index validity
                    if idrow < 0:
                        continue
                    if idrow >= len(self.cur_vision_maps):
                        break
                    for idcol in range(idc-seeker.radius, idc+seeker.radius + 1, +1):
                        # print('row:', idrow, 'col:', idcol)
                        if idcol == idc and idrow == idr:
                            continue
                        # check index validity
                        if idcol < 0:
                            continue
                        if idcol >= len(self.cur_vision_maps[0]):
                            break
                        if v_map[idrow][idcol] == True and self.seen_map[idrow][idcol] == False:
                            cnt += 1
                    # print('heuristic:', cnt)
                if cnt > max_count_val:
                    max_count_val = cnt
                    max_coordinate = [ (idr, idc) ]
                elif cnt == max_count_val:
                    max_coordinate.append( (idr, idc) )

            # print('max:', max_count_val)
            # print('n cell:', len(max_coordinate))
            # for i in max_coordinate:
            #     print(i)
            if len(max_coordinate) == 0:
                # is blocked, cannot move to any adjacent cells
                return False
            elif len(max_coordinate) > 1:
                # many cells share a common heuristic value
                if max_count_val == 0:
                    # h = 0: no new vision
                    radius = seeker.radius + 1
                    stop_flag = True  # to check whether we expanded the whole map
                    while stop_flag:
                        stop_flag = False
                        cells = []

                        for row in range(cur_r - radius, cur_r + radius + 1):
                            if row < 0:
                                continue
                            if row >= len(seeker.origin_map):
                                break
                            for col in range(cur_c - radius, cur_c + radius + 1):
                                if col < 0:
                                    continue
                                if col >= len(seeker.origin_map[0]):
                                    break
                                if -1 in seeker.origin_map[row][col]:
                                    # skip wall
                                    continue
                                if self.seen_map[row][col] == False:
                                    cells.append({
                                        'coordinate': (row, col),
                                        'distance': abs(row - cur_r) + abs(col - cur_c)  # Manhattan distance
                                    })
                        if len(cells):
                            # Sort cells by Manhattan distance
                            cells.sort(key=lambda x: x['distance'])
                            for x in cells:
                                print('cells:', x['coordinate'])
                            for cell_data in cells:
                                res = self.__move_towards_target(cell_data['coordinate'])
                                if res:
                                    for i, j in res:
                                        print('res:', res)
                                        if (i, j != self.moves_stack[-1]):
                                            return [(i, j)]
                        radius += 1
                        stop_flag = True
                        # if (radius + cur_c < len(seeker.origin_map[0]) or radius + cur_c > 0) and (radius + cur_r < len(seeker.origin_map) or radius + cur_r > 0):
                        #     radius += 1
                        # else:
                        #     # No path found to any reachable unseen cell
                        #     return False

                else:
                    # h != 0: choose the cell whose Manhattan distance from the previous cell is the largest
                    max_distance = -1
                    max_distance_coor = None
                    for i, j in max_coordinate:
                        tmp_dis = abs(last_r - i) + abs(last_c - j)
                        if tmp_dis > max_distance:
                            max_distance_coor = (i, j)
                    return [max_distance_coor]
            else:
                print('max coordinate:', (max_coordinate[0]))
                return [(max_coordinate[0])]
    
    def __hider_take_turn(self, hider: Hider):
        """
        A hider in the list of hiders takes its turn:
            - Increase count to announcement
            - If needed, raise an announcement and put it onto the map

        id: Index of hider in the list of hider in the problem, and it is also ID of the hider
        Returns nothing
        """
        hider.count_to_announcement += 1
        if hider.count_to_announcement == hider.step_to_announcement:
            # Reset count to announcement
            hider.count_to_announcement = 0

            # Raise an announcement for the hider
            announce = hider.announce()
            print('ANNOUNCE', announce.coordinate)
            self.announcements_on_map.append( announce )
            row, col = announce.coordinate

            # Place the new announcement on the map
            if 1000 in self.problem.map_list[row][col]:
                self.problem.map_list[row][col] = [announce]
            else:
                self.problem.map_list[row][col].append(announce)

    def run(self):
        from copy import deepcopy, copy
        seeker = self.problem.seeker
        hider_coor = []
        announcement_coor = []
        self.moves_stack = [ copy(seeker.coordinate) ]                   # stack of steps of seeker

        self.vision_maps = {                    # map a coordinate with the corresponding vision map for later reuse
            
        }

        self.seen_map = [                       # list of cells which seeker has already seen
            [True if cell == -1 else False for cell in row ] for row in seeker.skeleton_map
        ]                                       # True / False

        seeker_turn = True
        self.announcements_on_map = []
        self.current_announcement = None
        self.last_step = seeker.coordinate

        # HANDLE NO HIDER CASE

        if len(self.problem.hiders) != 1:
            raise ValueError('Hider not exist or out of range.')

        while True:
            if not seeker_turn:
                # # hider raise announcement
                hider = self.problem.hiders[0]
                self.__hider_take_turn(hider)

                yield StateForFE(
                    player=hider,
                    old_row=hider.coordinate[0],
                    old_col=hider.coordinate[1],
                    new_row=hider.coordinate[0],
                    new_col=hider.coordinate[1],
                    announcements=self.announcements_on_map
                )
                seeker_turn = not seeker_turn
                pass

            # SEEKER MOVE
            else:
                seeker_turn = not seeker_turn
                r,c = seeker.coordinate

                self.moves_stack = [ copy(seeker.coordinate) ]  
                self.cur_vision_maps = self.vision_maps.get( (r,c) )
                print('cur:', r, c)
                print('previous step:', self.moves_stack[-1])
                if self.cur_vision_maps == None:
                    seeker.vision()
                    self.cur_vision_maps = deepcopy(seeker.vision_map)
                    self.vision_maps[ (r,c) ] = self.cur_vision_maps

                # Check for existence of Hider or Announcement in the vision
                hider_found = False
                announcement_found = False

                for idrow in range(-seeker.radius, seeker.radius + 1, +1):
                    # check index validity
                    if r + idrow < 0:
                        continue
                    if r + idrow >= len(self.cur_vision_maps):
                        break
                    for idcol in range(-seeker.radius, seeker.radius + 1, +1):
                        if idcol == 0 and idrow == 0:
                            continue
                        # check index validity
                        if c + idcol < 0:
                            continue
                        if c + idcol >= len(self.cur_vision_maps[0]):
                            break
                        if self.cur_vision_maps[idrow][idcol] != 0 and self.cur_vision_maps[idrow][idcol] != -1:
                            for element in self.problem.map_list[r + idrow][c + idcol]:
                                if not isinstance(element, int):
                                    # not -1 or 0 => is object
                                    if element.signature == 'Hider':
                                        hider_coor.append((r + idrow, c + idcol))
                                        hider_found = True
                                    elif element.signature == 'Announcement':
                                        announcement_coor.append((r + idrow, c + idcol))
                                        announcement_found = True

                        if hider_found or announcement_found:
                            break  # Exit the loop if either a Hider or Announcement is found

                    if hider_found or announcement_found:
                        break  # Exit the loop if either a Hider or Announcement is found

                # CHECK IN CASE SEEKER CANNOT FIND OUT HIDER -> GIVE UP
                flag_reach_all = True
                for row in self.seen_map:
                    for cell in row:
                        if cell == False:
                            flag_reach_all = not flag_reach_all
                    if not flag_reach_all: break
                if flag_reach_all:
                    # traverse through the whole map, return
                    return
                
                if len(hider_coor) or len(announcement_coor):
                    if len(hider_coor):
                        # there is a hider, go to this
                        if len(hider_coor) > 1 and seeker.coordinate == hider_coor:
                            # SUCESSFULLY FOUND HIDER
                            print('FOUND HIDER:', (hider_coor), "SEEKER:", (seeker.coordinate))
                            return
                        else:
                            # only 1 hider
                            hider_coor = hider_coor[0]
                            print('hider', hider_coor)
                            res = self.__move_towards_target(hider_coor)
                            if res:
                                for i, j in res:
                                    self.problem.map_list[r][c].remove(seeker)
                                    r, c = i, j                 # Update seeker's position to current cell
                                    seeker.coordinate = (i, j)  # Update seeker's position to move towards the Hider
                                    visionmap = self.vision_maps.get((i, j))
                                    if visionmap == None:
                                        tmp_seeker = Seeker(
                                            coordinate=(i, j)
                                        )
                                        tmp_seeker.origin_map = seeker.origin_map
                                        tmp_seeker.skeleton_map = seeker.skeleton_map
                                        tmp_seeker.vision()
                                        visionmap = deepcopy(tmp_seeker.vision_map)
                                        self.vision_maps[(i, j)] = visionmap
                                    # after choosing a cell, assign new vision to the seen map
                                    for idr in range(i - seeker.radius, i + seeker.radius + 1, +1):
                                        if idr < 0:
                                            continue
                                        if idr >= len(seeker.vision_map):
                                            break
                                        for idc in range(j - seeker.radius, j + seeker.radius + 1, +1):
                                            if idc < 0:
                                                continue
                                            if idc >= len(seeker.vision_map[0]):
                                                break
                                            if visionmap[idr][idc] == True:
                                                self.seen_map[idr][idc] = True
                                    if 1000 in self.problem.map_list[i][j]:
                                        self.problem.map_list[i][j] = [seeker]
                                    else:
                                        self.problem.map_list[i][j].append(seeker)
                                    self.moves_stack.append((i, j))

                                    print('MOVE TOWARDS HIDER')
                                    for row in self.problem.map_list:
                                        for cell in row:
                                            if -1 in cell:
                                                print('x', end=' ')
                                            # if there is a seeker in that cell
                                            elif seeker in cell:
                                                print('S', end=' ')
                                            # if there is a hider in that cell
                                            elif len(cell) == 1 and isinstance(cell[0], Hider):
                                                print('H', end=' ')
                                            else:
                                                print('-', end=' ')
                                        print()
                    if len(announcement_coor):
                        # there is an announcement, find path to announcement

                        # There is only an announcement in sight, move towards it
                        if len(announcement_coor) == 1:
                            announcement_coor = announcement_coor[0]
                        else:
                            # Multiple announcements, prioritize the latest one
                            announcement_coor = announcement_coor[-1]
                        res = self.__move_towards_target(announcement_coor)
                        if res:
                            for i, j in res:
                                print('seeker move to announcement', (i, j))
                                # Update seeker's position
                                self.problem.map_list[r][c].remove(seeker)
                                r, c = i, j
                                seeker.coordinate = (i, j)
                                # Update vision map
                                visionmap = self.vision_maps.get((i, j))
                                if visionmap is None:
                                    tmp_seeker = Seeker(coordinate=(i, j))
                                    tmp_seeker.origin_map = seeker.origin_map
                                    tmp_seeker.skeleton_map = seeker.skeleton_map
                                    tmp_seeker.vision()
                                    visionmap = deepcopy(tmp_seeker.vision_map)
                                    self.vision_maps[(i, j)] = visionmap
                                # Update seen map
                                for idr in range(i - seeker.radius, i + seeker.radius + 1, +1):
                                    if idr < 0:
                                        continue
                                    if idr >= len(seeker.vision_map):
                                        break
                                    for idc in range(j - seeker.radius, j + seeker.radius + 1, +1):
                                        if idc < 0:
                                            continue
                                        if idc >= len(seeker.vision_map[0]):
                                            break
                                        if visionmap[idr][idc] == True:
                                            self.seen_map[idr][idc] = True
                                # Update map with seeker's new position
                                if 1000 in self.problem.map_list[i][j]:
                                    self.problem.map_list[i][j] = [seeker]
                                else:
                                    self.problem.map_list[i][j].append(seeker)
                                self.moves_stack.append((i, j))

                                print('MOVE TOWARDS ANNOUNCEMENT')
                                for row in self.problem.map_list:
                                    for cell in row:
                                        if -1 in cell:
                                            print('x', end=' ')  # Wall
                                        elif seeker in cell:
                                            print('S', end=' ')  # Seeker
                                        elif any(isinstance(obj, Hider) for obj in cell):
                                            print('H', end=' ')  # Hider
                                        elif any(isinstance(obj, Announcement) for obj in cell):
                                            print('A', end=' ')  # Announcement
                                        else:
                                            print('-', end=' ')  # Empty cell
                                    print()

                
                else:
                    # no hider, no announcement
                    res = self.__choose_step_no_info()
                    # for i in res:
                    #     print(i)
                    if res == False:
                        # give up
                        print("No cell to go")
                        return [], False
                    for R, C in res:
                        self.problem.map_list[r][c].remove( seeker )
                        seeker.coordinate = (R,C)
                        visionmap = self.vision_maps.get( (R,C) )
                        if visionmap == None:
                            tmp_seeker = Seeker(
                                coordinate=(R, C)
                            )
                            tmp_seeker.origin_map = seeker.origin_map
                            tmp_seeker.skeleton_map = seeker.skeleton_map
                            tmp_seeker.vision()
                            visionmap = deepcopy(tmp_seeker.vision_map)
                            self.vision_maps[ (idr, idc) ] = visionmap


                        # -----------------------------------------------------------------
                        # print debug
                        # for row in visionmap:
                        #     for cell in row:
                        #         if cell == -1:
                        #             print('x', end=' ')
                        #         elif cell == 1000:
                        #             print('-', end=' ')
                        #         elif cell:
                        #             print(1, end=' ')
                        #         else:
                        #             print(0, end=' ')
                        #     print()
                        # # -----------------------------------------------------------------

                        # after choosing a cell, assign new vision to the seen map
                        for idr in range(R - seeker.radius, R + seeker.radius + 1, +1):
                            if idr < 0:
                                continue
                            if idr >= len(seeker.vision_map):
                                break
                            for idc in range(C - seeker.radius, C + seeker.radius + 1, +1):
                                if idc < 0:
                                    continue
                                if idc >= len(seeker.vision_map[0]):
                                    break
                                if visionmap[idr][idc] == True:
                                    self.seen_map[idr][idc] = True
                        if 1000 in self.problem.map_list[R][C]:
                            self.problem.map_list[R][C] = [ seeker ]
                            print('append seeker', (R, C))
                        else:
                            self.problem.map_list[R][C].append( seeker )

                        # decrease seeker score for each move
                        seeker.score -= 1

                        yield StateForFE(
                            player=seeker,
                            old_row=self.moves_stack[-1][0],
                            old_col=self.moves_stack[-1][1],
                            new_row=R,
                            new_col=C,
                            announcements=self.announcements_on_map
                        )
                        self.moves_stack.append( (R,C) )  

                for row in self.problem.map_list:
                    for cell in row:
                        if -1 in cell:
                            print('x', end=' ')
                        # if there is a seeker in that cell
                        elif seeker in cell:
                            print('S', end=' ')
                        # if there is a hider in that cell
                        elif len(cell) == 1 and isinstance(cell[0], Hider):
                            print('H', end=' ')
                        else:
                            print('-', end=' ')
                    print()

            #=============================================
            #============================================
            # TEST
            # visionmap = self.vision_maps.get( (0,9) )
            # if visionmap == None:
            #     tmp_seeker = Seeker(
            #         coordinate=(0, 9)
            #     )
            #     tmp_seeker.origin_map = seeker.origin_map
            #     tmp_seeker.skeleton_map = seeker.skeleton_map
            #     tmp_seeker.vision()
            #     visionmap = deepcopy(tmp_seeker.vision_map)
            #     self.vision_maps[ (idr, idc) ] = visionmap

            # -----------------------------------------------------------------
            # print debug
            # print('vision map')
            # for row in self.problem.map_list:
            #     for cell in row:
            #         if -1 in cell:
            #             print('x', end=' ')
            #         # if there is a seeker in that cell
            #         elif seeker in cell:
            #             print('S', end=' ')
            #         # if there is a hider in that cell
            #         elif len(cell) == 1 and isinstance(cell[0], Hider):
            #             print('H', end=' ')
            #         else:
            #             print('-', end=' ')
            #     print()  
            # print('=====================')
            for row in self.seen_map:
                for cell in row:
                    if cell == -1:
                        print('x', end=' ')
                    elif cell == 1000:
                        print('-', end=' ')
                    elif cell:
                        print(1, end=' ')
                    else:
                        print(0, end=' ')
                print()
            # -----------------------------------------------------------------       

class Level2:
    """
        steps_stack: top stack is at the end of the array
    """
    _all_announcements = []     # to keep all announcements
    def __init__(self, input_filepath: str) -> None:
        """
            there are 3 kinds of map:
            - original map: problem.map_list
            - map of vision: viewable cells
            - map of heuristic: heuristics value only (-1, 0-999, 1000)
        """
        # a frame to build vision of a player
        # cells in the vision are numbered from 0 to (2r+1)^2 - 1
        # the following list contains multiple sublists, each of which is at index i and is a sequence of cell numbers that become unviewable when the cell i is a wall
        Level2.__vision_convention = None
        self.problem = Problem(
            input_filename=input_filepath,
            allow_move_obstacles=False
        )

    ADJACENT = [
        (-1,-1),    (-1,0),     (-1,1),
        (0,-1),                 (0,1),
        (1,-1),     (1,0),      (1,1)
    ]
    @staticmethod
    def is_adjacent(tile1: tuple, tile2: tuple):
        """
            check whether tile 1 adjacent to tile 2

            tiles are given as their coordinate
        """
        for dr,dc in Level2.ADJACENT:
            if tile1[0] + dr == tile2[0] and tile1[1] + dc == tile2[1]:
                return True
        return False
    
    def move_seeker_to(self, coordinate: tuple):
        """
            assign current coordinate to self.last_step
            remove seeker from old tile
            add it to the new tile
            assign new coordinate to the seeker

            no return
        """
        seeker = self.problem.seeker
        r,c = seeker.coordinate
        self.last_step = (r,c)

        next_r, next_c = coordinate
        if -1 in self.problem.map_list[next_r][next_c]:
            # wall
            raise ValueError('Cannot go through a wall')
        elif 1000 in self.problem.map_list[next_r][next_c]:
            # empty cell
            self.problem.map_list[next_r][next_c] = [ seeker ]
        else:
            self.problem.map_list[next_r][next_c].append( seeker )
        
        # remove seeker from the previous cell
        self.problem.map_list[r][c].remove(seeker)

        # assign new coordinate to seeker
        seeker.coordinate = coordinate
        
    def __seeker_check_found_hider(self):
        """
            check if the seeker is currently in the same tile with a particular hider
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        for element in self.problem.map_list[cur_r][cur_c]:
            if not isinstance(element, int) and element.signature == 'Hider':
                # a hider is found
                self.total_hiders -= 1
                seeker.score += 20
                print('found', (cur_r, cur_c))
                self.visibile_hider_coor.remove( (cur_r, cur_c) )
                self.problem.hiders.remove(element)
                self.problem.map_list[cur_r][cur_c].remove(element)
                # remove all of its announcements in the list of visible announcements
                for ann in self.visible_announcements:
                    if ann['hider_id'] == element.id:
                        self.visible_announcements.remove( ann )
                if self.current_announcement and self.current_announcement['hider_id'] == element.id:
                    self.current_announcement = None
                    self.seeker_path_for_announcement = []
                
                break

    def __seeker_check_new_hider_and_announcement(self):
        """
            check the vision map from current tile to find new hiders and announcements in the field of view 
        """
        from copy import deepcopy
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        # get vision map from the current tile
        visionmap = self.vision_maps.get( (cur_r, cur_c) )
        if visionmap == None:
            seeker.vision()
            visionmap = deepcopy(seeker.vision_map)
            self.vision_maps[ (cur_r, cur_c) ] = visionmap
        
        # check the vision map to find new visible hiders and announcements
        for idrow in range(cur_r-seeker.radius, cur_r+seeker.radius + 1, +1):
            # check index validity
            if idrow < 0:
                continue
            if idrow >= len(visionmap):
                break
            for idcol in range(cur_c-seeker.radius, cur_c+seeker.radius + 1, +1):
                if idcol == cur_c and idrow == cur_r:
                    # skip current cell
                    continue    
                # check index validity
                if idcol < 0:
                    continue
                if idcol >= len(visionmap[0]):
                    break
                if visionmap[idrow][idcol] == True: # cell is visible
                    # mark cell as seen
                    self.seen_map[idrow][idcol] = True

                    # as it is visible, it is also reachable
                    self.reachable[idrow][idcol] = True

                    for component in self.problem.map_list[idrow][idcol]:
                        if not isinstance(component, int):
                            # not -1 or 1000 => it is an object
                            if component.signature == 'Hider':
                                # is a hider
                                if not (component.coordinate[0], component.coordinate[1]) in self.visibile_hider_coor:
                                    self.visibile_hider_coor.append( (component.coordinate[0], component.coordinate[1]) )
                            elif component.signature == 'Announcement':
                                if not (component.coordinate[0], component.coordinate[1]) in self.visible_announcements:
                                    self.visible_announcements.append(
                                        {
                                            'coordinate': (component.coordinate[0], component.coordinate[1]),
                                            'hider_id': component.hider.id
                                        }
                                    )
    
    def __seeker_choose_cell_on_path_to_hider(self):
        """
            assuming that seeker is on the way to a hider

            return coordinate of the cell to go next and POP IT OUT OF THE PATH TO HIDER
        """
        cur_r, cur_c = self.problem.seeker.coordinate
        R,C = self.seeker_path_to_hider[0]
        if not Level2.is_adjacent(tile1=(cur_r, cur_c), tile2=(R,C)):
            path = astar.astar(
                grid=self.astar_map,
                start_coor=(cur_r, cur_c),
                goal_coor=(R,C)
            )
            path.pop()
            self.seeker_path_to_hider = path + self.seeker_path_to_hider
        return self.seeker_path_to_hider.pop(0)

    def __seeker_create_new_path_to_hider(self):
        """
            assuming that there is no path to hider but there are some visible hiders remain

            returns a new path to hider
        """
        cur_r, cur_c = self.problem.seeker.coordinate

        # assume that we are on the path to an announcement and we suddenly meet a hider
        # so that we will skip the announcement and prior the new hider
        if self.current_announcement:
            self.visible_announcements.insert( 0, self.current_announcement )
        self.current_announcement = None
        self.seeker_path_for_announcement = []

        # get path to the latest visible hider
        nexthider_coor = self.visibile_hider_coor.pop()
        res = astar.astar(
            grid=self.astar_map,
            start_coor=(cur_r, cur_c),
            goal_coor=nexthider_coor
        )
        return res

    def __seeker_choose_cell_on_path_for_announcement(self):
        """
            return coordinate of a cell on path for announcement
        """
        cur_r,cur_c = self.problem.seeker.coordinate
        R,C = self.seeker_path_for_announcement[0]
        if not Level2.is_adjacent(tile1=(cur_r,cur_c), tile2=(R,C)):
            path = astar.astar(
                grid=self.astar_map,
                start_coor=(cur_r, cur_c),
                goal_coor=(R,C)
            )
            path.pop()
            self.seeker_path_for_announcement = path + self.seeker_path_for_announcement
        return self.seeker_path_for_announcement.pop(0)
    
    def __seeker_check_unseen_cell_around_announcement(self):
        """
            returns new path to other cell in the region of the announcement that we have not seen;
            or None if there is no cell
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        ann_radius = self.problem.hiders[0].radius
        ann_coor = self.current_announcement['coordinate']
        for idrow in range(ann_coor[0] - ann_radius, ann_coor[0] + ann_radius + 1, +1):
            # check index validity
            if idrow < 0:
                break
            if idrow >= len(seeker.vision_map):
                break
            for idcol in range(ann_coor[1] - ann_radius, ann_coor[1] + ann_radius + 1, +1):
                # check index validity
                if idcol < 0:
                    break
                if idcol >= len(seeker.vision_map):
                    break
                if idrow == cur_r and idcol == cur_c:
                    continue
                if self.seen_map[idrow][idcol] == False and self.reachable[idrow][idcol] == True:
                    # cell in the region of the announcement but we have not seen it yet
                    path = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r, cur_c),
                        goal_coor=(idrow, idcol)
                    )
                    if not path or len(path) == 0:
                        self.reachable[idrow][idcol] = False
                    return path
        return None
    
    def __hider_take_turn(self, hider: Hider):
        """
            a hider in the list of hiders takes its turn:
                - increase count to announcement
                - if needed, raise an announcement and put it onto the map

            id: index of hider in the list of hider in the problem, and it is also ID of the hider
            returns nothing
        """
        hider.count_to_announcement += 1
        if hider.count_to_announcement == hider.step_to_announcement:
            if len(self.announcements_on_map) == self.total_hiders:
                # reset list of current announcements on the map
                self.announcements_on_map = []
            hider.count_to_announcement = 0
            announce = hider.announce()
            self.announcements_on_map.append( announce )
            if 1000 in self.problem.map_list[ announce.coordinate[0] ][ announce.coordinate[1] ]:
                self.problem.map_list[ announce.coordinate[0] ][ announce.coordinate[1] ] = [ announce ]
            else:
                self.problem.map_list[ announce.coordinate[0] ][ announce.coordinate[1] ].append( announce )

    def __seeker_blind_step_check_potential_directions(self):
        """
            returns 2 things:
                - LIST of direction (as a coordinate in terms of a tuple) that has maximum number of new and visible cells
                - the max number of new and visible cells
        """
        # avoid steping back to the previous step
        from copy import deepcopy
        last_r, last_c = self.last_step     # the previous coordinate of the agent
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate    # current coordinate of the seeker
        # find direction that has the maximum number of new and visible cell
        max_coordinate = []             # list of coordinate of cells with the largest cnt value
        max_count_val = -1
        # traverse all potential coordinate of the next step
        for dr, dc in Level2.ADJACENT:
            idr = cur_r + dr
            idc = cur_c + dc
            if idr < 0 or idr >= len(seeker.vision_map) or idc < 0 or idc >= len(seeker.vision_map[0]):
                # index out of range
                continue
            if idr == last_r and idc == last_c:
                # avoid steping back to the previous cell
                continue
            if -1 in seeker.origin_map[idr][idc]:
                # skip wall (cannot get through)
                continue
            
            # get vision map 
            visionmap = self.vision_maps.get( (idr, idc) )
            if visionmap == None:
                # check for the existence of the vision map of this cell
                tmp_seeker = Seeker(
                    coordinate=(idr, idc)
                )
                tmp_seeker.origin_map = seeker.origin_map
                tmp_seeker.skeleton_map = seeker.skeleton_map
                tmp_seeker.vision()
                visionmap = deepcopy(tmp_seeker.vision_map)
                self.vision_maps[ (idr, idc) ] = visionmap
            cnt = 0

            # traverse vision map of the potentially next step
            for idrow in range(idr-seeker.radius, idr+seeker.radius + 1, +1):
                # check index validity
                if idrow < 0:
                    continue
                if idrow >= len(visionmap):
                    break
                for idcol in range(idc-seeker.radius, idc+seeker.radius + 1, +1):
                    if idcol == idc and idrow == idr:
                        continue
                    # check index validity
                    if idcol < 0:
                        continue
                    if idcol >= len(visionmap):
                        break
                    if visionmap[idrow][idcol] == True and self.seen_map[idrow][idcol] == False:
                        cnt += 1
            if cnt > max_count_val:
                max_count_val = cnt
                max_coordinate = [ (idr, idc) ]
            elif cnt == max_count_val:
                max_coordinate.append( (idr, idc) )
        return max_coordinate, max_count_val

    def __seeker_find_goal_for_path_announcement(self):
        seeker = self.problem.seeker
        R,C = self.current_announcement['coordinate']
        ann_radius = self.problem.hiders[0].radius
        for idrow in range(R - ann_radius, R + ann_radius + 1, +1):
            # check validity of index
            if idrow < 0:
                continue
            if idrow >= len(seeker.origin_map):
                break
            for idcol in range(C - ann_radius, C + ann_radius + 1, +1):
                # check validity of index
                if idcol < 0:
                    continue
                if idcol >= len(seeker.origin_map[0]):
                    break
                if self.seen_map[idrow][idcol] == False and self.reachable[idrow][idcol] == True:
                    return R,C
        return None

    def __seeker_blind_step_find_new_unseen_cell(self):
        """
            all cells around are all seen and we need to find the possibly nearest cell that we have not seen yet

            - return None if there is no unseen cell => we have seen ALL THE CELL BUT THE GAME HAS NOT STOPPED => LOSE
            - return the path (list of coordinate) from current cell to goal cell, excluding start cell
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        radius = 2
        continue_flag = True        # to check whether we expanded the whole map, stop if it is False
        while continue_flag:
            # BFS with level as radius
            if continue_flag:
                continue_flag = not continue_flag
            cells = []              # list of cells's info on this level of radius which are unseen
                                    # a cell info is {'coordinate': (), 'distance': int}
            if cur_r - radius >= 0:
                if not continue_flag:
                    continue_flag = not continue_flag
                row = cur_r - radius
                for col in range(cur_c - radius, cur_c + radius + 1, +1):
                    if col < 0:
                        continue
                    if col >= len(seeker.origin_map[0]):
                        break
                    if -1 in seeker.origin_map[row][col]:
                        # skip wall
                        continue
                    if self.seen_map[row][col] == False:
                        cells.append(
                            {
                                'coordinate': (row, col),
                                'distance': abs(row - cur_r) + abs(col - cur_c) # manhattan distance
                            }
                        )

            if cur_r + radius < len(seeker.origin_map):
                if not continue_flag:
                    continue_flag = not continue_flag
                row = cur_r + radius
                for col in range(cur_c - radius, cur_c + radius + 1, +1):
                    if col < 0:
                        continue
                    if col >= len(seeker.origin_map[0]):
                        break
                    if -1 in seeker.origin_map[row][col]:
                        # skip wall
                        continue
                    if self.seen_map[row][col] == False:
                        cells.append(
                            {
                                'coordinate': (row, col),
                                'distance': abs(row - cur_r) + abs(col - cur_c) # manhattan distance
                            }
                        )

            if cur_c - radius >= 0:
                if not continue_flag:
                    continue_flag = not continue_flag
                col = cur_c - radius
                for row in range(cur_r - radius, cur_r + radius + 1, +1):
                    if row < 0:
                        continue
                    if row >= len(seeker.origin_map):
                        break
                    if -1 in seeker.origin_map[row][col]:
                        # skip wall
                        continue
                    if self.seen_map[row][col] == False:
                        cells.append(
                            {
                                'coordinate': (row, col),
                                'distance': abs(row - cur_r) + abs(col - cur_c) # manhattan distance
                            }
                        )

            if cur_c + radius < len(seeker.origin_map[0]):
                if not continue_flag:
                    continue_flag = not continue_flag
                col = cur_c + radius
                for row in range(cur_r - radius, cur_r + radius + 1, +1):
                    if row < 0:
                        continue
                    if row >= len(seeker.origin_map):
                        break
                    if -1 in seeker.origin_map[row][col]:
                        # skip wall
                        continue
                    if self.seen_map[row][col] == False:
                        cells.append(
                            {
                                'coordinate': (row, col),
                                'distance': abs(row - cur_r) + abs(col - cur_c) # manhattan distance
                            }
                        )
            
            # print('\tnormal path list')
            if len(cells) == 1:
                # there is only 1 cell to choose

                # check if the cell is reachable
                
                # print('\tFrom', (cur_r, cur_c), 'to', cells[0].get('coordinate'))
                path = astar.astar(
                    grid=self.astar_map,
                    start_coor=(cur_r, cur_c),
                    goal_coor=cells[0].get('coordinate')
                )
                if path:
                    # reachable
                    return path
                
            elif len(cells) > 1:
                # there are many cells to choose => choose cell with min distance
                min_distance = [ cells[0] ]     # list of cells that has minimum manhattan distance
                for el in cells[1:]:
                    if el['distance'] < min_distance[0]['distance']:
                        min_distance = [ el ]
                    elif el['distance'] == min_distance[0]['distance']:
                        min_distance.append( el )
                
                # check these min distance cells
                for min in min_distance:
                    # print('\tFrom', (cur_r,cur_c), 'to', min.get('coordinate'))
                    path = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r,cur_c),
                        goal_coor=min.get('coordinate')
                    )
                    if path:
                        return path
            radius += 1

    def __seeker_blind_step(self):
        """
            seeker has no info about hiders or announcement => it must take a blind step (a step without info)

            returns 1 of the following:
                - `None` if the seeker cannot go to any direction
                - a path as a list of coordinates we can go through (as a self.normal_path)
        """
        last_r, last_c = self.last_step     # the previous coordinate of the agent
        potential_cells, max_new_vision = self.__seeker_blind_step_check_potential_directions()
        if len(potential_cells) == 0:
            # the seeker is blocked and CANNOT GO ANYWHERE
            return None
        elif max_new_vision == 0:
            # no new vision
            res = self.__seeker_blind_step_find_new_unseen_cell()
            return res
        elif len(potential_cells) == 1:
            return [ potential_cells[0] ]
        elif len(potential_cells) > 1:
            max_distance = -1
            max_distance_coor = None
            for i,j in potential_cells:
                # i - row, j - col
                tmp_dis = abs(last_r - i) + abs(last_c - j)
                if tmp_dis > max_distance:
                    max_distance_coor = (i,j)
            return [ max_distance_coor ]

    def run(self):
        from copy import deepcopy
        seeker = self.problem.seeker
        self.visibile_hider_coor = []
        self.visible_announcements = []                      # list of info of announcement, including {'coordinate': (), 'hider_id': int}
        self.vision_maps = {                    # map a coordinate with the corresponding vision map for later reuse
            # tuple : list
        }

        self.seen_map = [                       # list of cells which seeker has already seen
            [True if cell == -1 else False for cell in row ] for row in seeker.skeleton_map
        ]                                       # True / False
        # self.visited_map = deepcopy(self.seen_map)  # list of cells which seeker has already visited
                                                # True / False
        
        seeker_turn = True
        self.seeker_path_to_hider = []          # step by step, 0..n-1  
        self.seeker_path_for_announcement = []  # step by step, 0..n-1
        self.seeker_normal_path = []            # seeker is on its path and this list keeps cells on that path which seeker has not reached
                                                # step by step, 0..n-1
        self.reachable = [[ None for cell in row ] for row in self.problem.skeleton_map]
        self.total_hiders = len(self.problem.hiders)
        self.astar_map = [ [False if cell == -1 else True for cell in row] for row in seeker.skeleton_map ]
        self.announcements_on_map = []          # list of announcements currently is on the map 
        self.current_announcement = None        # current announcement's info {'coordinate': (), 'hider_id': int}
        self.last_step = seeker.coordinate      # coordinate of the previous step
                                                # use when we take a blind step, we need to avoid steping back to the previous step
        while True:
            if not seeker_turn: # it is hiders' turn
                # traverse all hiders in the map
                for hider in self.problem.hiders:
                    # skip if hider has been caught

                    self.__hider_take_turn(hider=hider)

                    yield StateForFE(
                        player=hider,
                        old_row=hider.coordinate[0],
                        old_col=hider.coordinate[1],
                        new_row=hider.coordinate[0],
                        new_col=hider.coordinate[1],
                        announcements=self.announcements_on_map
                    )
                seeker_turn = not seeker_turn
            # ----------------------------------------------------------------------
            # ---------------------------SEEKER'S TURN------------------------------
            else:   # seeker turn
                seeker_turn = not seeker_turn
                cur_r, cur_c = seeker.coordinate    # current position of the seeker

                # check if seeker is in the same tile with a hider
                self.__seeker_check_found_hider()
                # ----------------------------------------
                # ----------------------------------------
                # check if all hiders are found
                if self.total_hiders == 0:
                    # end game, success
                    return
                
                # check if we reach all the cells
                flag_reach_all = True
                for row in self.reachable:
                    for cell in row:
                        if cell == None:
                            flag_reach_all = not flag_reach_all
                            break
                    if not flag_reach_all:
                        break
                if flag_reach_all:
                    # reach all
                    # => end game, failed
                    return
                
                # ----------------------------------------
                # ----------------------------------------
                # check appearance of new hiders and announcements around seeker
                self.__seeker_check_new_hider_and_announcement()
                # ----------------------------------------
                # ----------------------------------------
                # check whether we are on the way to a hider
                if len(self.seeker_path_to_hider):
                    # print('choose cell to hider')
                    R,C = self.__seeker_choose_cell_on_path_to_hider()
                    self.move_seeker_to( coordinate=(R,C) )
                    seeker.score -= 1
                    yield StateForFE(
                        player=seeker,
                        old_row=self.last_step[0],
                        old_col=self.last_step[1],
                        new_row=R,
                        new_col=C,
                        announcements=self.announcements_on_map
                    )
                    self.seeker_normal_path = []
                    continue
                # ----------------------------------------
                # ----------------------------------------
                # check whether we have seen hiders
                if len(self.visibile_hider_coor):
                    # print('create path to hider')
                    self.seeker_path_to_hider = self.__seeker_create_new_path_to_hider()
                    R,C = self.seeker_path_to_hider.pop(0)
                    self.move_seeker_to( coordinate=(R,C) )
                    seeker.score -= 1
                    yield StateForFE(
                        player=seeker,
                        old_row=self.last_step[0],
                        old_col=self.last_step[1],
                        new_row=R,
                        new_col=C,
                        announcements=self.announcements_on_map
                    )
                    self.seeker_normal_path = []
                    continue
                # ----------------------------------------
                # ----------------------------------------
                # check whether we are on the path to an announcement
                if len(self.seeker_path_for_announcement):
                    # print('choose cell to announcement')
                    R,C = self.__seeker_choose_cell_on_path_for_announcement()
                    self.move_seeker_to( coordinate=(R,C) )
                    seeker.score -= 1
                    yield StateForFE(
                        player=seeker,
                        old_row=self.last_step[0],
                        old_col=self.last_step[1],
                        new_row=R,
                        new_col=C,
                        announcements=self.announcements_on_map
                    )
                    self.seeker_normal_path = []
                    if len(self.seeker_path_for_announcement) == 0:
                        res = self.__seeker_check_unseen_cell_around_announcement()
                        if res:
                            self.seeker_path_for_announcement = res
                            continue
                # ----------------------------------------
                # ----------------------------------------
                # there are other visible announcements
                if len(self.visible_announcements):
                    # print('create path for announcement')
                    while len(self.visible_announcements):
                        self.current_announcement = self.visible_announcements.pop(0)
                        goal = self.__seeker_find_goal_for_path_announcement()
                        if goal:
                            if goal == (cur_r, cur_c):
                                goal = None
                            elif self.reachable[goal[0]][goal[1]]:
                                break
                    if goal:
                        self.seeker_path_for_announcement = astar.astar(
                            grid=self.astar_map,
                            start_coor=(cur_r, cur_c),
                            goal_coor=goal
                        )
                        self.seeker_path_for_announcement
                        R,C = self.seeker_path_for_announcement.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        yield StateForFE(
                            player=seeker,
                            old_row=self.last_step[0],
                            old_col=self.last_step[1],
                            new_row=R,
                            new_col=C,
                            announcements=self.announcements_on_map
                        )
                        self.seeker_normal_path = []
                        continue
                # ----------------------------------------
                # ----------------------------------------
                # blind step
                if len(self.seeker_normal_path) == 0:
                    # print('create normal path')
                    self.seeker_normal_path = self.__seeker_blind_step()
                    if self.seeker_normal_path == None:
                        print('give up')
                        return
                R,C = self.seeker_normal_path.pop( 0 )
                self.move_seeker_to( coordinate=(R,C) )
                seeker.score -= 1
                yield StateForFE(
                    player=seeker,
                    old_row=self.last_step[0],
                    old_col=self.last_step[1],
                    new_row=R,
                    new_col=C,
                    announcements=self.announcements_on_map
                )
# if __name__ == '__main__':
#     lv2 = Level2('test/map1_2.txt')
#     for state in lv2.run():
#         if state.player.signature == 'Hider':
#             # print('Hider\'s turn.')
#             pass
#         elif state.player.signature == 'Seeker':
#             # print('Seeker\'s turn:', end=' ')
#             print(state.old_coordinate, '-->', state.new_coordinate)

            
if __name__ == '__main__':
    lv1 = Level1('test/map1_1.txt')
    for state in lv1.run():
        print(state.old_coordinate, '-->', state.new_coordinate)

# if __name__ == '__main__':
#     lv2 = Level2('test/map1_1.txt')
#     for state in lv2.run():
#         print(state.old_coordinate, '-->', state.new_coordinate)