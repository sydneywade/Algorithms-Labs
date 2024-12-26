def fastscan(f, id_, a):
    '''Input: f ....a binary, associative function.
              id_ ....The left identity of the function
              a ......A list, all of the same type.
              f must be a function of type l x r -> l where l is the type of id_, r is the type of elements of a.
        Returns:
            A list of reductions by f to the prefixes of a. When f is +, this amounts to partial sums of a.       
    '''
    # base cases
    if len(a) == 0:
        return [id_]
    elif len(a) == 1:
        return [id_, a[0]]
    else:
        # compute the "partial solution" by
        # applying f to each adjacent pair of numbers 
        # e.g., [2, 1, 3, 2, 2, 5, 4, 1] -> [3, 5, 7, 5]
        # this can be done in parallel

        partial_solution = [f(a[2*i], a[2*i+1]) for i in range(len(a)//2)]
        
        if len(a) % 2 == 1:
            partial_solution.append(a[-1])
        #TODO: Your code here. Replace 0 with the appropriate thing. Be sure that your code works when len(a) is even and when len(a) is odd.

        # recursively apply fastscan to the partial solution
        partial_output = fastscan(f, id_, partial_solution)
        #HERE
        
        # combine partial_output with input to get desired output
        ret = (
            [partial_output[i//2] if i%2==0 else   # use partial output
             f(partial_output[i//2], a[i-1])       # combine partial output with next value
             for i in range(len(a)+1)]
        )
        return ret

#print(fastscan(lambda x,y:x+y, 0, [1,8,9,10,5]))

def compose(f1,f2):
    #Assumes that f1 and f2 are dictionaries that represent functions.
    #If count_compositions is true, we increment a global counter.
    #Returns a dictionary whose keys are those of f1 that represents the composition of the functions.
    return {key: f2.get(f1[key], None) for key in f1 if f1[key] in f2}
    #HERE
    #pass

class state_machine(object):
    #We represent the states by the integers 0..k-1. The initial state is 0.
    #We represent the transition function of a letter using a dictionary whose keys and values are integers 0..k-1
    #The state machine is a dictionary whose keys are letters and values are dictionaries (transition functions of those letters.)
    def __init__(self, transitions, accept_states):
        #Assume that transitions is a dictionary of dictionaries of the form above.
        #Assume accept_states is a list of integers 0..k-1.
        self.transitions = transitions
        self.alphabet = list(transitions.keys())
        self.accept_states = accept_states
        self.num_alphabet = len(transitions)
        self.num_states = len(transitions[self.alphabet[0]])
    def identity_transform(self):
        #returns the dictionary that represents the identity function
        return {state:state for state in range(self.num_states)}
    def iterative_match(self,string):
        #Assume string is a string over the alphabet of the machine.
        #Returns True/False, depending on the resulting state.
        current_state = 0
        for s in string:
            current_state = self.transitions[s][current_state]
        return current_state in self.accept_states
    def scan_match(self,string):
        #Should have identical behavior to iterative_match.
        #TODO
        return self.iterative_match(string)
        #HERE
        #pass
    def __repr__(self):
        return str(self.transitions)
    @classmethod
    def example_state_machine(cls):
        #Returns the state machine on alphabet 0,1 that accepts an even number of 1's.

        transitions ={"0": 
                        {0:0, 1:1},
                      "1":
                        {0:1, 1:0}}
        accept_states = [0]
        return state_machine(transitions,accept_states)
    
    @classmethod
    def standardize_state_names(cls, transitions, initial_state, accept_states):
        #Expects transitions to be a dictionary from letters to states. 
        #        transitions is not assumed to be complete: 
        #           not every state appears as a key. But every state appears as a key for some transition, except possibly a garbage state.
        #We assume that the states are strings.
        #Initial state is the initial state. Accept states is a list of accept states.
        #Returns the state machine that standardizes the strings to integers, where 0 is the initial state.

        add_garbage_state = False #Whether or not to add an additional state to represent garbage.
        total_states = []
        for letter in transitions:
            current_transition = transitions[letter]
            total_states.extend([k for k in current_transition if k not in total_states])
        for letter in transitions:
            current_transition = transitions[letter]
            if len(current_transition.keys())<len(total_states):
                add_garbage_state = True
                break
        #Swap the initial state with total_states[0]
        index_of_initial_state = total_states.index(initial_state)
        total_states[0], total_states[index_of_initial_state] = initial_state, total_states[0] 

        standard_transitions = {letter: { total_states.index(k):total_states.index(transitions[letter][k]) for k in transitions[letter]} for letter in transitions}
        if add_garbage_state:
            #TODO: Add transitions to garbage states when no state exists.
            #HERE
            garbage_index = len(total_states)
            #total_states.append("garbage")
            for letter in transitions:
                new_dict = {}
                for state in range(len(total_states)+1):
                    new_dict[state] = standard_transitions[letter].get(state, len(total_states))
                    '''
                    if state not in standard_transitions[letter]:
                        standard_transitions[letter][state] = garbage_index
                        garbage_needed = True
        '''
                standard_transitions[letter] = new_dict
        standard_accept_states = [total_states.index(a) for a in accept_states]
        return state_machine(standard_transitions,standard_accept_states)
    
def transitions_of_weakly_increasing_decimals():
    #Returns a dictionary whose keys are the letters '.' and [0-9]. The values are dictionaries that describe the state transition of the corresponding letter.
    #We use the 31-state machine in the homework solutions.
    accept_states = [str(i)+ modifier for i in range(1,10) for modifier in ['l','r']] + ['0l']
    dot_transition = {str(i)+'l':str(i)+'dot' for i in range(10)}
    transitions = {
        str(i): {str(j) + 'l': str(i) + 'l' for j in range(1,10) if i >= j} #Transitions from jl to il
                |{str(j) + 'dot': str(i) + 'r' for j in range(10) if i>=j} #Transitions from jdot to ir
                #TODO: Transitions from jr to ir.
                #HERE
                |{str(j) + 'r': str(i) + 'r' for j in range(10) if i >= j} # TRANSITIONS FROM JR TO IR
                |{'initial_state': str(i)+ 'l'} for i in range(10) #Transitions from initial state.
    }
    transitions['.']=dot_transition
    return transitions,'initial_state', accept_states
if __name__=='__main__':
    transitions,initial_state,accept_states = transitions_of_weakly_increasing_decimals()
    sm=state_machine.standardize_state_names(transitions,initial_state,accept_states)
    print(sm)
