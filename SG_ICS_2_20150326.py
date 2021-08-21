import io
import sys

from z3 import*


f_read = open('Input_ICS_2.txt', 'r')

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
# The unique measurement sets (TODO: it should not be an input)
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 1):        
        num_umsrs = int(words[0])
        #print num_states, num_msrs
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

uMsrSets = []
for i in range(num_umsrs):
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

#################################################
# Security of unique measurements 
UMsr_secured = [Bool('unique_msr_secured_%s' % i) for i in range(0, num_umsrs + 1)]

for i in range(1, num_umsrs + 1):
    members = uMsrSets[i - 1]    
    Exprs = []
    for j in range(len(members)):
        Exprs.append(Msr_secured[members[j]])

    slv.add(Implies(UMsr_secured[i], Or(Exprs)))

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
# Number of secured unique measurements are at least equal to the number of states
## Number of secured measurements are at least equal to the number of states
#Msr_secured_int = [Int('msr_secured_int_%s' % i) for i in range(0, num_msrs + 1)]

#BExprs = []
#for i in range(1, num_msrs + 1):        
#    BExprs.append(And(Implies(Msr_secured[i], Msr_secured_int[i] == 1), Implies(Msr_secured[i] == False, Msr_secured_int[i] == 0)))

#slv.add(And(BExprs))
 
#IExprs = []
#for i in range(1, num_msrs + 1):        
#    IExprs.append(Msr_secured_int[i])

#slv.add(Sum(IExprs) >= num_states)

UMsr_secured_int = [Int('unique_msr_secured_int_%s' % i) for i in range(0, num_umsrs + 1)]

BExprs = []
for i in range(1, num_umsrs + 1):        
    BExprs.append(And(Implies(UMsr_secured[i], UMsr_secured_int[i] == 1), Implies(UMsr_secured[i] == False, UMsr_secured_int[i] == 0)))

slv.add(And(BExprs))
 
IExprs = []
for i in range(1, num_umsrs + 1):        
    IExprs.append(UMsr_secured_int[i])

slv.add(Sum(IExprs) >= num_states)

#################################################
# All the states are secured
Exprs2 = []
for i in range(1, num_states + 1):        
    Exprs2.append(State_secured[i])

slv.add(And(Exprs2))

#################################################
# Solve the formal model
status = slv.check()

f_write = open('Output_ICS_2.txt', 'a')
f_write.write(str(status))
f_write.write('\n')
print status

if (str(status) == 'sat'):
    m = slv.model()
    f_write.write('Model\n')
    f_write.write(str(m))
    f_write.write('\n')

    f_write.write('\nAuthenticated measurements\n')
    for i in range(1, num_ieds + 1):
        print i, ': ', m[Authenticated[i]]
        f_write.write(str(i) + ': ' + str(m[Authenticated[i]]) + '\n')

    f_write.write('\nIntegrity protected measurements\n')
    for i in range(1, num_ieds + 1):
        print i, ': ', m[Integrity_protected[i]]
        f_write.write(str(i) + ': ' + str(m[Integrity_protected[i]]) + '\n')

    f_write.write('\nSecured measurements\n')
    for i in range(1, num_msrs + 1):
        print i, ': ', m[Msr_secured[i]]
        f_write.write(str(i) + ': ' + str(m[Msr_secured[i]]) + '\n')

    f_write.write('\nSecured unique measurements\n')
    for i in range(1, num_umsrs + 1):
        print i, ': ', m[UMsr_secured[i]]
        f_write.write(str(i) + ': ' + str(m[UMsr_secured[i]]) + '\n')

    f_write.write('\n')

##################### End #######################
