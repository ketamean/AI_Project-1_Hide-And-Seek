import random

import problem as cprob
from obstacle import *
from player import *
from copy import deepcopy
import state_for_fe as sff
from astar import astar
class Level3:

    def __init__(self, file_path: str)->None:

        self.problem = cprob.Problem(input_filename=file_path, allow_move_obstacles=False)
        self.problem.seeker.origin_map = self.problem.map_list
        self.seeker_seen_cells = set()
        self.path_save = []
        self.seeker_visited_cells = set()
        self.announcement = []
        self.path_to_cell = None
        self.score = 0
        self.is_concede = False
        skeleton_map = []
        for row in self.problem.map_list:
            tmp_row = []
            for cell in row:
                if cell[0] == -1:
                    tmp_row.append(-1)
                else:
                    tmp_row.append(1000)
            skeleton_map.append(tmp_row)
        self.problem.seeker.vision_map = deepcopy(skeleton_map)
        self.problem.seeker.heuristic_map = deepcopy(skeleton_map)
        self.problem.seeker.skeleton_map = skeleton_map
        self.grid_for_astar = []
        for row in self.problem.map_list:
            tmp_row = []
            for cell in row:
                if cell[0] == -1:
                    tmp_row.append(False)
                else:
                    tmp_row.append(True)
            self.grid_for_astar.append(tmp_row)
        self.seeker_visited_cells.add(self.problem.seeker.coordinate)

    @staticmethod
    def manhattan_distance(cell_1: tuple, cell_2:tuple) -> int:
        return abs(cell_1[0] - cell_2[0]) + abs(cell_1[1] - cell_2[1])
    def is_valid_cell(self, row, col) -> bool:
        if row < 0 or row >= self.problem.num_row:
            return False
        if col < 0 or col >= self.problem.num_col:
            return False
        return True
    def number_of_new_cells(self, new_seeker: Seeker) -> int:
        new_cells = 0
        for i in range(max(0, new_seeker.coordinate[0] - 3), min(new_seeker.coordinate[0] + 3 + 1, self.problem.num_row)):
            for j in range(max(0, new_seeker.coordinate[1] - 3), min(new_seeker.coordinate[1] + 3 + 1, self.problem.num_col)):
                if type(new_seeker.vision_map[i][j]) == bool and new_seeker.vision_map[i][j] == True:
                    if (i, j) not in self.seeker_seen_cells and new_seeker.skeleton_map[i][j] != -1:
                        new_cells += 1
        return new_cells

    def seeker_finds_hider(self) -> None | tuple:
        seeker = self.problem.seeker
        for i in range(max(0, seeker.coordinate[0] - 3), min(seeker.coordinate[0] + 3 + 1, self.problem.num_row)):
            for j in range(max(0, seeker.coordinate[1] - 3), min(seeker.coordinate[1] + 3 + 1, self.problem.num_col)):
                if type(seeker.vision_map[i][j]) == bool and seeker.vision_map[i][j] == True:
                    for item in self.problem.map_list[i][j]:
                        if type(item) == Hider:
                            return i, j
        return None

    def seeker_finds_announcements(self) -> None|tuple:
        seeker = self.problem.seeker
        for i, j in self.announcement:
            if type(seeker.vision_map[i][j]) == bool and seeker.vision_map[i][j] == True:
                return i,j
        return None

    # choose next cell to move in normal situation (without announcement)

    def seeker_choose_cells(self)->tuple|list:
        seeker = self.problem.seeker
        seeker_row, seeker_col = seeker.coordinate
        seeker.vision()

        if self.seeker_finds_announcements() is not None:
            return self.seeker_finds_announcements()

        # find nearby 8 cells
        nearby_cells = []
        for row_delta in range(-1, 2):
            for col_delta in range(-1, 2):
                new_row = seeker_row + row_delta
                new_col = seeker_col + col_delta
                if row_delta == 0 and col_delta == 0:
                    continue
                elif new_row < 0 or new_row >= self.problem.num_row:
                    continue
                elif new_col < 0 or new_col >= self.problem.num_col:
                    continue
                elif len(self.path_save) != 0 and {new_row, new_col} == self.path_save[-1]:
                    continue
                elif seeker.skeleton_map[new_row][new_col] == -1:
                    continue
                new_seeker = deepcopy(seeker)
                new_seeker.coordinate = (new_row, new_col)
                new_seeker.vision()
                new_cells = self.number_of_new_cells(new_seeker)
                nearby_cells.append((new_seeker.coordinate, new_cells))
        return nearby_cells

    def seeker_catch(self):
        seeker = self.problem.seeker
        catch_list = []
        for hider in self.problem.hiders:
            if hider.coordinate == seeker.coordinate:
                catch_list.append(hider)
        for hider in catch_list:
            self.problem.map_list[hider.coordinate[0]][hider.coordinate[1]].remove(hider)
            self.problem.hiders.remove(hider)
            self.score += 20

    def seeker_moves(self):
        self.seeker_catch()
        seeker = self.problem.seeker
        seeker.vision()
        seeker_row, seeker_col = seeker.coordinate
        is_go_back = False
        if self.path_to_cell != None and len(self.path_to_cell) == 0:
            self.path_to_cell = None
        for i in range(self.problem.num_row):
            for j in range(self.problem.num_col):
                if type(seeker.vision_map[i][j]) == bool and seeker.vision_map[i][j] == True:
                    if seeker.skeleton_map[i][j] != -1 and (i, j) not in self.seeker_seen_cells:
                        self.seeker_seen_cells.add((i, j))

        if self.seeker_finds_hider() is not None:
            new_row, new_col = None, None
            hider_loc = self.seeker_finds_hider()
            min_manhattan_dis = 100
            for row_delta in range(-1, 2):
                for col_delta in range(-1, 2):
                    temp_row = seeker_row + row_delta
                    temp_col = seeker_col + col_delta
                    if self.is_valid_cell(temp_row, temp_col) and seeker.skeleton_map[temp_row][temp_col] != -1:
                        if abs(temp_row - hider_loc[0]) + abs(temp_col - hider_loc[1]) < min_manhattan_dis:
                            min_manhattan_dis = abs(temp_row - hider_loc[0]) + abs(temp_col - hider_loc[1])
                            new_row = temp_row
                            new_col = temp_col
            self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
            seeker.coordinate = (new_row, new_col)
            seeker.vision()
            self.problem.map_list[new_row][new_col].append(seeker)

        # Nếu đang tìm hiểu xung quanh 1 announcement thì tìm tiếp, không thì tìm thông tin từ 1 announcement mới.
        elif self.path_to_cell != None:

            new_cell = self.path_to_cell.pop(0)
            self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
            seeker.coordinate = new_cell
            seeker.vision()
            self.problem.map_list[new_cell[0]][new_cell[1]].append(seeker)
            if len(self.path_to_cell) == 0:
                self.path_to_cell = None
        elif self.seeker_finds_announcements() is not None:
            announcement = self.seeker_finds_announcements()
            for i in range(max(0, announcement[0] - 3), min(announcement[0] + 3 + 1, self.problem.num_row)):
                for j in range(max(0, announcement[1] - 3), min(announcement[1] + 3 + 1, self.problem.num_col)):
                    if (i, j) not in self.seeker_seen_cells:
                        path = astar(goal_coor=(i, j),grid=self.grid_for_astar, start_coor=seeker.coordinate)
                        if path is not None and len(path) != 0:
                            self.path_to_cell = path
                            new_cell = self.path_to_cell.pop(0)
                            self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
                            seeker.coordinate = new_cell
                            seeker.vision()
                            self.problem.map_list[new_cell[0]][new_cell[1]].append(seeker)
                            break
                if self.path_to_cell != None:
                    break
            if self.path_to_cell == None:
                for i in range(max(0, announcement[0] - 3), min(announcement[0] + 3 + 1, self.problem.num_row)):
                    for j in range(max(0, announcement[1] - 3), min(announcement[1] + 3 + 1, self.problem.num_col)):
                        path = astar(goal_coor=(i, j), grid=self.grid_for_astar, start_coor=seeker.coordinate)
                        if path is not None and len(path) != 0:
                            self.path_to_cell = path
                            new_cell = self.path_to_cell.pop(0)
                            self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
                            seeker.coordinate = new_cell
                            seeker.vision()
                            self.problem.map_list[new_cell[0]][new_cell[1]].append(seeker)
                            break
                    if self.path_to_cell != None:
                        break
        else:
            cells_chosen = self.seeker_choose_cells()
            mx_new_seen, count_mx = -1, 0
            for cell in cells_chosen:
                if mx_new_seen < cell[1]:
                    mx_new_seen = cell[1]
                    count_mx = 1
                elif mx_new_seen == cell[1]:
                    count_mx += 1

            if mx_new_seen != 0:
                new_cell = None
                for _cell in cells_chosen:
                    if _cell[1] == mx_new_seen:
                        new_cell = _cell[0]
                        break
                self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
                seeker.coordinate = new_cell
                seeker.vision()
                self.problem.map_list[new_cell[0]][new_cell[1]].append(seeker)
            elif mx_new_seen == 0:
                if len(self.path_save) == 0:
                    for i in range(self.problem.num_row):
                        for j in range(self.problem.num_col):
                            if (i, j) not in self.seeker_seen_cells and (i, j) != seeker.coordinate:
                                path = astar(goal_coor=(i, j), grid=self.grid_for_astar, start_coor=seeker.coordinate)
                                if path is not None:
                                    self.path_to_cell = path
                                    break
                        if self.path_to_cell != None:
                            break

                    if (self.path_to_cell == None):
                        self.is_concede = True
                    return
                else:
                    is_go_back = True
                    new_cell = self.path_save.pop()
                    self.problem.map_list[seeker.coordinate[0]][seeker.coordinate[1]].remove(seeker)
                    seeker.coordinate = new_cell
                    seeker.vision()
                    self.problem.map_list[new_cell[0]][new_cell[1]].append(seeker)
        self.seeker_visited_cells.add(seeker.coordinate)
        if not is_go_back:
            self.path_save.append(seeker.coordinate)

    def hider_see_moves(self, hider: Hider):
        seeker_location = None
        for i in range(max(0, hider.coordinate[0] - 2), min(hider.coordinate[0] + 2 + 1, self.problem.num_row)):
            for j in range(max(0, hider.coordinate[1] - 2), min(hider.coordinate[1] + 2 + 1, self.problem.num_col)):
                if type(hider.vision_map[i][j]) == bool and hider.vision_map[i][j]:
                    for item in self.problem.map_list[i][j]:
                        if type(item) == Seeker:
                            seeker_location = (i, j)
        if seeker_location == None:
            return
        old_hider_location = hider.coordinate
        delta_row = 0
        delta_col = 0
        if hider.coordinate[0] < seeker_location[0]:
            delta_row = -1
        elif hider.coordinate[0] > seeker_location[0]:
            delta_row = 1
        if hider.coordinate[1] < seeker_location[1]:
            delta_col = -1
        elif hider.coordinate[1] > seeker_location[1]:
            delta_col = 1
        if delta_col == delta_row and delta_col == 0:
            return
        new_row = hider.coordinate[0] + delta_row
        new_col = hider.coordinate[1] + delta_col
        if self.is_valid_cell(new_row, new_col) and hider.skeleton_map[new_row][new_col] != -1:
            self.problem.map_list[old_hider_location[0]][old_hider_location[1]].remove(hider)
            hider.coordinate = (new_row, new_col)
            hider.vision()
            self.problem.map_list[new_row][new_col].append(hider)
        pass

    def hiders_move(self):
        hiders = self.problem.hiders
        for hider in hiders:
            hider.vision()
            self.hider_see_moves(hider)
        pass

    def hider_random_announcement(self, hider) -> tuple:
        delta_row = random.randint(0, 6) - 3
        delta_col = random.randint(0, 6) - 3
        while not self.is_valid_cell(hider.coordinate[0] + delta_row, hider.coordinate[1] + delta_col):
            delta_row = random.randint(0, 6) - 3
            delta_col = random.randint(0, 6) - 3
        return delta_row + hider.coordinate[0], delta_col + hider.coordinate[1]
    def hiders_announce(self):
        hiders = self.problem.hiders
        is_announce_in_path = False
        for ann in self.announcement:
            if self.path_to_cell != None and self.path_to_cell[-1] == ann:
                is_announce_in_path = True
                break
        if is_announce_in_path:
            self.path_to_cell = None
        self.announcement.clear()
        for hider in hiders:
            self.announcement.append(self.hider_random_announcement(hider))
    def run(self) -> list:
        time_count = 0
        all_states = []
        while time_count < 1e5:
            if len(self.problem.hiders) == 0:
                self.is_concede = True
            time_count += 1
            if time_count % 5 == 0:
                self.hiders_announce()
            self.seeker_moves()
            self.hiders_move()
            self.score -= 1
            curren_state = sff.StateForFE(seeker=self.problem.seeker, hiders=self.problem.hiders, score=self.score, announcements=self.announcement, is_end=False)
            if self.is_concede:
                curren_state.is_end = True
            all_states.append(curren_state)
            if self.is_concede:
                break
        return all_states


class Level4:
    pass


# for debugging
if __name__ == "__main__":
    lv3 = Level3(file_path="test/map1_1.txt")
    lv3.run()