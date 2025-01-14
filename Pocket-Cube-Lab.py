#This file should contain all of the tools that you use to solve the cube.
#You can add whatever methods you want.
#Be sure that there is a solve method implemented here.
from pocket_cube import *
import heapq
from collections import deque
def BFS(source,                                                  #source is the node where the search starts.
        condition = lambda cube: cube.state == list(range(24)),  #condition is a function that expects a node and returns a bool that is True if we've found what we're looking for.
        get_neighbors=lambda cube: cube.get_neighbors(),         #get_neighbors is a function that expects a node and returns the neigbors of that node.
        continue_condition=lambda visited: True):                #continue_condition is a function that expects a the dictionary, visited. If function returns False, the search terminates.
    #returns the last node found and a dictionary: The keys are the nodes found in the search, 
    #pass HERE
    queue = deque()
    queue.append((source, "_"))
    visited = {} #key node, value move to get to node
    while len(queue) > 0 and continue_condition(visited):
        node, move = queue.popleft()
        if node in visited:
            continue
        else:
            visited[node] = move
        if not condition(node):
            neighbors = set()
            for neighbor, move in get_neighbors(node):
                if neighbor not in visited:
                    neighbors.add((neighbor, move))
            queue.extend(neighbors)
        else:
            return node, visited
    return None, visited

def dijkstra(source,                                                  #source is the node where the search starts.
             condition = lambda cube: cube.state == list(range(24)),  #condition is a function that expects a node and returns a bool that is True if we've found what we're looking for.
             get_neighbors=lambda cube: cube.get_neighbors(),         #get_neighbors is a function that expects a node and returns the neigbors of that node.
             continue_condition=lambda visited: True):                #continue_condition is a function that expects a the dictionary, visited. If function returns False, the search terminates.
    #returns the last node found and a dictionary: The keys are the nodes found in the search, 
    #                                              The values are the last move to that key in a shortest path from source.
    #pass HERE
    queue = []
    heappush(queue, (0, source, "_"))
    visited = {}
    while len(queue)> 0 and continue_condition(visited):
        cost, node, move = heappop(queue)
        if node not in visited:
            visited[node] = move
            if condition(node):
                return node, visited
            for neighbor, move in get_neighbors(node):
    
                heappush(queue, (cost + pocket_cube.move_cost_dict[move], neighbor, move))
    return None, visited
def solve_cube_method1(cube):
    #IMPLEMENT THIS
    def similar_to_cube_in_solved_neighborhood(cube,solved_neighborhood):
        for nearly_solved_cube in solved_neighborhood:
            cubies = cube.get_adjacent_pair_of_correctly_placed_and_oriented_cubies(nearly_solved_cube)
            if cubies is None:
                continue
            else:
                cubie1, cubie2 = cubies
                nearby_solved, intermediate_neighborhood = dijkstra(cube,
                                                                    condition= lambda cube: cube==nearly_solved_cube, 

                                                                    get_neighbors=lambda cube: cube.get_neighbors_avoiding(cubie1) & cube.get_neighbors_avoiding(cubie2))

                if nearby_solved is None:
                    continue
                else: 
                    return nearby_solved, intermediate_neighborhood
        return False
    #STEP 1
    solved_cube = pocket_cube()
    _, solved_neighborhood = dijkstra(solved_cube, condition=lambda cube:False,
                                      continue_condition=lambda visited: len(visited) <=3*18**3)
    nearby_scrambled, scrambled_neighborhood = dijkstra(cube, condition=lambda cube:
                                                        similar_to_cube_in_solved_neighborhood(cube, solved_neighborhood))
    nearby_solved, intermediate_neighborhood = similar_to_cube_in_solved_neighborhood(nearby_scrambled, solved_neighborhood)

    move_seq1 = get_path_from_search(cube, nearby_scrambled, scrambled_neighborhood)
    move_seq2 = get_path_from_search(nearby_scrambled, nearby_solved, intermediate_neighborhood)
    move_seq3 = get_path_from_search(solved_cube, nearby_solved, solved_neighborhood)
    move_seq3 = pocket_cube.invert_move_sequence(move_seq3)
    return move_seq1+move_seq2+move_seq3
def improve_move_sequence(move_sequence):
    #pass
    #IMPLEMENT THIS
    reverse_sequence = pocket_cube.invert_move_sequence(move_sequence)
    P = pocket_cube()
    checks = []
    cost = 0
    move_sequence = []
    for i, mv in enumerate(reverse_sequence):
        if i%5==0:
            checks.append(pocket_cube(state=P.state))
        P.perform_move(mv, mutate=True)
        cost=cost+pocket_cube.move_cost_dict[mv]
    if P not in checks:
        checks.append(P)
    cube = pocket_cube()
    while cube != P:
        i = checks.i(cube)
        next_cube, visited = dijkstra(cube, condition=lambda cube: cube in checks[i+1:])
        move_sequence.extend(get_path_from_search(cube, next_cube, visited))
        cube = next_cube
    return pocket_cube.invert_move_sequence(move_sequence)
def get_path_from_search(source,target,visited):
    #expects two vertices, source and target, and a dictionary, visited.
    #We assume that the keys of visited are vertices and the value is move that takes you to that key.
    #Returns a sequence of moves from source to target. 
    path = []
    current = pocket_cube(state = target.state)
    while current != source:
        move = visited[current]
        if isinstance(move, tuple):
            move = list(move)
        else:
            move = [move]
        move = pocket_cube.invert_move_sequence(move)
        path.extend(move)
        current.perform_move_sequence(move)
    return pocket_cube.invert_move_sequence(path)

def solve_small_scramble(cube, method = "BFS"):
    if method == "BFS":
        _, visited = BFS(cube,condition=lambda cube: cube.state == list(range(24)))
    elif method == "dijkstra":
        _, visited = dijkstra(cube,condition=lambda cube: cube.state == list(range(24)))
    solve_seq = get_path_from_search(cube,pocket_cube(),visited)
    return solve_seq
def solve_cube(cube, method="method1"):
    #provides a single function that lets you choose the method of solution using the method flag.
    #Expects a scrambled cube, cube and a method to solve.
    #Returns a move sequence that unscrambles the cube. Does not mutate cube.
    if method == "method1":
        return solve_cube_method1(cube)
    elif method == "BFS":
        return solve_small_scramble(cube, "BFS")
    elif method == "dijkstra":
        return solve_small_scramble(cube, "dijkstra")
    else:
        raise "Invalid method"
