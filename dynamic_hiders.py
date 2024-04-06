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

        skelaton_map = []
        for row in self.problem.map_list:
            tmp_row = []
            for cell in row:
                if cell[0] == -1:
                    tmp_row.append(-1)
                else:
                    tmp_row.append(1000)
            skelaton_map.append(tmp_row)
        self.problem.seeker.vision_map = deepcopy(skelaton_map)
        self.problem.seeker.heuristic_map = deepcopy(skelaton_map)
        self.problem.seeker.skelaton_map = skelaton_map


    def number_of_new_cells(self, new_seeker: Seeker) -> None:
        new_cells = 0
        for i in range(self.problem.num_row):
            for j in range(self.problem.num_col):
                if type(new_seeker.vision_map[i][j]) == bool and new_seeker.vision_map[i][j] == True:
                    if (i, j) not in self.seeker_seen_cells and new_seeker.skelaton_map[i][j] != -1:
                        new_cells += 1
        return new_cells

    # choose next cell to move in normal situation (without announcement)
    def move_without_announcement(self):
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
                elif seeker.skelaton_map[new_row][new_col] == -1:
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
                    if seeker.skelaton_map[i][j] != -1:
                        self.seeker_seen_cells.add((i, j))
        print(self.seeker_seen_cells)
        self.move_without_announcement()
        pass

    def hider_moves(self):
        pass
    def run(self) -> list:
        time_count = 0
        while time_count < 1:
            time_count += 1
            self.seeker_moves()



class Level4:
    pass

# for debugging
if __name__ == "__main__":
    lv3 = Level3(file_path="map1_1.txt")
    lv3.run()