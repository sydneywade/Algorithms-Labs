#The pocket cube is a 2x2x2 variant of the Rubik's cube.
#It is equivalent to just the corners of the Rubik's cube.
#This file contains the code for our pocket_cube class, which simulates the pocket cube.

#The pocket cube consists of 8 "cubies." Each cubie can be oriented in any of 3 ways.
#If we specify the orientation of 7 cubies, the last cubie's orientation is fixed.
#This means that there are 8!x3^7=88,179,840 configurations.
#You might see the claim that there are 3,674,160 configurations. This is because there are 24 orientations of the entire cube.
#But we are not accounting for these 24 orientations in this assignment.

#Further information can be found on Jaap's puzzle page: https://www.jaapsch.net/puzzles/cube2.htm

#The allowable moves consist of rotating a face of the cube clockwise 90, 180, or 270 degrees.
#We denote the faces Front (F), Back(B), Right(R), Left(L), Up(U), Down(D). The notation is standard from David Singmaster's original notes on the Rubik's cube.
#To denote a move, we name the face to turn, followed by a suffix.
#If the face is alone, it is a 90 degree turn clockwise.
#If the face is followed by "p" (for prime), we turn the face 270 degrees (or 90 degrees counterclockwise).
#If the face is followed by "2", we turn the face 180 degrees. 
#For example, "F" stands for rotating the front face clockwise.
#"F2" stands for rotating the front face counterclockwise.

#There are multiple ways to quantify the smallest solution to the solved cube from a given configuration.
#Quarter Turn Metric (QTM): Each 90 degree or 270 degree turn counts as 1 move. A 180 degree turn counts as 2 moves.
#Half Turn Metric (HTM): Each allowable move counts as 1 move
#General metrics: (ALT):  Assume we empirically determine how long it takes to perform each move. 
#                         Assume for simplicity that each move and its inverse take the same amount of time.
#                         Assume the amount of time each move takes is independent of the previous and subsequent moves.)
#It is claimed that every configuration can be solved in 11 moves using HTM and 14 moves using QTM.
#But we consider global orientation to be different, so for us it should take at most 15 moves using HTM and 22 using QTM.

#We will use Dijkstra's algorithm and Breadth First Search (BFS) to solve the pocket cube.
#The number of configurations is too large to solve this directly, so we will need a greedy heuristic or some other trick.

#To represent a state of the pocket cube, we will represent it by a list of length 24. We use the word "state" and "configuration" interchangably.
#The numbers in the list represent the faces of the cubies according to the following diagram, drawn by ChatGPT.
#
#           +----+----+
#           | 0  | 1  |
#           +----+----+
#           | 2  | 3  |
# +----+----+----+----+----+----+----+----+
# | 4  | 5  | 6  | 7  | 8  | 9  | 10 | 11 |
# +----+----+----+----+----+----+----+----+
# | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
#           +----+----+
#           | 20 | 21 |
#           +----+----+
#           | 22 | 23 |
#           +----+----+

#We also have a system for naming the cubies. For a given configuration, we name the 8 cubies of that configuration as
#cubie currently in the Back  Top  Left:   (0,0,0)
#                       Back  Top  Right:  (0,0,1)
#                       Back  Down Left:   (0,1,0)
#                       Back  Down Right:  (0,1,1)
#                       Front Top  Left:   (1,0,0)
#                       Front Top  Right:  (1,0,1)
#                       Front Down Left:   (1,1,0)
#                       Front Down Right:  (1,1,1)

import numpy as np
from heapq import heappush, heappop 
from collections import deque
import itertools

def determine_move_permutations():
    #Returns a dictionary whose keys are moves
    #The values are pairs, the permutations enacted by those moves.
    #This function will be called once and used in defining our pocket_cube class.
    moves =[direction+suffix for direction in ["F","B", "R","L", "U","D"] for suffix in ["","p","2"]]
    def rotate_F(state): #Rotate the front face clockwise.
        new_state = state[:]
        new_state[6] = state[14]
        new_state[7] = state[6]
        new_state[15] = state[7]
        new_state[14] = state[15]
        #---
        new_state[2] = state[13]
        new_state[3] = state[5]
        new_state[8] = state[2]
        new_state[16] = state[3]
        new_state[21] = state[8]
        new_state[20] = state[16]
        new_state[13] = state[21]
        new_state[5] = state[20]
        return new_state
    def rotate_R(state):
        new_state = state[:]
        new_state[8] = state[16]
        new_state[9] = state[8]
        new_state[17] = state[9]
        new_state[16] = state[17]
        #----
        new_state[3] = state[15]
        new_state[1] = state[7]
        new_state[10] = state[3]
        new_state[18] = state[1]
        new_state[23] = state[10]
        new_state[21] = state[18]
        new_state[15] = state[23]
        new_state[7] = state[21]
        return new_state
    def rotate_U(state):
        new_state = list(range(24))
        new_state[0] = state[2]
        new_state[1] = state[0]
        new_state[3] = state[1]
        new_state[2] = state[3]
        #---
        new_state[5] = state[7]
        new_state[4] = state[6]
        new_state[11] = state[5]
        new_state[10] = state[4]
        new_state[9] = state[11]
        new_state[8] = state[10]
        new_state[7] = state[9]
        new_state[6] = state[8]
        return new_state
    def rotate_L(state):
        new_state=state[:]
        new_state[4]= state[12]
        new_state[5]= state[4]
        new_state[13]=state[5]
        new_state[12]=state[13]
        #---
        new_state[0]= state[19]
        new_state[2]= state[11]
        new_state[6]= state[0]
        new_state[14]=state[2]
        new_state[20]=state[6]
        new_state[22]=state[14]
        new_state[19]=state[20]
        new_state[11]=state[22]
        return new_state
    def rotate_D(state):
        new_state=state[:]
        new_state[20] = state[22]
        new_state[21] = state[20]
        new_state[23] = state[21]
        new_state[22] = state[23]
        #---
        new_state[14] = state[12]
        new_state[15] = state[13]
        new_state[16] = state[14]
        new_state[17] = state[15]
        new_state[18] = state[16]
        new_state[19] = state[17]
        new_state[12] = state[18]
        new_state[13] = state[19]
        return new_state
    def rotate_B(state):
        new_state = state[:]
        new_state[10] = state[18]
        new_state[11] = state[10]
        new_state[19] = state[11]
        new_state[18] = state[19]
        #----
        new_state[17] = state[22]
        new_state[9] = state[23]
        new_state[1] = state[17]
        new_state[0] = state[9]
        new_state[4] = state[1]
        new_state[12] = state[0]
        new_state[22]= state[4]
        new_state[23] = state[12]
        return new_state
    to_return = {}
    for mv in moves:
        mv_permutation = list(range(24))
        if len(mv)==1:
            num_rotations = 1
        elif mv[1]=="2":
            num_rotations = 2
        else:
            num_rotations = 3
        for i in range(num_rotations):
            if mv[0]=="R":
                mv_permutation = rotate_R(mv_permutation)
            elif mv[0]=="L":
                mv_permutation = rotate_L(mv_permutation)
            elif mv[0]=="U":
                mv_permutation = rotate_U(mv_permutation)
            elif mv[0]=="D":
                mv_permutation = rotate_D(mv_permutation)
            elif mv[0]=="B":
                mv_permutation = rotate_B(mv_permutation)
            elif mv[0]=="F":
                mv_permutation = rotate_F(mv_permutation)
        to_return[mv] = mv_permutation
    return to_return

class pocket_cube(object):
    #move_permutation_dict is a dictionary from moves to permutations. The permutation is the permutation of the 24 cubie faces.
    move_permutation_dict = determine_move_permutations()#This function only gets called once, when the class is defined.

    #cubie_faces is a dictionary from cubies to the list of faces of that cubie. Each face is a number, 0-23
    cubie_faces={(0,0,0):[0,4,11],  #back  top  left
                 (0,0,1):[1,9,10],  #back  top  right
                 (0,1,0):[12,19,22],#back  down left
                 (0,1,1):[17,18,23],#back  down right
                 (1,0,0):[2,5,6],   #front top  left
                 (1,0,1):[3,7,8],   #front top  right
                 (1,1,0):[13,14,20],#front down left
                 (1,1,1):[15,16,21] #front down right
                 }

    #avoiding_moves is a dictionary from cubies to the list of moves that don't change that cubie.
    avoiding_moves= {(0,0,0):[mv for mv in move_permutation_dict if mv[0] in ("F","D","R")],
                     (0,0,1):[mv for mv in move_permutation_dict if mv[0] in("F","D","L")],
                     (0,1,0):[mv for mv in move_permutation_dict if mv[0] in("F","U","R")],
                     (0,1,1):[mv for mv in move_permutation_dict if mv[0] in("F","U","L")],
                     (1,0,0):[mv for mv in move_permutation_dict if mv[0] in("B","D","R")],
                     (1,0,1):[mv for mv in move_permutation_dict if mv[0] in("B","D","L")],
                     (1,1,0):[mv for mv in move_permutation_dict if mv[0] in("B","U","R")],
                     (1,1,1):[mv for mv in move_permutation_dict if mv[0] in("B","U","L")]}
    
    #cubie_faces_rotations is a dictionary from cubies to {-1,1}. -1 means that rotating the cubie counterclockwise is the same as moving its largest face onto its smallest face.
    #                                                              1 means that rotating the cubie        clockwise is the same as moving its largest face onto its smallest face.
    cubie_faces_rotations={(0,0,0):1,
                           (0,0,1):-1,
                           (0,1,0):-1,
                           (0,1,1):1,
                           (1,0,0):-1,
                           (1,0,1):-1,
                           (1,1,0):1,
                           (1,1,1):1}
    
    #The costs are encoded as the values of move_cost_dict. The keys are moves.
    #The costs are summarized by a string, the class variable, cost_type. 
    #To change the cost_move_dict, use the class method pocket_cube.change_cost_type("QTM")
    cost_type = "ALT"
    move_cost_dict = {m: 2 if len(m)==1 or m[1]=="p" else 3 for m in move_permutation_dict}

    def __init__(self, state=list(range(24))):
        #by default, the cube is initialized in the solved configuration.
        self.state = state
    def __repr__(self):
        #Prints the configuration of the pocket cube as an ASCII diagram.
        #ChatGPT was helpful with this, but its output needed some tweaking
        def pad(num): #expects num to be a 1 or 2 digit number.
                      #Returns a string of length 2 that represents that number.
            return f"{num:2}"
        
        foldout = f"""
          +----+----+
          | {pad(self.state[0])} | {pad(self.state[1])} |
          +----+----+
          | {pad(self.state[2])} | {pad(self.state[3])} |
+----+----+----+----+----+----+----+----+
| {pad(self.state[4])} | {pad(self.state[5])} | {pad(self.state[6])} | {pad(self.state[7])} | {pad(self.state[8])} | {pad(self.state[9])} | {pad(self.state[10])} | {pad(self.state[11])} |
+----+----+----+----+----+----+----+----+
| {pad(self.state[12])} | {pad(self.state[13])} | {pad(self.state[14])} | {pad(self.state[15])} | {pad(self.state[16])} | {pad(self.state[17])} | {pad(self.state[18])} | {pad(self.state[19])} |
+----+----+----+----+----+----+----+----+
          | {pad(self.state[20])} | {pad(self.state[21])} |
          +----+----+
          | {pad(self.state[22])} | {pad(self.state[23])} |
          +----+----+
        """
        return foldout
    def __eq__(self,other):
        return self.state==other.state
    def __hash__(self):
        #We need this to use pocket cubes as keys in a dictionary.
        #This appears to be the moste efficient way to hash a list.
        return hash(tuple(self.state))
    def __lt__(self,other):
        #We need to be able to compare pocket cubes to put them in a heap.
        #The comparison is arbitrary. This appears to be the fastest way to do it.
        return tuple(self.state)<tuple(other.state)
    def perform_move(self, move,mutate=False):
        #Expects move to be a string, like "Fp", "R2" or "L".
        #If mutate, mutates self by performing move and returns none. Otherwise, returns a new cube whose configuration is that of self, after performing move.
        new_state = [self.state[index] for index in pocket_cube.move_permutation_dict[move]]
        if mutate:
            self.state = new_state
        else:
            return pocket_cube(state = new_state)
    def perform_move_sequence(self,move_sequence,mutate=True):
        #Expects move_sequence to be a list of moves, like ["F","B2","Rp"]
        #Either returns None and mutates self (if mutate=True)
        #Or returns a new cube and does not affect self.
        if mutate:
            for move in move_sequence:
                self.perform_move(move,mutate=True)
        else:
            cube = pocket_cube(state = self.state)
            for move in move_sequence:
                cube.perform_move(move,mutate=True)
            return cube
        
    def identify_cubie(self,position):
        #takes a position (cubie in solved state) and returns the cubie currently in that position.
        faces = self.cubie_faces[position]
        faces = [self.state[faces[0]],self.state[faces[1]],self.state[faces[2]]]
        for index, cubie in enumerate(pocket_cube.cubie_faces):
            #print(pocket_cube.cubie_faces[cubie], faces)
            if set(pocket_cube.cubie_faces[cubie])==set(faces):
                return index
    def cubie_permutation(self):
        #Returns a list of length 8 that represents the permutation of the cubies, ignoring their orientations.
        return [self.identify_cubie(position) for position in itertools.product([0,1],repeat =3)]
    
    def get_twist_of_cubie(self,position):
        #Expects position to be a cubie position.
        #Returns 0, -1 or 1 depending on whether the cubie currently in posititon is oriented correctly, needs to be turned counter clockwise, or needs to be turned clockwise
        #in order for the largest face of that cubie to be in the position of the largest face of the cubie in that position when the cube is solved.
        #A basic invariant of the cube is that the sum of the twists is always 0.
        current_faces = [self.state[index] for index in self.cubie_faces[position]] #The faces that are currently on the cubie.
        largest_current_face = max(current_faces) #The largest face of the cubie currently in position.

        largest_solved_face = max(self.cubie_faces[position]) #The largest face of that cubie in the solved position.
        smallest_solved_face = min(self.cubie_faces[position])
        if largest_solved_face==self.state.index(largest_current_face):
            return 0
        elif smallest_solved_face ==self.state.index(largest_current_face):
            return -1*self.cubie_faces_rotations[position]
        else:
            return 1*self.cubie_faces_rotations[position]
    def cubie_twists(self):
        #returns a list of the twists of cubies in each position
        return [self.get_twist_of_cubie(position) for position in itertools.product([0,1], repeat =3)]
    def get_permutation_twist_rep(self):
        #Returns a pair. The 0th element is the cubie permutation. the 1st element is a list of twists of cubies.
        return self.cubie_permutation(), self.cubie_twists()
    def correctly_placed_cubies(self, other=None, orientation = False):
        #returns the number of cubies in the correct spot, relative to other. Ignores the orientation if orientation==False
        #By default, other=None, and we take this to mean that we are comparing to the solved cube.
        if other is None:
            other=pocket_cube()
        correctly_placed_cubies=[]
        if orientation==False:   
            for cubie in pocket_cube.cubie_faces:
                face1,face2,face3 = pocket_cube.cubie_faces[cubie]
                if {self.state[face1],self.state[face2],self.state[face3]}=={other.state[face1],other.state[face2],other.state[face3]}:
                    correctly_placed_cubies.append(cubie)
        else: #In this case, orientation==True and we check the order of the faces of the cubies by using lists.
            for cubie in pocket_cube.cubie_faces:
                face1,face2,face3 = pocket_cube.cubie_faces[cubie]
                if [self.state[face1],self.state[face2],self.state[face3]]==[other.state[face1],other.state[face2],other.state[face3]]:
                    correctly_placed_cubies.append(cubie)
        return correctly_placed_cubies
       
    def get_adjacent_pair_of_correctly_placed_and_oriented_cubies(self,other=None):
        #returns a pair of adjacent cubies that are in the correct spot with the correct orientation if they exist.
        #otherwise returns None.
        correctly_placed = self.correctly_placed_cubies(other=other,orientation=True)
        for c1, c2 in itertools.combinations(correctly_placed,2):
            if len([ "_" for x,y in zip(c1,c2) if x!=y])==1:
                return c1,c2
        return None
    @classmethod
    def move_sequence_cost(cls,move_sequence):
        #Expects move_sequence to be a list of moves.
        #Returns the sum of costs of the move sequence.
        return sum([cls.move_cost_dict[mv] for mv in move_sequence])
    @classmethod
    def invert_move_sequence(cls,move_sequence):
        #move_sequence is a list of moves. For example, ['R','L','Dp']
        #returns the move sequence that undoes move_sequence
        invert_sequence = []
        for mv in move_sequence[::-1]:#loop through move_sequence in reverse.
            if len(mv)==1:
                invert_sequence.append(mv+"p") #Replace a clockwise turn with the counterclockwise turn.
            elif mv[1]=='2':
                invert_sequence.append(mv) #A full turn is its own inverse.
            else:
                invert_sequence.append(mv[0]) #A clockwise turn inverts a counterclockwise turn.
        return invert_sequence
    
    @classmethod
    def change_cost_type(cls,new_cost_type):
        #Expects new_cost_type to be "HTM", "QTM", "ALT", or the new move_cost_dict
        #Updates the class variables pocket_cube.class_type and pocket_cube.move_cost_dict
        #Returns None
        if new_cost_type is dict:
            cls.cost_type = "ALT"
            if not new_cost_type.keys() == cls.move_cost_dict.keys():
                raise "cost dictionary invalid" #invalid keys
            elif any([ not isinstance(new_cost_type[key],(int, float) ) or new_cost_type[key]<0 for key in new_cost_type]):
                raise "wrong type of values to set costs"
        elif new_cost_type == "HTM":
            cls.cost_type = new_cost_type
            cls.move_cost_dict = {m: 1 if len(m)==1 or m[1]=="p" else 1 for m in cls.move_permutation_dict}
        elif new_cost_type == "QTM":
            cls.cost_type = "QTM"
            cls.move_cost_dict = {m: 1 if len(m)==1 or m[1]=="p" else 2 for m in cls.move_permutation_dict}
        elif new_cost_type == "ALT":
            cls.cost_type = "ALT"
            cls.move_cost_dict = {m: 2 if len(m)==1 or m[1]=="p" else 3 for m in cls.move_permutation_dict}

        else:
            raise "changed cost_type incorrectly."

    @classmethod
    def sequence_is_basic(cls,move_seq):
        #Returns true if the sequence cannot be obviously reduced. Used to construct the commutators.
        prev = move_seq[-1]
        for mv in move_seq:
            if prev[0]==mv[0]:
                return False
            prev = mv
        return True
    @classmethod
    def commutators(cls,length = 2):
        #Returns the iteratable of commutator moves, like ["R","L","Rp","Lp"] of length 2*length.
        #Commutators are known to be helpful in solving rubik's-type puzzles.
        def commutate(move_seq):
            return move_seq + cls.invert_move_sequence(move_seq)[::-1]
        return itertools.chain.from_iterable([[commutate(list(move_seq)) for move_seq in itertools.product(cls.move_permutation_dict.keys(), repeat = rep) if cls.sequence_is_basic(move_seq)] for rep in range(2,length+1)] )
        
    def scramble(self,length=15):
        #Scrambles the cube. Returns the list of moves used to scramble it.
        scramble_sequence = np.random.choice(list(pocket_cube.move_permutation_dict.keys()), size=length)
        self.perform_move_sequence(scramble_sequence)
        return scramble_sequence
    
    #Some neighborhood functions:
    def get_neighbors(self):
        #Returns the set of cubes that can be reached using a quarter turn or half turn.
        return {(self.perform_move(move,mutate=False), move) for move in pocket_cube.move_permutation_dict}
    def get_half_neighbors(self):
        #Returns the set of cubes that can be reached using a quarter turn.
        return {(self.perform_move(move,mutate=False), move) for move in pocket_cube.move_permutation_dict if move[-1] !="2"}
    def get_commutator_neighbors(self,length=2):
        #Returns the set of cubes that can be reached using a commutator.
        return {(self.perform_move_sequence(move_seq,mutate=False), tuple(move_seq)) for move_seq in pocket_cube.commutators(length=length)}
    def get_neighbors_avoiding(self, cubie):
    #expects cubie to be a tuple, like(0,0,0)
    #Returns the cubes that can be reached by moves that do not affect the cubie.
        return {(self.perform_move(move, mutate=False), move ) for move in pocket_cube.avoiding_moves[cubie]}