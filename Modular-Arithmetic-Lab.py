from sympy import isprime #This will be more efficient than checking with python.
import itertools
import functools
import random

def first_r_primes(r):
    #returns a list of the first n prime numbers.
    i=0
    primes = []
    while len(primes)<r:
        if isprime(i):
            primes.append(i)
        i+=1
    return primes

def extended_euclidean(a, b): #From ChatGPT
    # Returns GCD, x, y such that ax + by = GCD
    # Base case
    if b == 0:
        return a, 1, 0  # gcd(a, 0) = a, and the coefficients are (1, 0)

    # Recursive call
    gcd, x1, y1 = extended_euclidean(b, a % b)

    # Update x and y using the results from the recursion
    x = y1
    y = x1 - (a // b) * y1

    return gcd, x, y

class modular_int(object):
    #We are going to store integers as lists, [u_0,u_1,...,u_{r-1}]
    #This list represents the number x that satisfies $x=u_i %p_i, where p_i is the ith prime. u_i should be in [0,1,2,...,p_i-1].
    #Each instance of this class contains 
    # self.modular_rep . . . . . The list [u_0,...u_{r-1}]
    # self.r . . . . . . . . . . The number of primes used, also the length of self.modular_rep
    # self.primes_list . . . . . A list of the first r primes.
   
    @classmethod #See https://pynative.com/python-class-method/
    def create_modular_int_from_value(cls,value,r=10):
        #takes an integer value, returns a modular_int.
        #TODO: Get the list [u_0,u_1,...,u_{r-1}] based on value. Feed it and r into the constructor for modular_int.
        
        
        
        prime_numbers = first_r_primes(r) # gets a list of prime numbers to be used for calculating modular representation
        modular_rep = []
        for p in prime_numbers: # iterate through prime numbers
            modular_rep.append(value % p) # find the remainder when each value is divided by each prime number
        return modular_int(modular_rep, r)
        
        
        
        # pass
    @classmethod
    def modular_int_zero(cls,r): #The modular int zero
        return modular_int([0]*r, r)
    @classmethod
    def modular_int_one(cls,r): #The modular int one.
        return modular_int([1]*r, r)

    def __init__(self, modular_rep, r):
        #initializes from a list [u_0,u_1,...,u_{r-1}]
        self.r= len(modular_rep)
        self.modular_rep = modular_rep
        self.primes_list = first_r_primes(r)
    def __repr__(self) -> str:
        return str(self.modular_rep)
    def __eq__(self,other):
        if self.r != other.r:
            return False
        else:
            return all([self_ui==other_ui for self_ui,other_ui in zip(self.modular_rep,other.modular_rep)])
    def __add__(self,other):
        #implements addition.
        assert self.r==other.r #We assume the numbers have the same r.
        new_modular_rep = [(self_ui + other_ui)%p for self_ui, other_ui,p in zip(self.modular_rep, other.modular_rep,self.primes_list)]
        return modular_int(new_modular_rep, self.r)
    def __neg__(self):
        #negates the modular representation
        #TODO
        
        
        new_modular_rep = [(p - u_i) % p for u_i, p, p in zip(self.modular_rep, self.primes_list)]
        return modular_int(new_modular_rep, self.r)
        # see addition
        # https://www.w3schools.com/python/ref_func_zip.asp


        # pass
    def __sub__(self,other):
        return self + (-other)
    def __mul__(self,other):
        #implements multiplication.
        assert self.r==other.r
        #TODO: Implement multiplication. Similar to addition.
        
        
        assert self.r==other.r # assume same r
        new_modular_rep = [(self_ui * other_ui) % p for self_ui, other_ui, p in zip(self.modular_rep, other.modular_rep, self.primes_list)]
        # see addition
        return modular_int(new_modular_rep, self.r)
        # https://www.w3schools.com/python/ref_func_zip.asp
        
        # pass
    def __pow__(self,other):
        #Assume other is a natural number.
        #TODO implement exponents using multiplication and repeated squaring.
        #Don't refer to self.modular_rep or other.modular_rep in this function.
        #Hint: you can write the function recursively.
        
        
        
        if other == 0: # base case: if the exponent is 0, the value should be 1
            return modular_int.modular_int_one(self.r)
        if other == 1: # base case: if the exponent is 1, value remains unchanged
            return self
        # recursive call
        if other % 2 == 0: # if the exponent is even, find half the exponent and square that hald
            half_power = self ** (other // 2)
            return half_power * half_power
        else: # if the exponent is odd, find the power of the exponent - 1 (other - 1)
            return self * (self ** (other - 1))



        # pass

    def __int__(self):
        #Done. Following Knuth's notation on page 290 of TAOCP.
        c=[[0 for _ in range(self.r)] for _ in range(self.r)]#create a blank self.r x self.r matrix.
        v = [0]*self.r #creates a blank vector v
        u = self.modular_rep
        for i in range(self.r):
            for j in range(self.r):
                c[i][j]=extended_euclidean(self.primes_list[i],self.primes_list[j])[1]
        for k in range(self.r):
            current = u[k]
            for h in range(k):
                current = (current - v[h])%self.primes_list[k]
                current = (current * c[h][k])%self.primes_list[k]
            v[k]=current%self.primes_list[k]
        to_return = 0
        for k in range(self.r):
            to_return += v[k]*functools.reduce(lambda a,b: a*b,self.primes_list[:k],1)#https://www.geeksforgeeks.org/reduce-in-python/
        return to_return
    
def test_addition(r_vals,values):
    for r_val in r_vals:
        for a,b in itertools.combinations(values,2):
            assert a+b == int(modular_int.create_modular_int_from_value(a,r_val) + modular_int.create_modular_int_from_value(b,r_val)) 

def test_multiplication(r_vals,values):
    for r_val in r_vals:
        for a,b in itertools.combinations(values,2):
            assert a*b == int(modular_int.create_modular_int_from_value(a,r_val) * modular_int.create_modular_int_from_value(b,r_val)) 

def test_powers(r_vals,values):
    for r_val in r_vals:
        for a in values:
            for b in [0,1,2,3,5,7]:
                if r_val >2*b:#if r isn't big enough
                    assert a**b == int(modular_int.create_modular_int_from_value(a,r_val) ** b) 

def test_multiplication_self_test(r_vals,values):
    #Uses self-testing to check multiplication, assuming addition works.
    for r in r_vals:
        for a,b in itertools.combinations(values,2):
            a1 = random.randint(0,functools.reduce(lambda a,b:a*b, first_r_primes(r)))
            a2 = a - a1
            b1 = random.randint(0,functools.reduce(lambda a,b:a*b, first_r_primes(r)))
            b2 = b - b1
            a_mod,b_mod = modular_int.create_modular_int_from_value(a,r), modular_int.create_modular_int_from_value(b,r)
            a1_mod,a2_mod = modular_int.create_modular_int_from_value(a1,r), modular_int.create_modular_int_from_value(a2,r)
            b1_mod,b2_mod =  modular_int.create_modular_int_from_value(b1,r),modular_int.create_modular_int_from_value(b2,r)
            #TODO: What's the correct assertion to make here?
            assert (a1_mod + a2_mod)*(b1_mod+b2_mod) == a_mod * b_mod

if __name__ == '__main__':
    r_vals = [10, 15, 20, 40, 50]
    values = [1,2,3,6,7,10,15,100,123]  
    test_addition(r_vals,values)
    test_multiplication(r_vals,values)
    test_multiplication_self_test(r_vals,values)
    test_powers(r_vals,values)
    print("tests passed")
