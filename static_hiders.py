import math
from problem import *
from obstacle import *
from player import *
from pq import *
import astar
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

            stop_flag = 0

            while not open_list.empty():
                stop_flag += 1
                _, current = open_list.get()

                if current == target_coor:
                    # Reconstruct the path and return it
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.reverse()
                    return path
                
                stop_flag1 = 0
                for dr, dc in Level1.ADJACENT:
                    stop_flag1 += 1
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
                    if stop_flag1 > 150:
                        break
                
                if stop_flag > 150:
                    break
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

            if len(max_coordinate) == 0:
                # is blocked, cannot move to any adjacent cells
                return None
                # many cells share a common heuristic value
            elif max_count_val == 0:
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
                        # for x in cells:
                            # print('cells:', x['coordinate'])
                        for cell_data in cells:
                            res = self.__move_towards_target(cell_data['coordinate'])
                            if res:
                                for i, j in res:
                                    # print('res:', res)
                                    if (i, j != self.moves_stack[-1]):
                                        return [(i, j)]
                    radius += 1
                    stop_flag = True
                        # if (radius + cur_c < len(seeker.origin_map[0]) or radius + cur_c > 0) and (radius + cur_r < len(seeker.origin_map) or radius + cur_r > 0):
                        #     radius += 1
                        # else:
                        #     # No path found to any reachable unseen cell
                        #     return False

            elif len(max_coordinate) == 1:
                return [max_coordinate[0]]
            elif len(max_coordinate) > 1:
                 # h != 0: choose the cell whose Manhattan distance from the previous cell is the largest
                max_distance = -1
                max_distance_coor = None
                for i, j in max_coordinate:
                    tmp_dis = abs(last_r - i) + abs(last_c - j)
                    if tmp_dis > max_distance:
                        max_distance_coor = (i, j)
                return [max_distance_coor]
            
    
    def __hider_take_turn(self, hider: Hider):
        """
        A hider in the list of hiders takes its turn:
            - Increase count to announcement
            - If needed, raise an announcement and put it onto the map

        id: Index of hider in the list of hider in the problem, and it is also ID of the hider
        Returns nothing
        """
        hider.count_to_announcement += 1
        if hider.count_to_announcement >= hider.step_to_announcement:
            # Reset count to announcement
            hider.count_to_announcement = 0

            # Raise an announcement for the hider
            announce = hider.announce()
            # print('ANNOUNCE', announce.coordinate)
            self.announcements_on_map.append(announce)
            row, col = announce.coordinate

            # Place the new announcement on the map
            if 1000 in self.problem.map_list[row][col]:
                self.problem.map_list[row][col] = [announce]
            else:
                self.problem.map_list[row][col].append(announce)

    def __seeker_check_found_hider(self):
        """
        Check if the seeker is currently in the same tile with a particular hider.
        Remove the hider and its associated announcement from the game.
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        for element in self.problem.map_list[cur_r][cur_c]:
            if not isinstance(element, int) and element.signature == 'Hider':
                # A hider is found
                self.total_hiders -= 1
                seeker.score += 20
                # print('Hider found at', (cur_r, cur_c))
                self.hider_coor.remove((cur_r, cur_c))
                self.problem.hiders.remove(element)
                self.problem.map_list[cur_r][cur_c].remove(element)

                # Remove all of its announcements in the list of visible announcements
                for ann in self.announcement_coor:
                    self.announcement_coor.remove(ann)

                # Remove the associated announcement from the map
                if 1000 in self.problem.map_list[cur_r][cur_c]:
                    self.problem.map_list[cur_r][cur_c] = [x for x in self.problem.map_list[cur_r][cur_c] if not isinstance(x, Announcement)]
                else:
                    self.problem.map_list[cur_r][cur_c] = [x for x in self.problem.map_list[cur_r][cur_c] if not isinstance(x, Announcement)]
                break


    def __check_there_hider_or_announcement(self, seeker : Seeker):
        from copy import deepcopy
        from copy import copy

        r, c = seeker.coordinate

        self.moves_stack = [ copy(seeker.coordinate) ]  
        self.cur_vision_maps = self.vision_maps.get( (r,c) )
        # print('cur:', r, c)
        # print('previous step:', self.moves_stack[-1])
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
                                self.hider_coor.append((r + idrow, c + idcol))
                                hider_found = True
                            elif element.signature == 'Announcement':
                                self.announcement_coor.append((r + idrow, c + idcol))
                                announcement_found = True

                if hider_found or announcement_found:
                    break  # Exit the loop if either a Hider or Announcement is found

            if hider_found or announcement_found:
                break  # Exit the loop if either a Hider or Announcement is found

    def __seeker_go_to_hider(self, seeker : Seeker, seeker_index: tuple):
        """
        there is hider in seeker vision, goes to that announcement
        """

        from copy import deepcopy

        r, c = seeker_index
        # there is a hider, go to this
        if len(self.hider_coor) > 1 and seeker.coordinate == self.hider_coor:
            # SUCESSFULLY FOUND HIDER
            # print('FOUND HIDER:', (self.hider_coor), "SEEKER:", (seeker.coordinate))
            return
        else:
            # only 1 hider
            hider_coor = self.hider_coor[0]
            # print('hider', hider_coor)
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
                    
                    hiderr, hiderc = hider_coor


                    if hiderr == i and hiderc == j:
                        self.current_state_end = True
                        self.all_state.append(StateForFE(
                            seeker= seeker,
                            hiders= self.problem.hiders,
                            announcements=self.announcements_on_map,
                            score= seeker.score,
                            is_end=self.current_state_end
                        ))


                    self.all_state.append(StateForFE(
                        seeker= seeker,
                        hiders= self.problem.hiders,
                        announcements=self.announcements_on_map,
                        score= seeker.score,
                        is_end=self.current_state_end
                    ))
                    self.moves_stack.append((i, j))


    def __seeker_go_to_announcement(self, seeker : Seeker, seeker_index: tuple):
        """
        there is announcement in seeker vision, goes to that announcement
        update evertime see new announcement, set goal if see hider
        """
        from copy import deepcopy
        r, c = seeker_index
        
        cur_announcement = self.announcement_coor.pop(0)
        # print('actual announcement', cur_announcement)

        res = self.__move_towards_target(cur_announcement)
        # print('seeker move to announcement', cur_announcement)

        # for i in res:
        #     print(i)

        if res:
            for i, j in res:
                # print('seeker move to announcement', (i, j))
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

                self.all_state.append(StateForFE(
                            seeker= seeker,
                            hiders= self.problem.hiders,
                            announcements=self.announcements_on_map,
                            score= seeker.score,
                            is_end=self.current_state_end
                        ))
                self.moves_stack.append((i, j))
                
                #========================================
                # print('MOVE TOWARDS ANNOUNCEMENT')
                # for row in self.problem.map_list:
                #     for cell in row:
                #         if -1 in cell:
                #             print('x', end=' ')  # Wall
                #         elif seeker in cell:
                #             print('S', end=' ')  # Seeker
                #         elif any(isinstance(obj, Hider) for obj in cell):
                #             print('H', end=' ')  # Hider
                #         elif any(isinstance(obj, Announcement) for obj in cell):
                #             print('A', end=' ')  # Announcement
                #         else:
                #             print('-', end=' ')  # Empty cell
                #     print()


                for row in range(i-seeker.radius, i+seeker.radius+1, +1):
                    if row < 0:
                        continue
                    if row >= len(self.problem.map_list):
                        break
                    for col in range(j-seeker.radius,j+seeker.radius+1, +1):
                        if col < 0:
                            continue
                        if col >= len(self.problem.map_list[0]):
                            break
                        if self.seen_map[row][col] == True:
                            for cell in self.problem.map_list[row][col]:
                                if not isinstance(cell, int):
                                    if cell.signature == 'Hider':
                                        self.hider_coor.append((row, col))
                                        return

    def run(self)->list:
        from copy import deepcopy, copy
        seeker = self.problem.seeker
        self.hider_coor = []
        self.announcement_coor = []
        self.seeker_path = []
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
        self.total_hiders = len(self.problem.hiders)
        self.all_state = []

        self.current_state_end = False
        while True:
            if not seeker_turn:
                # # hider raise announcement
                hider = self.problem.hiders[0]
                self.__hider_take_turn(hider)

                self.all_state.append(StateForFE(
                    seeker= seeker,
                    hiders= self.problem.hiders,
                    announcements=self.announcements_on_map,
                    score= seeker.score,
                    is_end=self.current_state_end
                ))
                seeker_turn = not seeker_turn

            # SEEKER MOVE
            else:
                seeker_turn = not seeker_turn
                r,c = seeker.coordinate


                # CHECK IF HIDER FOUNDED
                self.__seeker_check_found_hider()
                if self.total_hiders == 0:
                    # done game
                    self.current_state_end = True
                    self.all_state.append(StateForFE(
                        seeker= seeker,
                        hiders= self.problem.hiders,
                        announcements=self.announcements_on_map,
                        score= seeker.score,
                        is_end=self.current_state_end
                    ))
                    break


                # CHECK IN CASE SEEKER CANNOT FIND OUT HIDER -> GIVE UP
                flag_reach_all = True
                for row in self.seen_map:
                    for cell in row:
                        if cell == False:
                            flag_reach_all = not flag_reach_all
                    if not flag_reach_all: break
                if flag_reach_all:
                    # traverse through the whole map, return
                    break
                

                self.__check_there_hider_or_announcement(seeker)
                
                if len(self.hider_coor) or len(self.announcement_coor):
                    seeker.score -= 1
                    if len(self.hider_coor):
                        self.__seeker_go_to_hider(seeker, (r,c))
                    elif len(self.announcement_coor):
                        # there is an announcement, find path to announcement
                        self.__seeker_go_to_announcement(seeker, (r,c))

                else:
                    #  THERE IS NO HIDER OR ANNOUNCEMENT IN THE SEEKER RANGE, SO IT WILL TAKE A BLIND STEP
                    res = self.__choose_step_no_info()

                    if len(res) == 0:
                        # No new vision
                        return [],False
                    

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
                            # print('append seeker', (R, C))
                        else:
                            self.problem.map_list[R][C].append( seeker )

                        # decrease seeker score for each move
                        seeker.score -= 1

                        self.all_state.append(StateForFE(
                            seeker= seeker,
                            hiders= self.problem.hiders,
                            announcements=self.announcements_on_map,
                            score= seeker.score,
                            is_end=self.current_state_end
                        ))
                        self.moves_stack.append( (R,C) )  

        return self.all_state
             
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
        if tile1 == tile2:
            return True
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
            set reachability of the new cell to True

            no return
        """
        seeker = self.problem.seeker
        if seeker.coordinate == coordinate:
            raise ValueError('New cell == current cell')
        r,c = seeker.coordinate
        self.last_step = (r,c)

        next_r, next_c = coordinate

        if not Level2.is_adjacent(tile1=(r,c), tile2=(next_r, next_c)):
            raise ValueError('Cannot go to non-adjacent tile')
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
        if len(self.problem.map_list[r][c]) == 0:
            self.problem.map_list[r][c] = [1000]

        self.reachable[next_r][next_c] = True

        # assign new coordinate to seeker
        seeker.coordinate = coordinate
        
    def __seeker_check_found_hider(self):
        """
            check if the seeker is currently in the same tile with a particular hider
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate

        # check the current cell
        for element in self.problem.map_list[cur_r][cur_c]:
            if not isinstance(element, int) and element.signature == 'Hider':
                # contains a Hider
                self.total_hiders -= 1
                seeker.score += 20

                # remove hider's coordinate from visible_hider_coor list
                if (cur_r, cur_c) in self.visibile_hider_coor:
                    self.visibile_hider_coor.remove( (cur_r, cur_c) )

                # remove hider from the problem
                self.problem.hiders.remove(element)
                self.problem.map_list[cur_r][cur_c].remove(element)
                if len(self.problem.map_list[cur_r][cur_c]) == 0:
                    self.problem.map_list[cur_r][cur_c] = [1000]
                
                # delete all of its announcements
                for ann in self.visible_announcements:
                    if ann['hider_id'] == element.id:
                        self.visible_announcements.remove( ann )
                if self.current_announcement and self.current_announcement['hider_id'] == element.id:
                    self.current_announcement = None
                    self.seeker_path_for_announcement = []
                
                for ann in self.announcements_on_map:
                    if ann.hider.id == element.id:
                        self.announcements_on_map.remove( ann )
                
                break

    def __seeker_check_new_hider_and_announcement(self):
        """
            check the vision map from current tile to find new hiders and announcements in the field of view 
            returns nothing
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
                # check index validity
                if idcol < 0:
                    continue
                if idcol >= len(visionmap[0]):
                    break
                if visionmap[idrow][idcol] == True: # cell is visible
                    self.seen_map[idrow][idcol] = True
                    if -1 in self.problem.map_list[idrow][idcol]:
                        self.reachable[idrow][idcol] = False
                    else:
                        # as it is visible and it is not a wall, it is reachable
                        self.reachable[idrow][idcol] = True
                
                # check element in this cell
                for component in self.problem.map_list[idrow][idcol]:
                    if not isinstance(component, int): # not -1 or 1000 => it is an object
                        if component.signature == 'Hider' and visionmap[idrow][idcol] == True: # is a VISIBLE hider
                            if not (component.coordinate in self.visibile_hider_coor):
                                # if has not been seen
                                self.visibile_hider_coor.append( component.coordinate )
                                path = astar.astar(
                                    grid=self.astar_map,
                                    start_coor=(cur_r, cur_c),
                                    goal_coor=component.coordinate
                                )
                                if path == None:
                                    self.reachable[component.coordinate[0]][component.coordinate[1]] = False
                                elif len(self.seeker_path_to_hider) > 0 and len(path) < len(self.seeker_path_to_hider):
                                    # if this path is better than the current path
                                    self.seeker_path_to_hider = path
                        elif component.signature == 'Announcement':
                            # check if announcement has been seen
                            existed = False
                            for ann in self.visible_announcements:
                                if component.coordinate == ann['coordinate']:
                                    existed = not existed # TRUE
                                    break
                            if not existed: # => new announcement
                                new_ann = {
                                    'coordinate': (component.coordinate[0], component.coordinate[1]),
                                    'hider_id': component.hider.id,
                                }
                                

                                # check if new path is better than current path
                                path = astar.astar(
                                    grid=self.astar_map,
                                    start_coor=(cur_r, cur_c),
                                    goal_coor=component.coordinate
                                )
                                if path == None:
                                    self.reachable[component.coordinate[0]][component.coordinate[1]] = False
                                elif self.current_announcement != None and len(self.seeker_path_for_announcement) > 0 and len(path) < len(self.seeker_path_for_announcement):
                                    self.visible_announcements.append( self.current_announcement )
                                    self.current_announcement = new_ann
                                    self.seeker_path_for_announcement = path
                                else:
                                    self.visible_announcements.append( new_ann )

    def __seeker_choose_cell_on_path_to_hider(self):
        """
            assuming that seeker is on the way to a hider

            return coordinate of the cell to go next
        """
        cur_r, cur_c = self.problem.seeker.coordinate
        R,C = self.seeker_path_to_hider[0]
        if not Level2.is_adjacent(tile1=(cur_r, cur_c), tile2=(R,C)):
            # find new path to the goal (which is the last tile in the path: path[-1])
            self.seeker_path_to_hider = astar.astar(
                grid=self.astar_map,
                start_coor=(cur_r, cur_c),
                goal_coor=self.seeker_path_to_hider[-1]
            )
        return self.seeker_path_to_hider[0]

    def __seeker_create_new_path_to_hider(self):
        """
            assuming that there is no path to hider but there are some visible hiders remain

            returns a new path to hider or None if there is no path
        """
        cur_r, cur_c = self.problem.seeker.coordinate

        # assume that we are on the path to an announcement and we suddenly meet a hider
        # so that we will skip the announcement and prior the new hider
        if self.current_announcement:
            # assign it back to list of visible announcements
            self.visible_announcements.append( self.current_announcement )
        self.current_announcement = None
        self.seeker_path_for_announcement = []

        # get path to the latest visible hider
        while len(self.visibile_hider_coor):
            nexthider_coor = self.visibile_hider_coor[-1]
            res = astar.astar(
                grid=self.astar_map,
                start_coor=(cur_r, cur_c),
                goal_coor=nexthider_coor
            )
            if res and len(res) > 0:
                return res
        return None # will not occur
    
    def __seeker_choose_cell_on_path_for_announcement(self):
        """
            return coordinate of a cell to go next on path for announcement

            return None if we should NOT go on this path
        """
        cur_r,cur_c = self.problem.seeker.coordinate
        while len(self.seeker_path_for_announcement):
            R,C = self.seeker_path_for_announcement[0]
            if (R,C) == (cur_r,cur_c):
                self.seeker_path_for_announcement.pop(0)
                continue

            if not Level2.is_adjacent(tile1=(cur_r,cur_c), tile2=(R,C)):
                self.seeker_path_for_announcement = astar.astar(
                    grid=self.astar_map,
                    start_coor=(cur_r, cur_c),
                    goal_coor=self.seeker_path_for_announcement[-1]
                )
                R,C = self.seeker_path_for_announcement[0]
            return R,C
        return None
    
    def __seeker_get_path_to_unseen_cell_of_announcement(self):
        """
            returns new path to other cell in the region of the announcement that we have not seen;
            or None if there is no cell
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        ann_radius = self.problem.hiders[0].radius
        ann_coor = self.current_announcement['coordinate']
        list_of_path = []
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
                if self.seen_map[idrow][idcol] == False and self.reachable[idrow][idcol] != False:
                    # cell in the region of the announcement but we have not seen it yet
                    path = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r, cur_c),
                        goal_coor=(idrow, idcol)
                    )
                    if path == None:
                        self.reachable[idrow][idcol] = False
                    else:
                        list_of_path.append( path )
        
        if list_of_path == []:
            # no path was found
            return None
        # choose the nearest cell
        min_distance_path = list_of_path[0]
        for path in list_of_path[1:]:
            if len(path) < len(min_distance_path):
                min_distance_path = path
        return min_distance_path
    
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
                max_count_val += cnt - max_count_val
                max_coordinate = [ (idr, idc) ]
            elif cnt == max_count_val:
                max_coordinate.append( (idr, idc) )
        if max_coordinate == []:
            max_coordinate = [(last_r, last_c)]
        return max_coordinate, max_count_val

    def __seeker_find_goal_for_path_announcement(self):
        """
            return a goal that is reachable from current cell

            or return None
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
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
                if -1 in self.problem.map_list[idrow][idcol]:
                    continue
                if self.seen_map[idrow][idcol] == False:
                    self.seeker_path_for_announcement = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r, cur_c),
                        goal_coor=(idrow, idcol)
                    )
                    if self.seeker_path_for_announcement == None:
                        self.reachable[idrow][idcol] = False
                        self.seeker_path_for_announcement = []
                    else:
                        if len(self.seeker_path_for_announcement):
                            return R,C
        self.seeker_path_for_announcement = []
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
                        cells.append( (row, col) )

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
                        cells.append( (row, col) )

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
                        cells.append( (row, col) )

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
                        cells.append( (row, col) )
            
            # print('\tnormal path list')
            if len(cells) == 1:
                # there is only 1 cell to choose

                # check if the cell is reachable
                
                # print('\tFrom', (cur_r, cur_c), 'to', cells[0].get('coordinate'))
                path = astar.astar(
                    grid=self.astar_map,
                    start_coor=(cur_r, cur_c),
                    goal_coor=cells[0]
                )
                if path == None:
                    self.reachable[cells[0][0]][cells[0][1]] = False
                return path
            elif len(cells) > 1:
                # there are many cells to choose => choose cell with min distance
                min_path = None
                for coor in cells:
                    path = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r, cur_c),
                        goal_coor=coor
                    )
                    if path == None:
                        self.reachable[ coor[0] ][ coor[1] ] = False
                        continue
                    if min_path == None or len(path) < len(min_path):
                        min_path = path
                return min_path
            radius += 1
        return None

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
            # print('no potential cell')
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

    def __seeker_shortest_path_to_announcement(self, announcement):
        """
            return the shortest path to the nearest cell in region of announcement

            return None if there is no path
        """
        seeker = self.problem.seeker
        cur_r, cur_c = seeker.coordinate
        ann_radius = self.problem.hiders[0].radius
        ann_coor = announcement['coordinate']
        list_of_path = []
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
                if self.seen_map[idrow][idcol] == False and self.reachable[idrow][idcol] != False:
                    # cell in the region of the announcement but we have not seen it yet
                    path = astar.astar(
                        grid=self.astar_map,
                        start_coor=(cur_r, cur_c),
                        goal_coor=(idrow, idcol)
                    )
                    if path == None:
                        self.reachable[idrow][idcol] = False
                    else:
                        list_of_path.append( path )
        
        if list_of_path == []:
            # no path was found
            return None
        # choose the nearest cell
        min_distance_path = list_of_path[0]
        for path in list_of_path[1:]:
            if len(path) < len(min_distance_path):
                min_distance_path = path
        return min_distance_path

    def run(self):
        from copy import deepcopy
        all_states = []
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
                seeker_turn = not seeker_turn
                # traverse all hiders in the map
                for hider in self.problem.hiders:
                    # skip if hider has been caught

                    self.__hider_take_turn(hider=hider)
                all_states.append(
                    StateForFE(
                        hiders=self.problem.hiders,
                        seeker=seeker,
                        announcements=self.announcements_on_map,
                        is_end=False,
                        score=seeker.score
                    )
                )
            # ----------------------------------------------------------------------
            # ---------------------------SEEKER'S TURN------------------------------
            else:
                seeker_turn = not seeker_turn

                # current position of the seeker
                cur_r, cur_c = seeker.coordinate 
                self.reachable[cur_r][cur_c] = True

                # check if seeker is in the same tile with a hider
                self.__seeker_check_found_hider()

                # ----------------------------------------
                # ----------------------------------------
                # check if all hiders are found
                if self.total_hiders == 0:
                    # end game, SUCCESS
                    all_states.append(
                        StateForFE(
                            hiders=self.problem.hiders,
                            seeker=seeker,
                            announcements=self.announcements_on_map,
                            is_end=True,
                            score=seeker.score
                        )
                    )
                    return all_states
                
                # ----------------------------------------
                # ----------------------------------------
                # check if we have reached all the cells
                flag_reach_all = True
                for row in self.reachable:
                    for cell in row:
                        if cell == None:
                            flag_reach_all = not flag_reach_all # FALSE
                            break
                    if not flag_reach_all:
                        break
                if flag_reach_all and self.visibile_hider_coor == []:
                    # reached all => end game, FAILED
                    all_states.append(
                        StateForFE(
                            hiders=self.problem.hiders,
                            seeker=seeker,
                            announcements=self.announcements_on_map,
                            is_end=True,
                            score=seeker.score
                        )
                    )
                    return all_states
                
                # ----------------------------------------
                # ----------------------------------------
                # check appearance of new hiders and announcements around seeker
                self.__seeker_check_new_hider_and_announcement()

                # ----------------------------------------
                # ----------------------------------------
                # check whether we are on the way to a hider
                if len(self.seeker_path_to_hider) > 0:
                    R,C = self.__seeker_choose_cell_on_path_to_hider()
                    self.seeker_path_to_hider.pop(0)
                    self.move_seeker_to( coordinate=(R,C) )
                    seeker.score -= 1
                    all_states.append(
                        StateForFE(
                            hiders=self.problem.hiders,
                            seeker=seeker,
                            announcements=self.announcements_on_map,
                            is_end=False,
                            score=seeker.score
                        )
                    )
                    self.seeker_normal_path = []
                    continue

                # ----------------------------------------
                # ----------------------------------------
                # check whether we have any visible hiders
                if len(self.visibile_hider_coor):
                    res = self.__seeker_create_new_path_to_hider()
                    if res != None:
                        self.seeker_path_to_hider = res
                        R,C = self.seeker_path_to_hider.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        all_states.append(
                            StateForFE(
                                hiders=self.problem.hiders,
                                seeker=seeker,
                                announcements=self.announcements_on_map,
                                is_end=False,
                                score=seeker.score
                            )
                        )
                        self.seeker_normal_path = []
                        continue

                # ----------------------------------------
                # ----------------------------------------
                # check whether we are on the path to an announcement
                if len(self.seeker_path_for_announcement) > 0 and self.current_announcement:
                    goal_x, goal_y = self.seeker_path_for_announcement[-1]
                    moved = False # mark if we have moved 

                    if self.seen_map[goal_x][goal_x] == True: # goal is seen
                        # skip this path
                        self.seeker_path_for_announcement = []
                    else:
                        # keep going on this path
                        chosen_cell = self.__seeker_choose_cell_on_path_for_announcement()
                        if chosen_cell == None:
                            self.seeker_path_for_announcement = []
                        else:
                            R,C = self.seeker_path_for_announcement.pop(0)
                            self.move_seeker_to( coordinate=(R,C) )
                            seeker.score -= 1
                            # yield
                            all_states.append(
                                StateForFE(
                                    hiders=self.problem.hiders,
                                    seeker=seeker,
                                    announcements=self.announcements_on_map,
                                    is_end=False,
                                    score=seeker.score
                                )
                            )
                            self.seeker_normal_path = []
                            moved = not moved # mark as moved
                    
                    # check other cells of this announcement
                    if len(self.seeker_path_for_announcement) == 0:
                        path = self.__seeker_get_path_to_unseen_cell_of_announcement()
                        if path == None:
                            # no more cell
                            self.current_announcement = None
                        else:
                            self.seeker_path_for_announcement = path
                    
                    if moved:
                        continue
                    elif len(self.seeker_path_for_announcement) > 0:
                        R,C = self.seeker_path_for_announcement.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        all_states.append(
                            StateForFE(
                                hiders=self.problem.hiders,
                                seeker=seeker,
                                announcements=self.announcements_on_map,
                                is_end=False,
                                score=seeker.score
                            )
                        )
                        self.seeker_normal_path = []
                        continue

                # ----------------------------------------
                # ----------------------------------------
                # there are other visible announcements
                if len(self.visible_announcements) > 0:
                    shortest_path = None
                    nearest_ann = None
                    for ann in self.visible_announcements:
                        path = self.__seeker_shortest_path_to_announcement(ann)
                        if path == None:
                            self.visible_announcements.remove( ann )
                            continue
                        if shortest_path == None or len(path) < len(shortest_path):
                            shortest_path = path
                            nearest_ann = ann
                    if shortest_path != None:
                        self.current_announcement = nearest_ann
                        self.visible_announcements.remove(nearest_ann)

                        self.seeker_path_for_announcement = shortest_path
                        R,C = self.seeker_path_for_announcement.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        all_states.append(
                            StateForFE(
                                hiders=self.problem.hiders,
                                seeker=seeker,
                                announcements=self.announcements_on_map,
                                is_end=False,
                                score=seeker.score
                            )
                        )
                        self.seeker_normal_path = []
                        continue
                # ----------------------------------------
                # ----------------------------------------
                # blind step
                if len(self.seeker_normal_path) == 0:
                    self.seeker_normal_path = self.__seeker_blind_step()
                    if self.seeker_normal_path == None:
                        # FAILED
                        all_states.append(
                            StateForFE(
                                hiders=self.problem.hiders,
                                seeker=seeker,
                                announcements=self.announcements_on_map,
                                is_end=True,
                                score=seeker.score
                            )
                        )
                        return all_states
                R,C = self.seeker_normal_path.pop( 0 )
                self.move_seeker_to( coordinate=(R,C) )
                seeker.score -= 1
                # yield
                all_states.append(
                    StateForFE(
                        hiders=self.problem.hiders,
                        seeker=seeker,
                        announcements=self.announcements_on_map,
                        is_end=False,
                        score=seeker.score
                    )
                )

def main():
    lv2 = Level2('test/map1_7.txt')

    states = lv2.run()

    print('Score:',lv2.problem.seeker.score)
    if lv2.problem.hiders == []:
        print('Success')
    else:
        print('Failed')
    # print('vision map:')
    # lv2.problem.seeker.coordinate = (9,28)
    # lv2.problem.seeker.vision()
    # for state in list(reversed(states)):
    #     if state.seeker.signature == 'Seeker':
    #         for row in state.vision:
    #             for cell in row:
    #                 if cell == True:
    #                     print(1, end=' ')
    #                 elif cell == False:
    #                     print(0, end=' ')
    #                 elif cell == -1:
    #                     print('x', end=' ')
    #                 elif cell == 1000:
    #                     print('-', end=' ')     
    #             print()
    #         break

