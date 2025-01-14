#This file contains the starter code for the greedy algorithm for the employment problem using the transversal matroid structure.
#Given a set W of workers and a set J of jobs and a bipartite graph on W+J whose edges represent that a worker is qualified for the job,
#and a value function val:J->R
#Find a set of jobs that maximizes this value, such that each job can be paired with a worker.

import random
from collections import deque

def match(edges,v):
    #Expects v to be a vertex.
    #Edges are a list of edges in a matching.
    #Returns the other vertex in the edge containing v.
    edges_incident_v = [e for e in edges if v==e[0] or v==e[1]]
    if len(edges_incident_v)==0:
        return None
    e = edges_incident_v[0]
    if v== e[0]:
        return e[1]
    elif v== e[1]:
        return e[0]
    
def BFS(source,                                                 
    condition, 
    get_neighbors        
    ):
    
    visited = {}
    queue = deque()
    queue.append((source, None))
    while len(queue) > 0:
        current, previous = queue.popleft()
        if current in visited:
            continue
        else: 
            visited[current] = previous
        if condition(current): # check if current node satisfies condition
            return current, visited
        else:
            neighbors = {(neighbor, current) for neighbor in get_neighbors(current) if neighbor not in visited}
            queue.extend(neighbors)
    return None, visited
def augment(a,B,W,J,G):
    #Assume that a is a job and B is sets of edges (w,j) that is a matching.
    #G is an adjacency list representation of a graph.
    #Returns a matching containing B. It contains a, if possible.
    
    use_match_edge = False
    current = a
    
    def end_vertex_condition(vertex):
        #returns True if vertex is in W and doesn't have a match in B.
        #TODO: write this
        #pass
        if vertex in W and match(B, vertex) is None:
            return True
        else:
            return False
         
    # check if the vertex is in W and does not have a matched edge in B
    def get_neighbors(vertex):
        #Alternate between using edges of G and edges of B to define neighbors.
        #use_match_edge determines which.
        #Toggle use_match_edge as a side effect.
        #Return the list of neighbors of vertex.
        nonlocal use_match_edge #It may help you to use this nonlocal variable to keep track of whether to use a match edge or a non-match edge. Not the only way to do it.
        #TODO: finish this function.
        #pass
        if use_match_edge: # use edges in B
            use_match_edge = False
            if match(B, vertex) is None:
                return []
            else:
                return [match(B, vertex)]
            #neighbors = [edge[0] for edge in B if edge[1] == vertex]
        else: # use edges in G
            use_match_edge = True
            neighbors = G[vertex]
            return neighbors
        
    e, visited = BFS(a,end_vertex_condition, get_neighbors) #Calls BFS using the functions you wrote.

    if e is None: #We don't find an end to the augmenting path starting at a.
        return B #the matching is unchanged.
    else:

        #TODO: backtrack to find the alternating path, switch the edges to get a new matching containing a and B.
        #pass
        path = []
        current = e

        while current != a:
            if current in W:
                 path.append((current, visited[current]))
            current = visited[current]
        jobs_rematch = []
        for w, j, in path:
            jobs_rematch.append(j)
        
       
        return [edge for edge in B if edge[1] not in jobs_rematch] + path

def get_maximal_matched_jobs(W,J,G,value = lambda j: int(j[1:])):
    #Expects G to be a bipartite graph with parts W,J
    #Expects value to be a function from J to non-negative real numbers.
    #By default, the value is the number of the job.
    #Returns a pair. The first coordinate is the set of jobs that achieves the maximal value. The second is the set of edges that achieves the pairing.
    #edges must be ordered pairs, (w,j). The job must be the second coordinate.
    sorted_J = sorted(J,key=value)
    jobs_match = []
    for j in sorted_J[::-1]: #loop through the jobs in reverse of their order.
        jobs_match = augment(j,jobs_match,W,J,G) #add j to the jobs of jobs_match, if possible.
    return [j for w,j in jobs_match], jobs_match
