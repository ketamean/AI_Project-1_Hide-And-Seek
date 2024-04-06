import problem as cprob
from obstacle import *
from player import *
from copy import deepcopy
import state_for_fe as tfe
class Level3:

    def __init__(self, file_path: str)->None:

        self.problem = cprob.Problem(input_filename=file_path, allow_move_obstacles=False)
        self.problem.seeker.origin_map = self.problem.map_list
        self.seeker_seen_cells = set()
        self.path_save = [tuple]
        self.seeker_visited_cells: [tuple]
        self.announcement: []

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

    def is_valid_cell(self, row, col) -> bool:
        if row < 0 or row >= self.problem.num_row:
            return False
        if col < 0 or col >= self.problem.num_col:
            return False
        return True
    def number_of_new_cells(self, new_seeker: Seeker) -> None:
        new_cells = 0
        for i in range(max(0, new_seeker.coordinate[0] - 3), min(new_seeker.coordinate[0] + 3 + 1, self.problem.num_row)):
            for j in range(max(0, new_seeker.coordinate[1] - 3), min(new_seeker.coordinate[1] + 3 + 1, self.problem.num_col)):
                if type(new_seeker.vision_map[i][j]) == bool and new_seeker.vision_map[i][j] == True:
                    if (i, j) not in self.seeker_seen_cells and new_seeker.skeleton_map[i][j] != -1:
                        new_cells += 1
        return new_cells

    # choose next cell to move in normal situation (without announcement)
    def seeker_choose_cells(self):
        seeker = self.problem.seeker
        seeker_row, seeker_col = seeker.coordinate
        seeker.vision()

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
                print(new_seeker.coordinate, new_cells)


    def seeker_moves(self):
        seeker = self.problem.seeker
        seeker.vision()
        for i in range(self.problem.num_row):
            for j in range(self.problem.num_col):
                if type(seeker.vision_map[i][j]) == bool and seeker.vision_map[i][j] == True:
                    if seeker.skeleton_map[i][j] != -1:
                        self.seeker_seen_cells.add((i, j))

        self.seeker_choose_cells()
        pass

    def hider_see_moves(self, hider: Hider):
        seeker_location = None
        for i in range(max(0, hider.coordinate[0] - 2), min(hider.coordinate[0] + 2 + 1, self.problem.num_row)):
            for j in range(max(0, hider.coordinate[1] - 2), min(hider.coordinate[1] + 2 + 1, self.problem.num_col)):
                if type(hider.vision_map[i][j]) == bool and hider.vision_map[i][j]:
                    if type(self.problem.map_list[i][j][0]) == Seeker:
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

    def hider_moves(self):
        hiders = self.problem.hiders
        for hider in hiders:
            hider.vision()
            self.hider_see_moves(hider)
            print(hider.coordinate)
        pass
    def run(self) -> list:
        time_count = 0
        while time_count < 1:
            time_count += 1
            self.seeker_moves()
            self.hider_moves()




class Level4:
    pass

# for debugging
if __name__ == "__main__":
    lv3 = Level3(file_path="map1_1.txt")
    lv3.run()