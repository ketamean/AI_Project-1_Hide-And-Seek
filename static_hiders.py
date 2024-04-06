from problem import *
from obstacle import *
from player import *
from pq import *
from astar import *
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

        skelaton_map = []
        for row in self.problem.map_list:
            row_skelation = []
            for cell in row:
                if cell == -1:
                    row_skelation.append(-1)
                else:
                    row_skelation.append(1000)
            skelaton_map.append( row_skelation )

        from copy import deepcopy
        seeker.vision_map = deepcopy(skelaton_map)
        seeker.heuristic_map = deepcopy(skelaton_map)
        seeker.skelaton_map = deepcopy(skelaton_map)

    ADJACENT = [
        (-1,-1),    (-1,0),     (-1,1),
        (0,-1),                 (0,1),
        (1,-1),     (1,0),      (1,1)
    ]
    def __backtrack_find_path(self, cur_coor: tuple, to_coor: tuple, cur_path: list, map: list):
        if cur_coor == to_coor:
            return cur_path
        r, c = cur_coor
        map[r][c] = False
        for pair in Level2.ADJACENT:
            next_r = r + pair[0]
            next_c = c + pair[1]
            if (next_r < 0 or next_r >= len(self.problem.map_list) or
                next_c < 0 or next_c >= len(self.problem.map_list[0]) or
                -1 in self.problem.map_list[next_r][next_c] or
                map[next_r][next_c] == False
                ):
                continue
            cur_path.append((next_r, next_c))
            res = self.__backtrack_find_path(
                cur_coor=(next_r, next_c),
                to_coor=to_coor,
                cur_path=cur_path,
                map=map
            )
            cur_path.pop()
            if res:
                return res
        # Return None or an empty list if no path is found
        return None
    
    def __move_towards_target(self, target_coor: tuple):
        """
        Move the seeker towards the target cell until it reaches the target.

        Returns a list of steps (as coordinates) taken by the seeker.
        """
        tmp_seeker = Seeker(
            coordinate= self.problem.seeker.coordinate
        )
        tmp_seeker.origin_map = self.problem.seeker.origin_map
        tmp_seeker.skelaton_map = self.problem.seeker.skelaton_map
        seeker_path = []

        while tmp_seeker.coordinate != target_coor:
            cur_r, cur_c = tmp_seeker.coordinate
            target_r, target_c = target_coor

            # Determine the direction to move towards the target cell
            move_direction = (
                1 if target_r > cur_r else -1 if target_r < cur_r else 0,
                1 if target_c > cur_c else -1 if target_c < cur_c else 0
            )

            # Attempt to move in the chosen direction
            next_r = cur_r + move_direction[0]
            next_c = cur_c + move_direction[1]

            # If the chosen direction is blocked, try alternative directions
            if (next_r < 0 or next_r >= len(self.problem.map_list) or
                next_c < 0 or next_c >= len(self.problem.map_list[0]) or
                -1 in self.problem.map_list[next_r][next_c]):
                # Check alternative directions
                for dr, dc in Level1.ADJACENT:
                    next_r = cur_r + dr
                    next_c = cur_c + dc
                    # Check if the alternative direction is valid
                    if (next_r >= 0 and next_r < len(self.problem.map_list) and
                        next_c >= 0 and next_c < len(self.problem.map_list[0]) and
                        -1 not in self.problem.map_list[next_r][next_c]):
                        # Move in the alternative direction
                        seeker_path.append((next_r, next_c))
                        tmp_seeker.coordinate = (next_r, next_c)
                        break  # Exit the loop after finding a valid direction

            else:
                # Move in the initially chosen direction
                seeker_path.append((next_r, next_c))
                tmp_seeker.coordinate = (next_r, next_c)

        return seeker_path

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
                    tmp_seeker.skelaton_map = seeker.skelaton_map
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
                        if idcol == idc and idrow == idr:
                            continue
                        # check index validity
                        if idcol < 0:
                            continue
                        if idcol >= len(self.cur_vision_maps):
                            break
                        if v_map[idrow][idcol] == True and self.seen_map[idrow][idcol] == False:
                            cnt += 1
                if cnt > max_count_val:
                    max_count_val = cnt
                    max_coordinate = [ (idr, idc) ]
                elif cnt == max_count_val:
                    max_coordinate.append( (idr, idc) )

            print('max:', max_count_val)
            print('n cell:', len(max_coordinate))
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
                            for col in range(cur_c - radius, cur_c + radius + 1):
                                if row < 0 or row >= len(seeker.origin_map) or col < 0 or col >= len(seeker.origin_map[0]):
                                    continue
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

                            for cell_data in cells:
                                res = self.__move_towards_target(cell_data['coordinate'])
                                if res:
                                    return [(res[0])]
                            else:
                                # No path found to any reachable unseen cell
                                return False

                        radius += 1
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

    def run(self):
        from copy import deepcopy, copy
        seeker = self.problem.seeker
        hider_coor = []
        announcement_coor = []
        self.moves_stack = [ copy(seeker.coordinate) ]                   # stack of steps of seeker

        self.vision_maps = {                    # map a coordinate with the corresponding vision map for later reuse
            
        }

        self.seen_map = [                       # list of cells which seeker has already seen
            [True if cell == -1 else False for cell in row ] for row in seeker.skelaton_map
        ]                                       # True / False
        self.visited_map = deepcopy(self.seen_map)  # list of cells which seeker has already visited
                                                # True / False

        while True:
            r,c = seeker.coordinate
            self.cur_vision_maps = self.vision_maps.get( (r,c) )
            if self.cur_vision_maps == None:
                seeker.vision()
                self.cur_vision_maps = deepcopy(seeker.vision_map)
                self.vision_maps[ (r,c) ] = self.cur_vision_maps

            # check for existence of Hider or Announcement in the vision
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
                    if c + idcol >= len(self.cur_vision_maps):
                        break
                    if self.cur_vision_maps[idrow][idcol] == True:
                        for element in self.problem.map_list[idrow][idcol]:
                            if not isinstance(element, int):
                                # not -1 or 1000 => is object
                                if element.signature == 'Hider':
                                    hider_coor.append( (idrow, idcol) )
                                elif element.signature == 'Announcement':
                                    announcement_coor.append( (idrow, idcol) )
                            # else, pass

            if len(hider_coor) or len(announcement_coor):
                if len(hider_coor):
                    # there is a hider, go to this
                    pass
            
                if len(announcement_coor):
                    # there is an announcement, go around this
                    pass
            else:
                # no hider, no announcement
                res = self.__choose_step_no_info()
                for i in res:
                    print(i)
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
                        tmp_seeker.skelaton_map = seeker.skelaton_map
                        tmp_seeker.vision()
                        visionmap = deepcopy(tmp_seeker.vision_map)
                        self.vision_maps[ (idr, idc) ] = visionmap

                    # -----------------------------------------------------------------
                    # print debug
                    for row in visionmap:
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
                    
                    yield StateForFE(
                        player=seeker,
                        old_row=self.moves_stack[-1][0],
                        old_col=self.moves_stack[-1][1],
                        new_row=R,
                        new_col=C,
                        # announcements=[]
                    )

                    # for row in self.problem.map_list:
                    #     for cell in row:
                    #         if cell 
                    #         # if cell == True:
                    #         #     print(1, end=' ')
                    #         # else:
                    #         #     print(0, end=' ')
                    #     print()

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

                    self.moves_stack.append( (R,C) )         

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
        seeker = self.problem.seeker
        seeker.origin_map = self.problem.map_list
        
        skelaton_map = []
        for row in self.problem.map_list:
            tmp_row = []
            for cell in row:
                if cell == -1:
                    tmp_row.append(-1)
                else:
                    tmp_row.append(1000)
            skelaton_map.append( tmp_row )
        
        from copy import deepcopy
        seeker.vision_map = deepcopy(skelaton_map)
        seeker.heuristic_map = deepcopy(skelaton_map)
        seeker.skelaton_map = skelaton_map
    
    @staticmethod
    def setup_heuristic_map(seeker: Seeker):
        """
            set up heuristic map of the seeker (seeker.heuristic_map)

            returns nothing
        """
        from copy import deepcopy
        seeker.heuristic_map = deepcopy(seeker.skelaton_map)
        seeker.vision()
        pos_r, pos_c = seeker.coordinate
        mark_hider = []         # mark all hiders in the vision
        mark_announcement = []  # mark all announcements in the vision

        # traverse seeker.vision_map
        for idrow in range(-seeker.radius, seeker.radius + 1, +1):
            # idrow in [-radius, radius + 1)
            if idrow < 0:
                continue
            if idrow >= len(seeker.vision_map):
                break
            for idcol in range(-seeker.radius, seeker.radius + 1, +1):
                # idcol in [-radius, radius + 1)
                if idcol < 0:
                    continue
                if idcol >= len(seeker.vision_map[0]):
                    break
                if seeker.vision_map[idrow][idcol] == True:
                    cell = seeker.origin_map[idrow][idcol]
                    if -1 in cell:
                        # is wall
                        if len(cell) > 1:
                            # exists announcement(s) on this wall
                            seeker.heuristic_map[idrow][idcol] = 0
                        else:
                            seeker.heuristic_map[idrow][idcol] = 1000
                    elif 1000 in cell:
                        # empty cell
                        if cell != [1000]:
                            # invalid map!
                            raise ValueError("An empty cell cannot contain any objects")
                        seeker.heuristic_map[idrow][idcol] = 1000
                    else:
                        # list has only Hider - Seeker - Announcement object
                        for component in cell:
                            # have not done
                            pass
                # else, heuristic value of the corresponding cell remains unchanged

    # def run(self):
    #     from copy import deepcopy
    #     nhiders = len(self.problem.hiders)
    #     seeker = self.problem.seeker
    #     reached = {
    #         seeker.coordinate: Node(
    #             id_row=seeker.coordinate[0],
    #             id_col=seeker.coordinate[1],
    #             cumulative_pathcost=0,
    #             parent=None
    #         )
    #     }
        
    #     # frontier = PriorityQueue( () )

    #     # while len(frontier) > 0:
    #     #     pass

    #     STEP = 5
    #     cumulative_vision_map = {
    #         # (r, c): map
    #     }

    #     seen_map = [[False for j in range( len( self.seen_map[0] ) ) ] for i in range( len( self.seen_map ) )]

    #     r,c = seeker.coordinate
    #     arr = [(r-1, c-1), (r-1, c), (r-1, c+1), (r,c-1), (r,c+1), (r+1, c-1), (r+1, c), (r+1, c+1)]
    #     for _ in range(STEP):
    #         arr = [(r-1, c-1), (r-1, c), (r-1, c+1), (r,c-1), (r,c+1), (r+1, c-1), (r+1, c), (r+1, c+1)]
    #         for _r, _c in arr:
    #             if _r < 0 or _c < 0 or _r >= len(seeker.origin_map) or _c >= len(seeker.origin_map[0]):
    #                 continue
    #             v_map = cumulative_vision_map.get( (_r,_c) )
    #             if v_map == None:
    #                 # .........................
    #                 cumulative_vision_map[ (_r, _c) ] = v_map
    #             cnt = 0
    #             for i in range(-seeker.radius, seeker.radius + 1, +1):
    #                 if _r + i < 0 or _r + i >= len(seeker.vision_map):
    #                     continue
    #                 for j in range(-seeker.radius, seeker.radius + 1, +1):
    #                     if _c + j < 0 or _c + j >= len(seeker.vision_map[0]):
    #                         continue
    #                     if seen_map[_r + i][_c + j] == False and v_map[_r + i][_c + j] == True:
    #                         # have not seen yet but now we do
    #                         cnt += 1
    ADJACENT = [
        (-1,-1),    (-1,0),     (-1,1),
        (0,-1),                 (0,1),
        (1,-1),     (1,0),      (1,1)
    ]
    def __backtrack_find_path(self, cur_coor: tuple, to_coor: tuple, cur_path: list, map: list):
        if cur_coor == to_coor:
            return cur_path
        r,c = cur_coor
        map[r][c] = False
        for pair in Level2.ADJACENT:
            next_r = r + pair[0]
            next_c = c + pair[1]
            if (next_r < 0 or next_r >= len(self.problem.map_list) or
                next_c < 0 or next_c >= len(self.problem.map_list[0]) or
                -1 in self.problem.map_list[next_r][next_c] or
                map[next_r][next_c] == False
                ):
                continue
            cur_path.append( (next_r, next_c) )
            res = self.__backtrack_find_path(
                cur_coor=(next_r, next_c),
                to_coor=to_coor,
                cur_path=cur_path,
                map=map
            )
            cur_path.pop()
            if res:
                return res

        map[r][c] = True
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
        if len(self.steps_stack) == 0:
            # the first step => has no previous step
            pass
        else:
            # avoid steping back to the previous step
            last_r, last_c = self.steps_stack[-1]   # the previous coordinate of the agent
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
                    tmp_seeker.skelaton_map = seeker.skelaton_map
                    tmp_seeker.vision()
                    v_map = deepcopy(tmp_seeker.vision_map)
                    self.vision_maps[ (idr, idc) ] = v_map
                cnt = 0

                # traverse vision map of the potentially next step
                for idrow in range(idr-seeker.radius, idr+seeker.radius + 1, +1):
                    # check index validity
                    if idrow < 0:
                        continue
                    if idrow >= len(self.current_vision_map):
                        break
                    for idcol in range(idc-seeker.radius, idc+seeker.radius + 1, +1):
                        if idcol == idc and idrow == idr:
                            continue
                        # check index validity
                        if idcol < 0:
                            continue
                        if idcol >= len(self.current_vision_map):
                            break
                        if v_map[idrow][idcol] == True and self.seen_map[idrow][idcol] == False:
                            cnt += 1
                if cnt > max_count_val:
                    max_count_val = cnt
                    max_coordinate = [ (idr, idc) ]
                elif cnt == max_count_val:
                    max_coordinate.append( (idr, idc) )

            print('max:', max_count_val)
            print('n cell:', len(max_coordinate))
            if len(max_coordinate) == 0:
                # is blocked, cannot move to any adjacent cells
                return False
            elif len(max_coordinate) > 1:
                # many cells share a common heuristic value
                if max_count_val == 0:
                    # h = 0: no new vision
                    radius = seeker.radius + 1
                    stop_flag = True        # to check whether we expanded the whole map
                    while stop_flag:
                        stop_flag = False
                        cells = []
                        if cur_r - radius >= 0:
                            stop_flag = True
                            row = cur_r - radius
                            for col in range(cur_c - seeker.radius, cur_c + seeker.radius + 1, +1):
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
                                    # (row, col)
      
                        if cur_r + radius < len(seeker.origin_map):
                            stop_flag = True
                            row = cur_r + radius
                            for col in range(cur_c - seeker.radius, cur_c + seeker.radius + 1, +1):
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
                            stop_flag = True
                            col = cur_c - radius
                            for row in range(cur_r - seeker.radius, cur_r + seeker.radius + 1, +1):
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
                            stop_flag = True
                            col = cur_c + radius
                            for row in range(cur_r - seeker.radius, cur_r + seeker.radius + 1, +1):
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
                        if len(cells):
                            _tmp_map = [ # a map which is False if tile is a wall; otherwise, False
                                [False if cell == -1 else True for cell in row] for row in seeker.skelaton_map
                            ]
                        if len(cells) == 1:
                            # there is only 1 cell at the lowest level that we have no vision
                            res = self.__backtrack_find_path(
                                cur_coor=(cur_r, cur_c),
                                to_coor=cells[0].get('coordinate'),
                                cur_path=[],
                                map=_tmp_map
                            )
                            if res:
                                return res
                            else:
                                return False
                        elif len(cells) > 1:
                            # there are multiple cells at this level of BFS

                            min_distance = [ cells[0] ]     # list of cells that has minimum manhattan distance
                            for el in cells[1:]:
                                if el['distance'] < min_distance[0]['distance']:
                                    min_distance = [ el ]
                                elif el['distance'] == min_distance[0]['distance']:
                                    min_distance.append( el )
                            res = self.__backtrack_find_path(
                                cur_coor=(cur_r, cur_c),
                                to_coor=min_distance[0].get('coordinate'),
                                cur_path=[],
                                map=_tmp_map
                            )
                            if res:
                                return res
                            else:
                                return False 
                        radius += 1
                    
                    # if it reach here, there is no cell to see
                    return False
                    # end while
                else:
                    # h != 0: choose the cell whose Manhattan distance from the previous cell is the largest
                    max_distance = -1
                    max_distance_coor = None
                    for i,j in max_coordinate:
                        # i - row, j - col
                        tmp_dis = abs(last_r - i) + abs(last_c - j)
                        if tmp_dis > max_distance:
                            max_distance_coor = (i,j)
                    return [max_distance_coor]
            else:
                return [(max_coordinate[0])]

    def __choose_step_w_hider(self):
        pass

    def __choose_step_w_announcement(self):
        pass

    def run(self):
        from copy import deepcopy, copy
        seeker = self.problem.seeker
        hider_coor = []
        announcement_coor = []
        self.steps_stack = [ copy(seeker.coordinate) ]                   # stack of steps of seeker

        self.vision_maps = {                    # map a coordinate with the corresponding vision map for later reuse
            
        }

        self.seen_map = [                       # list of cells which seeker has already seen
            [True if cell == -1 else False for cell in row ] for row in seeker.skelaton_map
        ]                                       # True / False
        self.visited_map = deepcopy(self.seen_map)  # list of cells which seeker has already visited
                                                # True / False

        while True:
            r,c = seeker.coordinate
            self.current_vision_map = self.vision_maps.get( (r,c) )
            if self.current_vision_map == None:
                seeker.vision()
                self.current_vision_map = deepcopy(seeker.vision_map)
                self.vision_maps[ (r,c) ] = self.current_vision_map

            # check for existence of Hider or Announcement in the vision
            for idrow in range(-seeker.radius, seeker.radius + 1, +1):
                # check index validity
                if r + idrow < 0:
                    continue
                if r + idrow >= len(self.current_vision_map):
                    break
                for idcol in range(-seeker.radius, seeker.radius + 1, +1):
                    if idcol == 0 and idrow == 0:
                        continue
                    # check index validity
                    if c + idcol < 0:
                        continue
                    if c + idcol >= len(self.current_vision_map):
                        break
                    if self.current_vision_map[idrow][idcol] == True:
                        for element in self.problem.map_list[idrow][idcol]:
                            if not isinstance(element, int):
                                # not -1 or 1000 => is object
                                if element.signature == 'Hider':
                                    hider_coor.append( (idrow, idcol) )
                                elif element.signature == 'Announcement':
                                    announcement_coor.append( (idrow, idcol) )
                            # else, pass

            if len(hider_coor) or len(announcement_coor):
                if len(hider_coor):
                    # there is a hider, go to this
                    pass
            
                if len(announcement_coor):
                    # there is an announcement, go around this
                    pass
            else:
                # no hider, no announcement
                res = self.__choose_step_no_info()
                if res == False:
                    # give up
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
                        tmp_seeker.skelaton_map = seeker.skelaton_map
                        tmp_seeker.vision()
                        visionmap = deepcopy(tmp_seeker.vision_map)
                        self.vision_maps[ (idr, idc) ] = visionmap

                    # -----------------------------------------------------------------
                    # print debug
                    for row in visionmap:
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
                    else:
                        self.problem.map_list[R][C].append( seeker )
                    
                    yield StateForFE(
                        player=seeker,
                        old_row=self.steps_stack[-1][0],
                        old_col=self.steps_stack[-1][1],
                        new_row=R,
                        new_col=C,
                        # announcements=[]
                    )
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
                    self.steps_stack.append( (R,C) )
                
if __name__ == '__main__':
    lv1 = Level1('test/map1_1.txt')
    for state in lv1.run():
        print(state.old_coordinate, '-->', state.new_coordinate)

# if __name__ == '__main__':
#     lv2 = Level2('test/map1_1.txt')
#     for state in lv2.run():
#         print(state.old_coordinate, '-->', state.new_coordinate)