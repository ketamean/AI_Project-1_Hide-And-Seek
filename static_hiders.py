from problem import *
from obstacle import *
from player import *
from pq import *
from state_for_fe import StateForFE
import astar
class Level1:
    pass

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

        self.reachable[next_r][next_c] = True

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
                # remove it from list of hiders in Problem
                # remove it from the Problem.map_list
                # remove its coordinate from visible_hider_coor list
                # remove all of its announcements from list of visible announcements and announcements_on_map
                self.total_hiders -= 1
                seeker.score += 20
                print('found', (cur_r, cur_c))
                if (cur_r, cur_c) in self.visibile_hider_coor:
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
                for ann in self.announcements_on_map:
                    if ann.hider.id == element.id:
                        self.announcements_on_map.remove( ann )
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
                # check index validity
                if idcol < 0:
                    continue
                if idcol >= len(visionmap[0]):
                    break

                if visionmap[idrow][idcol] == True: # cell is visible
                    # mark cell as seen
                    self.seen_map[idrow][idcol] = True
                    if -1 in self.problem.map_list[idrow][idcol]:
                        self.reachable[idrow][idcol] = False
                    else:
                        # as it is visible and it is not a wall, it is reachable
                        self.reachable[idrow][idcol] = True
                for component in self.problem.map_list[idrow][idcol]:
                    if not isinstance(component, int):
                        # not -1 or 1000 => it is an object
                        if component.signature == 'Hider' and visionmap[idrow][idcol] == True:
                            # is a VISIBLE hider
                            if component.coordinate not in self.visibile_hider_coor:
                                self.visibile_hider_coor.append( (component.coordinate[0], component.coordinate[1]) )
                                path = astar.astar(
                                    grid=self.astar_map,
                                    start_coor=(cur_r, cur_c),
                                    goal_coor=component.coordinate
                                )
                                if path == None:
                                    self.reachable[component.coordinate[0]][component.coordinate[1]] = False
                                elif len(self.seeker_path_to_hider) == 0 or len(path) < len(self.seeker_path_to_hider):
                                    self.visibile_hider_coor.pop()
                                    if len(self.seeker_path_to_hider):
                                        self.visibile_hider_coor.append( self.seeker_path_to_hider[-1] )
                                    self.seeker_path_to_hider = path

                            # for hider in self.problem.hiders:
                            #     if hider.coordinate == component.coordinate and component.coordinate not in self.visibile_hider_coor:
                            #         self.visibile_hider_coor.append( (component.coordinate[0], component.coordinate[1]) )
                            #         break
                        elif component.signature == 'Announcement':
                            existed = False
                            for ann in self.visible_announcements:
                                if component.coordinate == ann['coordinate']:
                                    existed = not existed # TRUE
                                    break
                            if not existed:
                                new_ann = {
                                    'coordinate': (component.coordinate[0], component.coordinate[1]),
                                    'hider_id': component.hider.id
                                }
                                self.visible_announcements.append( new_ann )
                                path = astar.astar(
                                    grid=self.astar_map,
                                    start_coor=(cur_r, cur_c),
                                    goal_coor=component.coordinate
                                )
                                if path == None:
                                    self.reachable[component.coordinate[0]][component.coordinate[1]] = False
                                elif len(self.seeker_path_for_announcement) == 0 or len(path) < len(self.seeker_path_for_announcement):
                                    self.visible_announcements.pop()
                                    if self.current_announcement:
                                        self.visible_announcements.append( self.current_announcement )
                                    self.seeker_path_for_announcement = path
                                    self.current_announcement = new_ann

    
    def __seeker_choose_cell_on_path_to_hider(self):
        """
            assuming that seeker is on the way to a hider

            return coordinate of the cell to go next and POP IT OUT OF THE PATH TO HIDER
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
            nexthider_coor = self.visibile_hider_coor.pop()
            res = astar.astar(
                grid=self.astar_map,
                start_coor=(cur_r, cur_c),
                goal_coor=nexthider_coor
            )
            if res and len(res):
                return res
        return None
    
    def __seeker_choose_cell_on_path_for_announcement(self):
        """
            return coordinate of a cell on path for announcement
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
                # if idrow == cur_r and idcol == cur_c:
                #     continue
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
                        self.reachable[idrow][idcol] = True
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
                        self.reachable[idrow][idcol] = True
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
                    # print('\t',path)
                    return path
                # print('no path')
                
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
                        # print('\t',path)
                        return path
                    # print('no path')
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

                    # yield
                    StateForFE(
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
                self.reachable[cur_r][cur_c] = True
                # check if seeker is in the same tile with a hider
                self.__seeker_check_found_hider()
                # ----------------------------------------
                # ----------------------------------------
                # check if all hiders are found
                if self.total_hiders == 0:
                    # end game, success
                    return StateForFE._all_states, True
                
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
                    print('reached all give up')
                    return StateForFE._all_states, False
                
                # ----------------------------------------
                # ----------------------------------------
                # check appearance of new hiders and announcements around seeker
                self.__seeker_check_new_hider_and_announcement()
                # ----------------------------------------
                # ----------------------------------------
                # check whether we are on the way to a hider
                if len(self.seeker_path_to_hider):
                    # print('\tchoose cell to hider')
                    R,C = self.__seeker_choose_cell_on_path_to_hider()
                    self.seeker_path_to_hider.pop(0)
                    # if len(self.seeker_path_to_hider) == 0:
                    #     self.visibile_hider_coor.pop()
                    self.move_seeker_to( coordinate=(R,C) )
                    seeker.score -= 1
                    # yield
                    StateForFE(
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
                    # print('\tcreate path to hider')
                    res = self.__seeker_create_new_path_to_hider()
                    if res:
                        self.seeker_path_to_hider = res
                        R,C = self.seeker_path_to_hider.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        # yield
                        StateForFE(
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
                    print('\tchoose cell to announcement')
                    x,y = self.seeker_path_for_announcement[-1]
                    moved = False
                    if self.seen_map[x][y] == False:
                        # the target cell is unseen
                        res = self.__seeker_choose_cell_on_path_for_announcement()
                        if res == None:
                            self.seeker_path_for_announcement = []
                        else:
                            self.seeker_path_for_announcement.pop(0)
                            R,C = res
                            self.move_seeker_to( coordinate=(R,C) )
                            seeker.score -= 1
                            # yield
                            StateForFE(
                                player=seeker,
                                old_row=self.last_step[0],
                                old_col=self.last_step[1],
                                new_row=R,
                                new_col=C,
                                announcements=self.announcements_on_map
                            )
                            self.seeker_normal_path = []
                            moved = not moved # TRUE
                    else:
                        self.seeker_path_for_announcement = []
                    if len(self.seeker_path_for_announcement) == 0:
                        res = self.__seeker_check_unseen_cell_around_announcement()
                        if res:
                            self.seeker_path_for_announcement = res
                    if moved:
                        continue
                    else:
                        if len(self.seeker_path_for_announcement):
                            R,C = self.seeker_path_for_announcement.pop(0)
                            self.move_seeker_to( coordinate=(R,C) )
                            seeker.score -= 1
                            # yield
                            StateForFE(
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
                # there are other visible announcements
                if len(self.visible_announcements):
                    print('\tcreate path for announcement')
                    while len(self.visible_announcements):
                        self.current_announcement = self.visible_announcements.pop()
                        goal = self.__seeker_find_goal_for_path_announcement()
                        if goal:
                            if goal == (cur_r, cur_c):
                                goal = None
                            else:
                                break
                    if goal:
                        R,C = self.seeker_path_for_announcement.pop(0)
                        self.move_seeker_to( coordinate=(R,C) )
                        seeker.score -= 1
                        # yield
                        StateForFE(
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
                    # print('\tcreate normal path')
                    self.seeker_normal_path = self.__seeker_blind_step()
                    if self.seeker_normal_path == None:
                        print('no normal path give up')
                        return StateForFE._all_states, False
                R,C = self.seeker_normal_path.pop( 0 )
                self.move_seeker_to( coordinate=(R,C) )
                seeker.score -= 1
                # yield
                StateForFE(
                    player=seeker,
                    old_row=self.last_step[0],
                    old_col=self.last_step[1],
                    new_row=R,
                    new_col=C,
                    announcements=self.announcements_on_map
                )
def main():
    lv2 = Level2('test/map1_7.txt')

    states, flag = lv2.run()

    for state in states[-10::]:
        if state.player.signature == 'Hider':
            # print('Hider\'s turn.')
            pass
        elif state.player.signature == 'Seeker':
            # print('Seeker\'s turn:', end=' ')
            print(state.old_coordinate, '-->', state.new_coordinate)
            pass
    
    if flag:
        print('Success')
    else:
        print('Failed')
    print('Score:',lv2.problem.seeker.score)

    # print('vision map:')
    # lv2.problem.seeker.coordinate = (9,28)
    # lv2.problem.seeker.vision()
    for state in list(reversed(states)):
        if state.player.signature == 'Seeker':
            for row in state.vision:
                for cell in row:
                    if cell == True:
                        print(1, end=' ')
                    elif cell == False:
                        print(0, end=' ')
                    elif cell == -1:
                        print('x', end=' ')
                    elif cell == 1000:
                        print('-', end=' ')     
                print()
            break

main()