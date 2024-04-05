from pq import PriorityQueue

class Node:
    def __init__(self, coordinate: tuple, g, h , parent=None):
        # parent == None is the root node
        self.coordinate = coordinate
        self.g = g
        self.h = h
        self.cost = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

def get_path_from_parent(node: Node):
    """
        get list of coordinate from start to goal, excluding the start node
    """
    if node.parent == None:
        return [  ]
    l = get_path_from_parent(node.parent)
    l.append( node.coordinate )
    return l

def heuristic(start_coor: tuple, goal_coor: tuple):
    return abs(start_coor[0] - goal[0]) + abs(start_coor[1] - goal[1])

def astar(grid, start_coor: tuple, goal_coor: tuple):
    """
        get list of coordinate from start to goal, excluding the start node

        if there is no path, returns None
    """
    node = Node(
        coordinate=start_coor,
        g=0,
        h=heuristic( start_coor, goal_coor ),
    )
    frontier = PriorityQueue( (heuristic( start_coor=start_coor, goal_coor=goal_coor ), node) )
    reached = {
        start_coor: node
    }
    ADJACENT = [
        (-1,-1), (-1,0), (-1,1),
        (0,-1),          (0,1),
        (1,-1),  (1,0),  (1,1)
    ]
    expanded = {
        # state: True
    }
    while not frontier.is_empty():
        prior, node = frontier.pop()

        # mark state as expanded
        expanded[node.coordinate] = True

        if node.coordinate == goal_coor:
            return get_path_from_parent(node)
        
        # -----------------------------------------------------
        # NOTE: expanding node
        children = []
        cur_r, cur_c = node.coordinate
        for dr, dc in ADJACENT:
            new_r = cur_r + dr
            new_c = cur_c + dc
            if (
                new_r < 0 or new_r >= len(grid) or new_c < 0 or new_c >= len(grid[0]) or    # invalid index
                expanded.get( (new_r, new_c) ) != None or                                   # already be expanded
                grid[new_r][new_c] == False                                                 # cell cannot get through
            ):
                continue
            children.append(
                Node(
                    coordinate=(new_r, new_c),
                    g=node.g + 1,
                    h=heuristic( (new_r, new_c), goal_coor ),
                    parent=node
                )
            )
        # -----------------------------------------------------

        for child in children:
            r,c = child.coordinate
            if reached.get( (r,c) ) == None or child.cost < reached[ (r,c) ].cost:
                reached[ (r,c) ] = child
                frontier.push( (child.cost, child) )
    
    return None  # No path found

# Example usage:
grid = [
    [0, 0, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

start = (0, 0)
goal = (3, 3)

path = astar(grid, start, goal)
if path:
    print("Path found:", path)
else:
    print("No path found")
