from problem import *
from player import *
from state import *

prob = Problem(
    input_filename='test/map1_1.txt',
    allow_move_obstacles=False
)
seeker = prob.seeker

seeker.vision()

# for row in seeker.skeleton_map:
#     for cell in row:
#         if cell == -1:
#             print('x', end=' ')
#         elif cell == 1000:
#             print('v', end=' ')
#         else:
#             print(0, end=' ')
#     print()

# for row in seeker.origin_map:
#     for cell in row:
#         if -1 in cell:
#             print(cell)
#             # print('x', end=' ')
#         # else:
#             # print('v', end=' ')
#     print()
for row in seeker.vision_map:
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