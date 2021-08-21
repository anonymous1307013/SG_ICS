import io
import sys

from z3 import*


f_read = open('Input_ICS.txt', 'r')

slv = Solver()

# Number of states and measurements
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 2):
        num_states = int(words[0])
        num_msrs = int(words[1])
        #print num_states, num_msrs
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

# Jacobian matrix (the relation between the states and the measurements)
State_msr_relation = [[Bool('state_msr_%s_%s' % (i, j)) for j in range(0, num_msrs + 1)] for i in range(0, num_states + 1)]
#print State_msr_relation

for j in range(1, num_msrs + 1):     
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) == num_states):
            for i in range(1, len(words) + 1):
                if (words[i - 1] == "0"):
                    #slv.add(state_msr_relation[(i - 1) * num_states + j - 1] == False)                    
                    slv.add(State_msr_relation[i][j] == False)                    
                else:
                    #slv.add(state_msr_relation[(i - 1) * num_states + j - 1] == True) 
                    slv.add(State_msr_relation[i][j] == True) 
                                       
                #print words[i - 1]
        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break

# Topology
# Number of IEDs (1-8) and RTUs (9-12) (1 MTU (13) is assumed)
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()    

    if (len(words) == 2):
        num_ieds = int(words[0])
        num_rtus = int(words[1])
        #print num_ieds, num_rtus
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

# Measurements corresponding to IEDs
Ied_msr_relation = [[Bool('ied_msr_%s_%s' % (i, j)) for j in range(0, num_msrs + 1)] for i in range(0, num_ieds + 1)]
#print Ied_msr_relation

for i in range(1, num_ieds + 1):     
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) > 0):    # At least a single measurement is transmitted by this ied
            for j in range(1, num_msrs + 1): 
                if (str(j) in words[1 : len(words)]):
                    slv.add(Ied_msr_relation[i][j] == True)                    
                    #print j
                else:                    
                    slv.add(Ied_msr_relation[i][j] == False)                                                        
        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break

# Reachability (among the IEDs, the RTUs, and the MTU)
num_nodes = num_ieds + num_rtus + 1 # 1 is for the MTU
Reachability = [[Bool('reachability_%s_%s' % (i, j)) for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]
#print Reachability

reachability = [[0 for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]

while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()    

    if (len(words) == 1):                       
        # Assuming that the reachabilities are given for the time being
        m = int(words[0])
        for k in range(m):
            while True:
                line = f_read.readline()
                if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
                    continue

                words = line.split()
                        
                if (len(words) == 2):    # At least a single measurement is transmitted by this ied
                    i = int(words[0])
                    j = int(words[1])      
                    reachability[i][j] = 1;                                                      
                else:
                    print ('Unmatched Input: Exit')
                    sys.exit()

                break
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

for i in range(1, num_nodes + 1):
    for j in range(1, num_nodes + 1):
        if (reachability[i][j] == 1):
            slv.add(Reachability[i][j] == True)
        else:
            slv.add(Reachability[i][j] == False)                    

# Security profile between the communicating entities
# Security profile can be desing using 8 bits (bit vector operations)
# 1 = hmac, 2 = chap, 3 = rsa, 4 = sha, 5 = sha2, 6 = rc4, and 7 = aes
num_cryptos = 7
Sec_prof_node_pair = [[[Bool('sec_prof_node_pair_%s_%s_%s' % (i, j, k)) 
                        for k in range(0, num_cryptos + 1)] 
                       for j in range(0, num_nodes + 1)] 
                      for i in range(0, num_nodes + 1)]
#print Sec_prof_node_pair

sec_prof_node_pair = [[[0 for k in range(0, num_cryptos + 1)] for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]

while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()    

    if (len(words) == 1):                       
        # Assuming that the reachabilities are given for the time being
        m = int(words[0])
        for l in range(m):
            while True:
                line = f_read.readline()
                if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
                    continue

                words = line.split()
                        
                if (len(words) > 2):    # At least a single crypto algorithm and key will be at each entry
                    i = int(words[0])
                    j = int(words[1])                    
                    for k in range(2, len(words)):
                        if (words[k] == "hmac"): sec_prof_node_pair[i][j][1] = 1;
                        elif (words[k] == "chap"): sec_prof_node_pair[i][j][2] = 1;
                        elif (words[k] == "rsa"): sec_prof_node_pair[i][j][3] = 1;
                        elif (words[k] == "sha"): sec_prof_node_pair[i][j][4] = 1;
                        elif (words[k] == "sha2"): sec_prof_node_pair[i][j][5] = 1;
                        elif (words[k] == "rc4"): sec_prof_node_pair[i][j][6] = 1;
                        elif (words[k] == "aes"): sec_prof_node_pair[i][j][7] = 1;
                        elif (words[k] == "des"): sec_prof_node_pair[i][j][8] = 1;
                else:
                    print ('Unmatched Input: Exit')
                    sys.exit()

                break
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

for i in range(1, num_nodes + 1):
    for j in range(1, num_nodes + 1):
        if (reachability[i][j] == 1):
            for k in range(1, num_cryptos + 1):
                if (sec_prof_node_pair[i][j][k] == 1):
                    slv.add(Sec_prof_node_pair[i][j][k] == True)
                else:
                    slv.add(Sec_prof_node_pair[i][j][k] == False)


# Authenticated communication from an ied to the mtu
Authenticated = [Bool('authenticated_%s' % i) for i in range(0, num_ieds + 1)]

for i in range(1, num_ieds + 1):
    Exprs = []
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        Exprs.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                            Or(Sec_prof_node_pair[i][j][1], Sec_prof_node_pair[i][j][2], Sec_prof_node_pair[i][j][3]),
                            Or(Sec_prof_node_pair[j][num_nodes][1], Sec_prof_node_pair[j][num_nodes][2], Sec_prof_node_pair[j][num_nodes][3])))
    slv.add(Implies(Authenticated[i], Or(Exprs)))

# Integrity protected communication from an ied to the mtu
Integrity_protected = [Bool('integrity_protected_%s' % i) for i in range(0, num_ieds + 1)]

for i in range(1, num_ieds + 1):
    Exprs = []
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        Exprs.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                            Or(Sec_prof_node_pair[i][j][3], Sec_prof_node_pair[i][j][4], Sec_prof_node_pair[i][j][5], Sec_prof_node_pair[i][j][7]),
                            Or(Sec_prof_node_pair[j][num_nodes][3], Sec_prof_node_pair[j][num_nodes][4], Sec_prof_node_pair[j][num_nodes][5], Sec_prof_node_pair[j][num_nodes][7])))
    slv.add(Implies(Integrity_protected[i], Or(Exprs)))

# Measurement authenticated and integrity protected to the mtu
Msr_secured = [Bool('msr_secured_%s' % i) for i in range(0, num_msrs + 1)]

for j in range(1, num_msrs + 1):
    Exprs = []
    for i in range(1, num_ieds + 1):
        Exprs.append(And (Ied_msr_relation[i][j], Authenticated[i], Integrity_protected[i]))
    slv.add(Implies(Msr_secured[j], Or(Exprs)))

# Secured states
State_secured = [Bool('state_secured_%s' % i) for i in range(0, num_states + 1)]

for i in range(1, num_states + 1):
    Exprs = []
    for j in range(1, num_msrs + 1):
        Exprs.append(And (State_msr_relation[i][j], Msr_secured[j]))
    slv.add(Implies(State_secured[i], Or(Exprs)))


# Number of secured measurement are at least equal to the number of states
Msr_secured_int = [Int('msr_secured_int_%s' % i) for i in range(0, num_msrs + 1)]

BExprs = []
for i in range(1, num_msrs + 1):        
    BExprs.append(And(Implies(Msr_secured[i], Msr_secured_int[i] == 1), Implies(Msr_secured[i] == False, Msr_secured_int[i] == 0)))

slv.add(And(BExprs))
 
IExprs = []
for i in range(1, num_msrs + 1):        
    IExprs.append(Msr_secured_int[i])

slv.add(Sum(IExprs) >= num_states)


# All the states are secured
Exprs2 = []
for i in range(1, num_states + 1):        
    Exprs2.append(State_secured[i])

slv.add(And(Exprs2))


# Solve the formal model
status = slv.check()

#f_write = open('Output_ICS.txt', 'a+')
#f_write.writeline(status);
print status

if (str(status) == 'sat'):
    m = slv.model()
    print m
    for i in range(1, num_ieds + 1):
        print i, ': ', m[Authenticated[i]]

    for i in range(1, num_ieds + 1):
        print i, ': ', m[Integrity_protected[i]]

    for i in range(1, num_msrs + 1):
        print i, ': ', m[Msr_secured[i]]

"""
sat
[msr_secured_3 = True,
 msr_secured_5 = True,
 msr_secured_int_2 = 1,
 msr_secured_1 = True,
 msr_secured_11 = True,
 msr_secured_int_1 = 1,
 msr_secured_int_3 = 1,
 msr_secured_int_11 = 1,
 msr_secured_int_5 = 1,
 msr_secured_2 = True,
 integrity_protected_3 = True,
 authenticated_3 = True,
 integrity_protected_2 = True,
 authenticated_2 = True,
 integrity_protected_1 = True,
 authenticated_1 = True,
 state_secured_5 = True,
 state_secured_4 = True,
 state_secured_3 = True,
 state_secured_2 = True,
 state_secured_1 = True,
 msr_secured_int_14 = 0,
 msr_secured_int_13 = 0,
 msr_secured_int_12 = 0,
 msr_secured_int_10 = 0,
 msr_secured_int_9 = 0,
 msr_secured_int_8 = 0,
 msr_secured_int_7 = 0,
 msr_secured_int_6 = 0,
 msr_secured_int_4 = 0,
 msr_secured_14 = False,
 msr_secured_13 = False,
 msr_secured_12 = False,
 msr_secured_10 = False,
 msr_secured_9 = False,
 msr_secured_8 = False,
 msr_secured_7 = False,
 msr_secured_6 = False,
 msr_secured_4 = False,
 integrity_protected_8 = False,
 integrity_protected_7 = False,
 integrity_protected_6 = False,
 integrity_protected_5 = False,
 integrity_protected_4 = False,
 authenticated_4 = False,
 sec_prof_node_pair_12_13_7 = True,
 sec_prof_node_pair_12_13_6 = False,
 sec_prof_node_pair_12_13_5 = False,
 sec_prof_node_pair_12_13_4 = False,
 sec_prof_node_pair_12_13_3 = True,
 sec_prof_node_pair_12_13_2 = False,
 sec_prof_node_pair_12_13_1 = False,
 sec_prof_node_pair_11_13_7 = True,
 sec_prof_node_pair_11_13_6 = False,
 sec_prof_node_pair_11_13_5 = False,
 sec_prof_node_pair_11_13_4 = False,
 sec_prof_node_pair_11_13_3 = True,
 sec_prof_node_pair_11_13_2 = False,
 sec_prof_node_pair_11_13_1 = False,
 sec_prof_node_pair_10_13_7 = True,
 sec_prof_node_pair_10_13_6 = False,
 sec_prof_node_pair_10_13_5 = False,
 sec_prof_node_pair_10_13_4 = False,
 sec_prof_node_pair_10_13_3 = True,
 sec_prof_node_pair_10_13_2 = False,
 sec_prof_node_pair_10_13_1 = False,
 sec_prof_node_pair_9_13_7 = True,
 sec_prof_node_pair_9_13_6 = False,
 sec_prof_node_pair_9_13_5 = False,
 sec_prof_node_pair_9_13_4 = False,
 sec_prof_node_pair_9_13_3 = True,
 sec_prof_node_pair_9_13_2 = False,
 sec_prof_node_pair_9_13_1 = False,
 sec_prof_node_pair_8_12_7 = False,
 sec_prof_node_pair_8_12_6 = False,
 sec_prof_node_pair_8_12_5 = False,
 sec_prof_node_pair_8_12_4 = False,
 sec_prof_node_pair_8_12_3 = False,
 sec_prof_node_pair_8_12_2 = False,
 sec_prof_node_pair_8_12_1 = True,
 sec_prof_node_pair_7_12_7 = False,
 sec_prof_node_pair_7_12_6 = False,
 sec_prof_node_pair_7_12_5 = False,
 sec_prof_node_pair_7_12_4 = False,
 sec_prof_node_pair_7_12_3 = False,
 sec_prof_node_pair_7_12_2 = False,
 sec_prof_node_pair_7_12_1 = True,
 sec_prof_node_pair_6_11_7 = False,
 sec_prof_node_pair_6_11_6 = False,
 sec_prof_node_pair_6_11_5 = False,
 sec_prof_node_pair_6_11_4 = False,
 sec_prof_node_pair_6_11_3 = False,
 sec_prof_node_pair_6_11_2 = False,
 sec_prof_node_pair_6_11_1 = True,
 sec_prof_node_pair_5_11_7 = False,
 sec_prof_node_pair_5_11_6 = False,
 sec_prof_node_pair_5_11_5 = False,
 sec_prof_node_pair_5_11_4 = False,
 sec_prof_node_pair_5_11_3 = False,
 sec_prof_node_pair_5_11_2 = False,
 sec_prof_node_pair_5_11_1 = True,
 sec_prof_node_pair_4_10_7 = False,
 sec_prof_node_pair_4_10_6 = False,
 sec_prof_node_pair_4_10_5 = False,
 sec_prof_node_pair_4_10_4 = False,
 sec_prof_node_pair_4_10_3 = False,
 sec_prof_node_pair_4_10_2 = False,
 sec_prof_node_pair_4_10_1 = False,
 sec_prof_node_pair_3_9_7 = False,
 sec_prof_node_pair_3_9_6 = False,
 sec_prof_node_pair_3_9_5 = True,
 sec_prof_node_pair_3_9_4 = False,
 sec_prof_node_pair_3_9_3 = False,
 sec_prof_node_pair_3_9_2 = True,
 sec_prof_node_pair_3_9_1 = False,
 sec_prof_node_pair_2_9_7 = False,
 sec_prof_node_pair_2_9_6 = False,
 sec_prof_node_pair_2_9_5 = True,
 sec_prof_node_pair_2_9_4 = False,
 sec_prof_node_pair_2_9_3 = False,
 sec_prof_node_pair_2_9_2 = True,
 sec_prof_node_pair_2_9_1 = False,
 sec_prof_node_pair_1_9_7 = False,
 sec_prof_node_pair_1_9_6 = False,
 sec_prof_node_pair_1_9_5 = True,
 sec_prof_node_pair_1_9_4 = False,
 sec_prof_node_pair_1_9_3 = False,
 sec_prof_node_pair_1_9_2 = True,
 sec_prof_node_pair_1_9_1 = False,
 ...]
1 :  True
2 :  True
3 :  True
4 :  False
5 :  None
6 :  None
7 :  None
8 :  None
1 :  True
2 :  True
3 :  True
4 :  False
5 :  False
6 :  False
7 :  False
8 :  False
1 :  True
2 :  True
3 :  True
4 :  False
5 :  True
6 :  False
7 :  False
8 :  False
9 :  False
10 :  False
11 :  True
12 :  False
13 :  False
14 :  False
Press any key to continue . . .
"""

"""
A = Bool('a') 
B = Bool('b')
C = Bool('c')
slv.add(A)
slv.add(B)
slv.add(C == False)
slv.add(Implies(A, And(B, C)))
"""

"""
# Relation between states and measurements (Jacobian matrix)
state_msr_relation = [Bool('state_msr_%s_%s' % (i, j)) for i in range(num_msrs) for j in range(num_states)]


# Relation between ieds and measurements
ied_msr_relation = [Bool('ied_msr_%s_%s' % (i, j)) for i in range(num_ieds) for j in range(num_states)]


# Reachability
reachable = [Bool('reachable_%s_%s' % (i, j)) for (i, j) in reachabilities]
"""

"""
x = Int('x')
p3 = Bool('p3')
s = Solver()
s.set(unsat_core=True)

s.add(x > 0)
s.add(x != 1)
s.assert_and_track(x < 0, p3)

#s.assert_and_track(x > 0,  'p1')
#s.assert_and_track(x != 1, 'p2')
#s.assert_and_track(x < 0,  p3)

print(s.check())
c = s.unsat_core()
print c
"""