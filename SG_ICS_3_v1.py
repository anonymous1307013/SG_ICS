# Solve considering unique measurements from power flow and power consumption point of view
# k-resiliency

import io
import sys

from z3 import*


f_read = open('Input_ICS_3.txt', 'r')

slv = Solver()

#################################################
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

#################################################
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

#################################################
# The unique measurement sets (Should it be an input?)
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 1):        
        num_unique_msrs = int(words[0])
        #print num_states, num_msrs
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

# Power flow measurements
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 1):        
        num_unique_msrs_flow = int(words[0])        
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

uMsrSets = []
for i in range(num_unique_msrs_flow):
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
        
        if (len(words) > 0):
            members = []
            for j in range(len(words)):
                members.append(int(words[j]))
        
            uMsrSets.append(members)

        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break    

# Power consumption measurements
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 1):        
        num_unique_msrs_multi = int(words[0])        
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

for i in range(num_unique_msrs_multi):
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
        
        if (len(words) > 0):
            members = []
            for j in range(len(words)):
                members.append(int(words[j]))
        
            uMsrSets.append(members)

        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break    

#################################################
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

#################################################
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

#################################################
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
################## Input Ends ###################

#################################################
# Authentication and data integrity protection calculation, as well as identifying the RTU at the hierarchically top position towards MTU
# Authenticated communication from an ied to the mtu
Authenticated = [Bool('authenticated_%s' % i) for i in range(0, num_ieds + 1)]

# Integrity protected communication from an ied to the mtu
Integrity_protected = [Bool('integrity_protected_%s' % i) for i in range(0, num_ieds + 1)]

# RTU on the secured path associated with the IED
Ied_associated_rtu = [Int('ied_associated_rtu_%s' % i) for i in range(0, num_ieds + 1)]

bIedToMTUPath = [False for i in range(0, num_nodes + 1)]

# Single intermediate node (RTU)
for i in range(1, num_ieds + 1):
    ExpA = []
    ExpI = []
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        if ((reachability[i][j] == 1) and (reachability[j][num_nodes] == 1)):
            bIedToMTUPath[i] = True
            slv.add(Ied_associated_rtu[i] == j)
            ExpA.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                                Or(Sec_prof_node_pair[i][j][1], Sec_prof_node_pair[i][j][2], Sec_prof_node_pair[i][j][3]),
                                Or(Sec_prof_node_pair[j][num_nodes][1], Sec_prof_node_pair[j][num_nodes][2], Sec_prof_node_pair[j][num_nodes][3])))
            ExpI.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                                Or(Sec_prof_node_pair[i][j][3], Sec_prof_node_pair[i][j][4], Sec_prof_node_pair[i][j][5], Sec_prof_node_pair[i][j][7]),
                                Or(Sec_prof_node_pair[j][num_nodes][3], Sec_prof_node_pair[j][num_nodes][4], Sec_prof_node_pair[j][num_nodes][5], Sec_prof_node_pair[j][num_nodes][7])))
    
    # If there is at least one path to the MTU
    if (len(ExpA) > 0): # Then, len(ExpI) > 0
        slv.add(Implies(Authenticated[i], Or(ExpA)))        
        slv.add(Implies(Integrity_protected[i], Or(ExpI)))               


# Double intermediate nodes (RTUs)
for i in range(1, num_ieds + 1):
    ExpA = []
    ExpI = []
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):        
        for k in range(num_ieds + 1, num_ieds + num_rtus + 1):
            if (j == k):
                continue
            if ((reachability[i][j] == 1) and (reachability[j][k] == 1) and (reachability[k][num_nodes] == 1)):
                bIedToMTUPath[i] = True
                slv.add(Ied_associated_rtu[i] == j)
                ExpA.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                                    Or(Sec_prof_node_pair[i][j][1], Sec_prof_node_pair[i][j][2], Sec_prof_node_pair[i][j][3]),
                                    Or(Sec_prof_node_pair[j][k][1], Sec_prof_node_pair[j][k][2], Sec_prof_node_pair[j][k][3]),
                                    Or(Sec_prof_node_pair[k][num_nodes][1], Sec_prof_node_pair[k][num_nodes][2], Sec_prof_node_pair[k][num_nodes][3])))
                ExpI.append(And (Reachability[i][j], Reachability[j][num_nodes], 
                                    Or(Sec_prof_node_pair[i][j][3], Sec_prof_node_pair[i][j][4], Sec_prof_node_pair[i][j][5], Sec_prof_node_pair[i][j][7]),
                                    Or(Sec_prof_node_pair[j][k][3], Sec_prof_node_pair[j][k][4], Sec_prof_node_pair[j][k][5], Sec_prof_node_pair[j][k][7]),
                                    Or(Sec_prof_node_pair[k][num_nodes][3], Sec_prof_node_pair[k][num_nodes][4], Sec_prof_node_pair[k][num_nodes][5], Sec_prof_node_pair[k][num_nodes][7])))

    # If there is at least one path to the MTU
    if (len(ExpA) > 0): # Then, len(ExpI) > 0
        slv.add(Implies(Authenticated[i], Or(ExpA)))
        slv.add(Implies(Integrity_protected[i], Or(ExpI)))
    

# If there is no path from an IED to the MTU
for i in range(1, num_ieds + 1):
    if (bIedToMTUPath[i] == False):
        slv.add(Authenticated[i] == False)
        slv.add(Integrity_protected[i] == False)


# Measurement authenticated and integrity protected to the mtu
Msr_secured = [Bool('msr_secured_%s' % i) for i in range(0, num_msrs + 1)]

for j in range(1, num_msrs + 1):
    Exprs = []
    for i in range(1, num_ieds + 1):
        Exprs.append(And (Ied_msr_relation[i][j], Authenticated[i], Integrity_protected[i]))
    
    slv.add(Implies(Msr_secured[j], Or(Exprs)))

#################################################
# Security of unique measurements 
UMsr_secured = [Bool('unique_msr_secured_%s' % i) for i in range(0, num_unique_msrs + 1)]

for i in range(1, num_unique_msrs_flow + 1):
    members = uMsrSets[i - 1]    
    Exprs = []
    for j in range(len(members)):
        Exprs.append(Msr_secured[members[j]])

    slv.add(Implies(UMsr_secured[i], Or(Exprs)))

# Security of unique measurements (multiple)

for i in range(num_unique_msrs_flow + 1, num_unique_msrs_flow + num_unique_msrs_multi + 1):
    members = uMsrSets[i - 1]    
    Exprs = []
    for j in range(1, len(members)):
        Exprs.append(UMsr_secured[members[j]])

    slv.add(Implies(UMsr_secured[i], And(Msr_secured[members[0]], Not(And(Exprs)))))

#################################################
# Security of states derived from the security of ieds 
# Security of unique measurements is not an issue, since it only looks for the coverage by the secured measurements
# and measurements within the unique measurement set cover the same states.

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

#################################################
# Relation with states, IEDs, and RTUs
Secured_state_ied_relation = [[Bool('secured_state_ied_relation_%s_%s' % (i, j)) 
                               for j in range(0, num_ieds + 1)] 
                              for i in range(0, num_states + 1)]

for i in range(1, num_states + 1):    
    for j in range(1, num_ieds + 1):
        Exprs = []
        for k in range(1, num_msrs + 1):
            Exprs.append(And (State_msr_relation[i][k], Msr_secured[k], Ied_msr_relation[j][k]))
    
        slv.add(Implies(Secured_state_ied_relation[i][j], Or(Exprs)))


Secured_state_rtu_relation = [[Bool('secured_state_rtu_relation_%s_%s' % (i, j)) 
                               for j in range(0, num_ieds + num_rtus + 1)] 
                              for i in range(0, num_states + 1)]

for i in range(1, num_states + 1):    
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        Exprs = []
        for k in range(1, num_ieds + 1):
            Exprs.append(And (Secured_state_ied_relation[i][k], (Ied_associated_rtu[k] == j)))
    
        slv.add(Implies(Secured_state_rtu_relation[i][j], Or(Exprs)))

#################################################
# Number of secured (unique) measurements are at least equal to the number of states
UMsr_secured_int = [Int('unique_msr_secured_int_%s' % i) for i in range(0, num_unique_msrs + 1)]

BExprs = []
for i in range(1, num_unique_msrs + 1):        
    BExprs.append(And(Implies(UMsr_secured[i], UMsr_secured_int[i] == 1), Implies(UMsr_secured[i] == False, UMsr_secured_int[i] == 0)))

slv.add(And(BExprs))
 
IExprs = []
for i in range(1, num_unique_msrs + 1):        
    IExprs.append(UMsr_secured_int[i])

slv.add(Sum(IExprs) >= num_states)

#################################################
# All the states are secured
Exprs2 = []
for i in range(1, num_states + 1):
    Exprs2.append(State_secured[i])

slv.add(And(Exprs2))

#################################################
# Number of IEDs associated with each state must be greater than k (k-resiliency)
Secured_state_ied_relation_int = [[Int('secured_state_ied_relation_int_%s_%s' % (i, j)) 
                               for j in range(0, num_ieds + 1)] 
                              for i in range(0, num_states + 1)]

BExprs = []
for i in range(1, num_states + 1):        
    for j in range(1, num_ieds + 1):
        BExprs.append(And(Implies(Secured_state_ied_relation[i][j], Secured_state_ied_relation_int[i][j] == 1), 
                          Implies(Secured_state_ied_relation[i][j] == False, Secured_state_ied_relation_int[i][j] == 0)))

slv.add(And(BExprs))
 

# For each state, we need to see if there is k+1 RTUs responsible to send measurements related to that state
k_resilient_ied = 2
for i in range(1, num_states + 1):        
    IExprs = []
    for j in range(1, num_ieds + 1):
        IExprs.append(Secured_state_ied_relation_int[i][j])

    slv.add(Sum(IExprs) > k_resilient_ied)

#################################################
# Number of RTUs associated with each state must be greater than k (k-resiliency)
Secured_state_rtu_relation_int = [[Int('secured_state_rtu_relation_int_%s_%s' % (i, j)) 
                                   for j in range(0, num_ieds + num_rtus + 1)] 
                                  for i in range(0, num_states + 1)]

BExprs = []
for i in range(1, num_states + 1):        
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        BExprs.append(And(Implies(Secured_state_rtu_relation[i][j], Secured_state_rtu_relation_int[i][j] == 1), 
                          Implies(Secured_state_rtu_relation[i][j] == False, Secured_state_rtu_relation_int[i][j] == 0)))

slv.add(And(BExprs))
 

# For each state, we need to see if there is k'+1 RTUs responsible to send measurements related to that state
k_resilient_rtu = 0
for i in range(1, num_states + 1):        
    IExprs = []
    for j in range(num_ieds + 1, num_ieds + num_rtus + 1):
        IExprs.append(Secured_state_rtu_relation_int[i][j])

    slv.add(Sum(IExprs) > k_resilient_rtu)

#################################################
# Solve the formal model
status = slv.check()

f_write = open('Output_ICS_3.txt', 'a')
f_write.write(str(status))
f_write.write('\n')
print status

if (str(status) == 'sat'):
    m = slv.model()
    f_write.write('Model\n')
    f_write.write(str(m))
    f_write.write('\n')

    f_write.write('\nAuthenticated IEDs\n')
    for i in range(1, num_ieds + 1):
        print i, ': ', m[Authenticated[i]]
        f_write.write(str(i) + ': ' + str(m[Authenticated[i]]) + '\n')

    f_write.write('\nIntegrity protected IEDs\n')
    for i in range(1, num_ieds + 1):
        print i, ': ', m[Integrity_protected[i]]
        f_write.write(str(i) + ': ' + str(m[Integrity_protected[i]]) + '\n')

    f_write.write('\nSecured measurements\n')
    for i in range(1, num_msrs + 1):
        print i, ': ', m[Msr_secured[i]]
        f_write.write(str(i) + ': ' + str(m[Msr_secured[i]]) + '\n')

    f_write.write('\nSecured unique measurements\n')
    for i in range(1, num_unique_msrs + 1):
        print i, ': ', m[UMsr_secured[i]]
        f_write.write(str(i) + ': ' + str(m[UMsr_secured[i]]) + '\n')

    f_write.write('\n')

##################### End #######################
