## This specific model is to find all threatvectors

## The model for k-Resilient Observability
## Solve the problem from a attack vector synthesis point of view. If an attack vector is not found, it means that the system is k-resilient.
## Consider unique measurements from power flow and power consumption point of views

## We CONSIDER the full measurement set and the input representing whether a measurement is taken or not.
## We CONSIDER any number of intermediate nodes (RTUs) toward the MTU.
## We CONSIDER the possbility of multiple paths from an IED to the MTU.
## We CONSIDER the case when a measurement can be measured by more than two IEDs.

import io
import sys
import datetime

from z3 import *

NUMBER_BUSES = 14
NUMBER_LINES = 20
RTU_MTU_HIERARCHY_LEVEL = 4

f_name = 'Input_ICS_Bus_' + str(NUMBER_BUSES) + '_' + str(NUMBER_LINES) + '_' + str(RTU_MTU_HIERARCHY_LEVEL) + '.txt'
f_read = open(f_name, 'r')

slv = Solver()

#################################################
## Number of states and measurements
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
## Jacobian matrix (the relation between the states and the measurements), plus if the measurement is taken or not
State_msr_relation = [[Bool('state_msr_%s_%s' % (i, j)) for j in range(0, num_msrs + 1)] for i in range(0, num_states + 1)]
#print State_msr_relation

msr = [False for j in range(0, num_msrs + 1)]

for j in range(1, num_msrs + 1):     
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) == num_states + 1):
            ## If the corresponding measurement is taken
            if (words[num_states] == "1"):
                msr[j] = True
            else:
                msr[j] = False
            
            #print words[num_states]

            for i in range(1, num_states + 1):
                if ((words[i - 1] == "0") or (msr[j] == False)):    ## If the measurement is not taken or the matrix entry is zero
                    slv.add(State_msr_relation[i][j] == False)                    
                else:                    
                    slv.add(State_msr_relation[i][j] == True) 
                                       
                #print words[i - 1]            

        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break


#################################################
## Unique power flow measurements
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

## Unique power consumption measurements
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

num_unique_msrs = num_unique_msrs_flow + num_unique_msrs_multi  ## Number of total unique measurement sets

#################################################
## Number of IEDs (e.g., 1-8) and RTUs (e.g., 9-12) 
## 1 MTU (i.e., 13) is assumed
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

## Total number of nodes/devices (IEDs, RTUs, and MTU)
num_nodes = num_ieds + num_rtus + 1 # 1 is for the MTU

## A node (RTU or IED) can be unavailable 
Node = [Bool('node_%s' % i) for i in range(0, num_nodes + 1)]

slv.add(Node[num_nodes]) ## the MTU is always alive

## Measurements corresponding to IEDs
ied_msr_association = [[False for j in range(0, num_msrs + 1)] for i in range(0, num_ieds + 1)]
#print ied_msr_relation

for i in range(1, num_ieds + 1):     
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) > 0):    # At least a single measurement is transmitted by this ied
            for j in range(1, num_msrs + 1): 
                if ((str(j) in words[1 : len(words)]) and (msr[j] == True)):                    
                    ied_msr_association[i][j] = True
        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break

#################################################
## Topology
#################################################
## Connectivity (among the IEDs, the RTUs, and the MTU)
Connected = [[Bool('connected_%s_%s' % (i, j)) for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]
#print Connected

connected = [[0 for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]

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
                        
                if (len(words) == 2):
                    i = int(words[0])
                    j = int(words[1])      
                    connected[i][j] = 1;                                                      
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
        if (connected[i][j] == 1):
            slv.add(Connected[i][j] == True)
        else:
            slv.add(Connected[i][j] == False)                    


#################################################
## k-Resiliency requirements
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 2):
        k_resiliency_ieds = int(words[0])
        k_resiliency_rtus = int(words[1])
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break

################## Input Ends ###################


#################################################
## Reachable if there is connectivity and both of the nodes are available
Reachable = [[Bool('reachability_%s_%s' % (i, j)) for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]
for i in range(1, num_nodes + 1):
    for j in range(1, num_nodes + 1):        
            slv.add(Implies(Reachable[i][j], And(Connected[i][j], Node[i], Node[j])))
            slv.add(Implies(And(Connected[i][j], Node[i], Node[j]), Reachable[i][j]))


#################################################
## There is a communication Path from an IED to the MTU
CommPath = [Bool('commPath%s' % i) for i in range(0, num_ieds + 1)]

## If there is a path from IED to MTU (through RTU)
bIedToMTUPath = [False for i in range(0, num_nodes + 1)]

## Find paths from an IED (actually the connected RTU) toward the MTU (the highest Id)

paths = []
def find_path(cur, dest, path):
    if (cur == dest):
        paths.append(path)
        return

    for next in range(1, num_nodes + 1):
        if ((path.count(next) == 0) and (connected[cur][next] == 1)):
            path.append(next)
            find_path(next, dest, path)

    return

for i in range(1, num_ieds + 1):    ## For each IED    
    paths = []
    find_path(i, num_nodes, [i])

    if (len(paths) > 0):
        bIedToMTUPath[i] = True
        Exprs = []        
        for j in range(0, len(paths)):
            path = paths[j]
            Exprs2 = []
            for k in range(0, len(path) - 1):
                Exprs2.append(Reachable[path[k]][path[k + 1]])
            Exprs.append(And(Exprs2))

        slv.add(Implies(CommPath[i], Or(Exprs)))        
        slv.add(Implies(Or(Exprs), CommPath[i]))     
          
    else:
        bIedToMTUPath[i] = False
        slv.add(CommPath[i] == False)


## Measurement delivered to the mtu
Msr_delivered = [Bool('msr_delivered_%s' % i) for i in range(0, num_msrs + 1)]

## Done: Why Do We Need To Consider Each Msr and Each Ied, WHILE We Already Know The Relation Between A Msr and An IED (Change from the last version)
## Here we also CONSIDER the case when a measurement is can be measured by more than two ides.
for j in range(1, num_msrs + 1):
    Exprs = []
    for i in range(1, num_ieds + 1):
        if (ied_msr_association[i][j] == True):
            Exprs.append(CommPath[i])
    
    if (len(Exprs) > 0):
        slv.add(Implies(Msr_delivered[j], Or(Exprs)))
        slv.add(Implies(Or(Exprs), Msr_delivered[j]))
    else:
        slv.add(Msr_delivered[j] == False)

#################################################
## Delivery of unique measurements  with regards to power flows
UMsr_delivered = [Bool('unique_msr_delivered_%s' % i) for i in range(0, num_unique_msrs + 1)]

for i in range(1, num_unique_msrs_flow + 1):
    members = uMsrSets[i - 1]    
    Exprs = []
    for j in range(len(members)):
        Exprs.append(Msr_delivered[members[j]])

    slv.add(Implies(UMsr_delivered[i], Or(Exprs)))
    slv.add(Implies(Or(Exprs), UMsr_delivered[i]))

## Delivery of unique bus consumption measurements with regards to unique power flow measurements

for i in range(num_unique_msrs_flow + 1, num_unique_msrs_flow + num_unique_msrs_multi + 1):
    members = uMsrSets[i - 1]    
    Exprs = []
    for j in range(1, len(members)):
        Exprs.append(UMsr_delivered[members[j]])
    
    if (len(Exprs) > 0):
        slv.add(Implies(UMsr_delivered[i], And(Msr_delivered[members[0]], Not(And(Exprs)))))
        slv.add(Implies(And(Msr_delivered[members[0]], Not(And(Exprs))), UMsr_delivered[i]))
    else:
        slv.add(Implies(UMsr_delivered[i], Msr_delivered[members[0]]))
        slv.add(Implies(Msr_delivered[members[0]], UMsr_delivered[i]))

#################################################
## Security of states derived from the security of ieds 
## Security of unique measurements is not an issue, since it only looks for the coverage by the secured measurements
## and measurements within the unique measurement set cover the same states.

# Secured states
State_delivered = [Bool('state_delivered_%s' % i) for i in range(0, num_states + 1)]

for i in range(1, num_states + 1):
    Exprs = []
    for j in range(1, num_msrs + 1):
        Exprs.append(And (State_msr_relation[i][j], Msr_delivered[j]))
    
    slv.add(Implies(State_delivered[i], Or(Exprs)))
    slv.add(Implies(Or(Exprs), State_delivered[i]))

#################################################
## The number of unavailable (failed/under-attack) RTUs or IEDs

Node_int = [Int('node_int_%s' % i) for i in range(0, num_nodes + 1)]

BExprs = []
for i in range(1, num_nodes + 1):        
    BExprs.append(And(Implies(Node[i], Node_int[i] == 1), Implies(Node[i] == False, Node_int[i] == 0)))

slv.add(And(BExprs))

### Irrespective of the node type (IED or RTU)
#IExprs = []
#for i in range(1, num_nodes + 1):
#    IExprs.append(Node_int[i])

### (num_nodes - k_resiliency_nodes) is the number of available nodes
#slv.add((Sum(IExprs) >= (num_nodes - k_resiliency_nodes)))

## Considering IEDs only
IExprs = []
for i in range(1, num_ieds + 1):
    IExprs.append(Node_int[i])

IExprs2 = []
for i in range(num_ieds + 1, num_ieds + num_rtus + 1):
    IExprs2.append(Node_int[i])

## (num_ieds - k_resiliency_ieds) is the number of available ieds
slv.add((Sum(IExprs) >= (num_ieds - k_resiliency_ieds)))

## (num_rtus - k_resiliency_rtus) is the number of available rtus
slv.add((Sum(IExprs2) >= (num_rtus - k_resiliency_rtus)))

#################################################
## k-Resiliency Threat Constraint Modeling
## Number of delivered (unique) measurements is less than the number of states OR
## All the states are not secured

## Counting secured measurements
UMsr_delivered_int = [Int('unique_msr_delivered_int_%s' % i) for i in range(0, num_unique_msrs + 1)]

BExprs = []
for i in range(1, num_unique_msrs + 1):        
    BExprs.append(And(Implies(UMsr_delivered[i], UMsr_delivered_int[i] == 1), Implies(UMsr_delivered[i] == False, UMsr_delivered_int[i] == 0)))

slv.add(And(BExprs))
 
IExprs = []
for i in range(1, num_unique_msrs + 1):        
    IExprs.append(UMsr_delivered_int[i])

## At least one state is not secured
Exprs2 = []
for i in range(1, num_states + 1):
    Exprs2.append(State_delivered[i] == False)

## Constraint
slv.add(Or((Sum(IExprs) < num_states), Or(Exprs2)))


#################################################
#################################################
## Solve the formal model

slv.push()
num_solution = 0
MAX_SOLUTION = 10000

f_write_name = 'Output_ICS_Bus_Vectors.txt'
f_write = open(f_write_name, 'a')

f_write.write('Bus:' + str(NUMBER_BUSES) + ' Lines:' + str(NUMBER_LINES) + ' Hierarchy:' + str(RTU_MTU_HIERARCHY_LEVEL) + ' ::\n')

while True:    
    status = slv.check()        

    if (str(status) == 'sat'):
        num_solution += 1

        print('Number of Solutions: ' + str(num_solution) + '\n')

        m = slv.model()        

        BExprs = []                            
        for i in range(1, num_nodes + 1):            
            if (str(m[Node[i]]) == 'True'):
                BExprs.append(Node[i] == True)
            else:
                BExprs.append(Node[i] == False)        

        if (num_solution >= MAX_SOLUTION):
            break

        slv.pop()
        slv.add(Not(And(BExprs)))
        #print slv.to_smt2()
        slv.push()

    else:
        print('No more satisfiable result')
        f_write.write('\nNo more satisfiabile result\n')
        break


f_write.write('Number of Solutions: ' + str(num_solution) + '\n')
f_write.write('***************************\n\n')

##################### End #######################
