
import io
import sys
import datetime
import random
from math import gcd
import time
from itertools import zip_longest # in Python 3 zip_longest
from z3 import *


f_name = 'Newip2.txt'
f_read = open(f_name, 'r')
f2 = open('Assertions.txt', 'a')

slv = Solver()

#################################################
### Number of flows
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n') or (line[0]=='\t')):
        continue

    words = line.split()
    
    if (len(words) == 3):
        num_flows = int(words[0])
        num_channels = int(words[1])
        num_nodes = int(words[2])
    else:
        print('Unmatched Input: Exit')
        sys.exit()

    break

### Packet Generation time, Periods and Deadlines of each flow
flow_period_deadline = []
for i in range(1, num_flows + 1):
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n') or (line[0]=='\t')):
            continue

        words = line.split()
        #print(words)
    
        if (len(words) == 4):
            list = []
            for j in range(0, len(words)):
                list.append(int(words[j]))
            flow_period_deadline.append(list)
        else:
            print('Unmatched Input: Exit')
            sys.exit()
        break


### Primary path of each flow
flow_path = []
for i in range(1, num_flows + 1):
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n') or (line[0]=='\t')):
            continue

        words = line.split()
        #print(words)
    
        if (len(words) > 0):
            list = []
            for j in range(1, len(words)):
                list.append(int(words[j]))
            flow_path.append(list)
        else:
            print('Unmatched Input: Exit')
            sys.exit()
        break


### Secondary paths list
secondary_path = []
for fl in range(1, num_flows + 1):
    ls2 = []
    for p in range(1, len(flow_path[fl - 1])):
        while True:
            line = f_read.readline()
            if ((line is None) or (line[0] == '#') or (line[0] == '\n') or (line[0]=='\t')):
                continue

            words = line.split()
    
            if (len(words) > 0):
                ls1 = []
                for j in range(2, len(words)):
                    ls1.append(int(words[j]))
                ls2.append(ls1)
                #secondary_path.append(ls1)
            else:
                print('Unmatched Input: Exit')
                sys.exit()
            break
    secondary_path.append(ls2)

################### Input Ends ###################

#### Connectivity (among the field devices)

### Connectivity of primary nodes
Connected_p = [[Bool('connected_p %s_%s' % (i, j)) for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]
connected_p = [[0 for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]

for l in range(0, len(flow_path)):
    ls1 = flow_path[l]
    for m in range(0, len(ls1) - 1):
        i = ls1[m]
        j = ls1[m + 1]
        connected_p[i][j] = 1   
          
for i in range(1, num_nodes + 1):
    for j in range(1, num_nodes + 1):
        if (connected_p[i][j] == 1):
            slv.add(Connected_p[i][j] == True)
        else:
            slv.add(Connected_p[i][j] == False)  


### Connectivity of secondary nodes
Connected_s = [[Bool('connected_s %s_%s' % (i, j)) for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]                                             
connected_s = [[0 for j in range(0, num_nodes + 1)] for i in range(0, num_nodes + 1)]   
               
for fl in range(1, num_flows + 1):
    for p in range(1, len(flow_path[fl - 1])):
        ls2 = secondary_path[fl - 1][p - 1]
        for q in range(0, len(ls2) - 1):
            i = ls2[q]
            j = ls2[q + 1]
            connected_s[i][j] = 1      

for i in range(1, num_nodes + 1):
    for j in range(1, num_nodes + 1):
        if (connected_s[i][j] == 1):
            slv.add(Connected_s[i][j] == True)
        else:
            slv.add(Connected_s[i][j] == False)     
            
## hyper-period, T (i.e., LCM of the periods of flows)
list_periods = []
for f in range(0, num_flows):
    list_periods.append(int(flow_period_deadline[f][-2]))  
lcm = list_periods[0]
for j in list_periods[1:]:
    lcm = int(lcm) * j / math.gcd(int(lcm), j)
T = int(lcm)
          

# Packet generation
packet_generate = [[0 for t in range(0, T + 1)] for f in range(0, num_flows + 1)]

for fl in range(1, num_flows + 1):                       
    starting_slot = flow_period_deadline[fl - 1][1]
    for ts in range(1, T + 1):
         if(ts == starting_slot):
            packet_generate[fl][ts] = 1            # Initilization of packet generation
for fl in range(1, num_flows + 1):
    for ts in range(1, T + 1):
        if(packet_generate[fl][ts] == 1):
            while(ts < T + 1):
                ts = flow_period_deadline[fl - 1][-2] + ts
                if (ts < T + 1):
                    packet_generate[fl][ts] = 1

pkt_per_flow = [0]
for fl in range(1, num_flows + 1):
    pkt_per_flow.append(sum(packet_generate[fl]))
#print(pkt_per_flow)
total_pkt = sum(pkt_per_flow)


####***********************************************************************************************************************************####

## pkt_per_flow = [total pkts generated by each flow]
## flow_path = [[list of nodes along primary path]]
## flow_period_deadline = [[Type, Time generation, Period, Deadline]]
## secondary_path = [[list of nodes along secondary path]]

######### Schedule of packets
### DT: Dedicated Transmission
### ST: Shared Transmission

DT = [[[[[[Bool('dt_%s_%s_%s_%s_%s_%s' % (fl,pkt,u,v,ch,ts)) for ts in range(0, T + 1)] for ch in range(0, num_channels + 1)]  for v in range(0, num_nodes + 1)] for u in range(0, num_nodes + 1)] for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]    
                      
ST = [[[[[[[Bool('st_%s_%s_%s_%s_%s_%s_%s' % (fl,pkt,path,u,v,ch,ts)) for ts in range(0, T + 1)] for ch in range(0, num_channels + 1)] for v in range(0, num_nodes + 1)] for u in range(0, num_nodes + 1)] for path in range(0, len(flow_path[fl - 1]))] for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

##### Channel Constriant
### if channel is used by DT, the same channel can't be used by any ST
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                Exp1=[]
                                for fp in range(1, num_flows + 1):
                                    for pp in range(1, pkt_per_flow[fp] + 1):
                                        for path in range(1, len(flow_path[fp - 1])):
                                            for sp in secondary_path[fp - 1][path - 1]:
                                                for rp in secondary_path[fp - 1][path - 1]:
                                                    if((sp != s) or (rp != r)):
                                                        if(connected_s[sp][rp]==1):
                                                            Exp1.append(Not(ST[fp][pp][path][sp][rp][ch][ts]))
                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1)))
                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1))))

### if channel is used by DT, the same channel can't be used by any DT
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                Exp1=[]
                                for fp in range(1, num_flows + 1):
                                    for pp in range(1, pkt_per_flow[fp] + 1):
                                        for sp in flow_path[fp - 1]:
                                            for rp in flow_path[fp - 1]:
                                                if((sp != s) or (rp != r)):
                                                    if(connected_p[sp][rp]==1):
                                                        Exp1.append(Not(DT[fp][pp][sp][rp][ch][ts]))
                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1)))

### if channel is used by ST, the same channel can't be used by any DT
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for path in range(1, len(flow_path[fl - 1])):
            for s in secondary_path[fl - 1][path - 1]:
                for r in secondary_path[fl - 1][path - 1]:
                    if(connected_s[s][r] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    Exp1=[]
                                    for fp in range(1, num_flows + 1):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for sp in flow_path[fp - 1]:
                                                for rp in flow_path[fp - 1]:
                                                    if((sp != s) or (rp != r)):
                                                        if(connected_p[sp][rp]==1):
                                                            Exp1.append(Not(DT[fp][pp][sp][rp][ch][ts]))
                                    slv.add(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp1)))

## if channel is used by ST, the same channel can't be used by any ST
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for path in range(1, len(flow_path[fl - 1])):
            for s in secondary_path[fl - 1][path - 1]:
                for r in secondary_path[fl - 1][path - 1]:
                    if(connected_s[s][r] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    Exp1=[]
                                    for fp in range(1, num_flows + 1):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for pthp in range(1, len(flow_path[fp - 1])):
                                                for sp in secondary_path[fp - 1][pthp - 1]:
                                                    for rp in secondary_path[fp - 1][pthp - 1]:
                                                        if((sp != s) or (rp != r)):
                                                            if(connected_s[sp][rp]==1):
                                                                Exp1.append(Not(ST[fp][pp][pthp][sp][rp][ch][ts]))
                                    slv.add(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp1)))

##### Relation between DT and ST of the same packet of the same flow                   
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1):
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                Exp1 = []
                                for path in range(1, len(flow_path[fl - 1])):
                                    for sp in secondary_path[fl - 1][path - 1]:
                                        for rp in secondary_path[fl - 1][path - 1]: 
                                            if(connected_s[sp][rp]==1):
                                                if(sp==s):
                                                    for cp in range(1, num_channels + 1):
                                                        for tp in range(t1, ts+1):
                                                            Exp1.append(Not(ST[fl][pkt][path][sp][rp][cp][tp]))
                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1)))
                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1))))

### Same packet can't be scheduled in different channel at same time along DT
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
       for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r]==1):
                    for ch in range(1, num_channels +1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl-1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                Exp=[]
                                for cp in range(1, num_channels +1):
                                    if(cp!=ch):
                                        Exp.append(Not(DT[fl][pkt][s][r][cp][ts]))
                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp))) 
                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp))))
                                                         
                            
### Same packet can't be scheduled in different channel at same time along ST
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            for s in secondary_path[fl - 1][path - 1]:
                for r in secondary_path[fl - 1][path - 1]:
                    if(connected_s[s][r]==1):
                        for ch in range(1, num_channels +1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl-1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    Exp=[]
                                    for cp in range(1, num_channels +1):
                                        if(cp!=ch):
                                            Exp.append(Not(ST[fl][pkt][path][s][r][cp][ts]))
                                    slv.add(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp)))  
                                    #print(str(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp))))

### Same packet can't be scheduled multiple time between the same sender and reciver along DT
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
       for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r]==1):
                    for ch in range(1, num_channels +1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl-1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                Exp=[]
                                for cp in range(1, num_channels +1):
                                    for tp in range(1, T + 1):
                                        if(t1 <= tp <= t2):
                                            if(tp!=ts):
                                                Exp.append(Not(DT[fl][pkt][s][r][cp][tp]))
                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp)))
                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp))))                          
                            
### Same packet can't be scheduled multiple time between the same sender and reciver along ST
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            for s in secondary_path[fl - 1][path - 1]:
                for r in secondary_path[fl - 1][path - 1]:
                    if(connected_s[s][r]==1):
                        for ch in range(1, num_channels +1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl-1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    Exp=[]
                                    for cp in range(1, num_channels +1):
                                        for tp in range(1, T + 1):
                                            if(t1 <= tp <= t2):
                                                if(tp!=ts):
                                                    Exp.append(Not(ST[fl][pkt][path][s][r][cp][tp]))
                                    slv.add(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp))) 
                                    #print(str(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp))))

#### Same packet from different secondary paths can't be scheduled at same time, if both the sender and the reciver are same (irrespective of channel)
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            for s in secondary_path[fl - 1][path - 1]:
                for r in secondary_path[fl - 1][path - 1]:
                    if(connected_s[s][r]==1):
                        for ch in range(1, num_channels +1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl-1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    Exp=[]
                                    for pthp in range(1, len(flow_path[fl - 1])):
                                        if(pthp!=path):
                                            for cp in range(1, num_channels +1):
                                                Exp.append(Not(ST[fl][pkt][pthp][s][r][cp][ts]))
                                    slv.add(Implies(ST[fl][pkt][path][s][r][ch][ts], And(Exp))) 
####***********************************************************************************************************************************####

###### Time Constraint for Dedicated links
#### Can't be schedule a transmission from the sender at same time slot, when it is talking with dedicated node (here, sender(s) to receiver (r))
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                for fp in range(1, num_flows + 1):
                                    if(fp != fl):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for cp in range(1, num_channels + 1):        
                                                Exp1 = []
                                                for sp in flow_path[fp - 1]:
                                                    for rp in flow_path[fp - 1]:
                                                        if(connected_p[sp][rp]==1):
                                                            if(sp==s):
                                                                Exp1.append(Not(DT[fp][pp][sp][rp][cp][ts]))
                                                Exp2 =[]
                                                for path in range(1, len(flow_path[fp - 1])):
                                                    for sp in secondary_path[fp - 1][path - 1]:
                                                        for rp in secondary_path[fp - 1][path - 1]:
                                                            if(connected_s[sp][rp]==1):
                                                                if(sp==s):
                                                                    Exp2.append(Not(ST[fp][pp][path][sp][rp][cp][ts]))
                                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1),And(Exp2))))
                                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1),And(Exp2)))))

## Can't be schedule a transmission to the sender at same time slot, when it is talking with dedicated node (here, s to r)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                for fp in range(1, num_flows + 1):
                                    if(fp != fl):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for cp in range(1, num_channels + 1):
                                                Exp1 = []
                                                for sp in flow_path[fp - 1]:
                                                    for rp in flow_path[fp - 1]:
                                                        if(connected_p[sp][rp]==1):
                                                            if(rp==s):
                                                                Exp1.append(Not(DT[fp][pp][sp][rp][cp][ts]))
                                                Exp2 = []
                                                for path in range(1, len(flow_path[fp - 1])):
                                                    for sp in secondary_path[fp - 1][path - 1]:
                                                        for rp in secondary_path[fp - 1][path - 1]:
                                                            if(connected_s[sp][rp]==1):
                                                                if(rp==s):
                                                                    Exp2.append(Not(ST[fp][pp][path][sp][rp][cp][ts]))
                                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1), And(Exp2))))
                                                   
## Can't be schedule a transmission from the receiver at same time slot, when it is talking with dedicated node (here, s to r)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                for fp in range(1, num_flows + 1):
                                    if(fp != fl):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for cp in range(1, num_channels + 1):
                                                Exp1 = []
                                                for sp in flow_path[fp-1]:
                                                    for rp in flow_path[fp - 1]:
                                                        if(connected_p[sp][rp]==1):
                                                            if(sp == r):
                                                                Exp1.append(Not(DT[fp][pp][sp][rp][cp][ts]))
                                                Exp2 = []
                                                for path in range(1, len(flow_path[fp - 1])):
                                                    for sp in secondary_path[fp - 1][path - 1]:
                                                        for rp in secondary_path[fp - 1][path - 1]:
                                                            if(connected_s[sp][rp]==1):
                                                                if(sp==r):
                                                                    Exp2.append(Not(ST[fp][pp][path][sp][rp][cp][ts]))
                                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1), And(Exp2))))
                                                                                                           
## Can't be schedule a transmission to the receiver at same time slot when it is talking with dedicated one (here, s to r)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1): 
        for s in flow_path[fl - 1]:
            for r in flow_path[fl - 1]:
                if(connected_p[s][r] == 1):
                    for ch in range(1, num_channels + 1):
                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                        for ts in range(1, T + 1):
                            if(t1 <= ts <= t2):
                                for fp in range(1, num_flows + 1):
                                    if(fp != fl):
                                        for pp in range(1, pkt_per_flow[fp] + 1):
                                            for cp in range(1, num_channels + 1):
                                                Exp1 = []
                                                for sp in flow_path[fp - 1]:
                                                    for rp in flow_path[fp - 1]:
                                                        if(connected_p[sp][rp]==1):
                                                            if(rp==r):
                                                                Exp1.append(Not(DT[fp][pp][sp][rp][cp][ts]))
                                                Exp2 = []
                                                for path in range(1, len(flow_path[fp - 1])):
                                                    for sp in secondary_path[fp - 1][path - 1]:
                                                        for rp in secondary_path[fp - 1][path - 1]:
                                                            if(connected_s[sp][rp]==1):
                                                                if(rp==r):
                                                                    Exp2.append(Not(ST[fp][pp][path][sp][rp][cp][ts]))
                                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1),And(Exp2))))
                                                #print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(And(Exp1),And(Exp2)))))
###***********************************************************************************************************************************####

### Time Constraint for Shared Links
### Can't be schedule a transmission to/from the sender at same time slot, when it is talking with shared node (here, x to y)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1):
        for path in range(1, len(flow_path[fl - 1])):
            for x in secondary_path[fl - 1][path - 1]:  
                for y in secondary_path[fl - 1][path - 1]:
                    if(connected_s[x][y] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    for fp in range(1, num_flows + 1):
                                        if (fp != fl):
                                            for pp in range(1,  pkt_per_flow[fp] + 1):
                                                for cp in range(1, num_channels + 1):
                                                    Exp1 = []
                                                    for xp in flow_path[fp - 1]:
                                                        for yp in flow_path[fp - 1]:
                                                            if(connected_p[xp][yp]==1):
                                                                if(yp==x):
                                                                    Exp1.append(Not(DT[fp][pp][xp][yp][cp][ts])) 
                                                    Exp2 = [] 
                                                    for xp in flow_path[fp - 1]:
                                                        for yp in flow_path[fp - 1]:
                                                            if(connected_p[xp][yp]==1):
                                                                if(xp==x):
                                                                    Exp2.append(Not(DT[fp][pp][xp][yp][cp][ts]))
                                                    slv.add(Implies(ST[fl][pkt][path][x][y][ch][ts], And(And(Exp1), And(Exp2))))
                                                    
#### Can't be schedule a transmission from/to the receiver at same time slot, when it is talking with shared node (here, x to y)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1):
        for path in range(1, len(flow_path[fl - 1])):
            for x in secondary_path[fl - 1][path - 1]:  
                for y in secondary_path[fl - 1][path - 1]:
                    if(connected_s[x][y] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    for fp in range(1, num_flows + 1):
                                        if (fp != fl):
                                            for pp in range(1,  pkt_per_flow[fp] + 1):
                                                for cp in range(1, num_channels + 1):
                                                    Exp1 = []
                                                    for xp in flow_path[fp - 1]:
                                                        for yp in flow_path[fp - 1]:
                                                            if(connected_p[xp][yp]==1):
                                                                if(xp==y):
                                                                    Exp1.append(Not(DT[fp][pp][xp][yp][cp][ts])) 
                                                    Exp2 = []
                                                    for xp in flow_path[fp - 1]:
                                                        for yp in flow_path[fp - 1]:
                                                            if(connected_p[xp][yp]==1):
                                                                if(yp==y):
                                                                    Exp2.append(Not(DT[fp][pp][xp][yp][cp][ts]))
                                                    slv.add(Implies(ST[fl][pkt][path][x][y][ch][ts], And(And(Exp1),And(Exp2))))
                                                    #print(str(Implies(ST[fl][pkt][path][x][y][ch][ts], And(And(Exp1),And(Exp2)))))

#### Can't be schedule a transmission to/from the sender at same time slot, when it is talking with shared node (here, x to y)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1):
        for path in range(1, len(flow_path[fl-1])):
            for x in secondary_path[fl-1][path-1]: 
                for y in secondary_path[fl-1][path-1]: 
                    if(connected_s[x][y] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    for fp in range(1, num_flows + 1):
                                        if (fp != fl):
                                            for pp in range(1,  pkt_per_flow[fp] + 1):
                                                for cp in range(1, num_channels + 1):
                                                    Exp1 = []
                                                    for pthp in range(1, len(flow_path[fp - 1])):
                                                        for xp in secondary_path[fp - 1][pthp - 1]:
                                                            for yp in secondary_path[fp - 1][pthp - 1]:
                                                                if(connected_s[xp][yp]==1):
                                                                    if(yp==x):
                                                                        Exp1.append(Not(ST[fp][pp][pthp][xp][yp][cp][ts])) 
                                                    slv.add(Implies(ST[fl][pkt][path][x][y][ch][ts], And(Exp1)))
                                                    Exp2 = []
                                                    for pthp in range(1, len(flow_path[fp - 1])):
                                                        for xp in secondary_path[fp - 1][pthp - 1]:
                                                            for yp in secondary_path[fp - 1][pthp - 1]:
                                                                if(connected_s[xp][yp]==1):
                                                                    if(xp==x):
                                                                        Exp2.append(Not(ST[fp][pp][pthp][xp][yp][cp][ts]))
                                                    slv.add(Implies(ST[fl][pkt][path][x][y][ch][ts], And(And(Exp1),And(Exp2))))
                                                    
#### Can't be schedule a transmission from the receiver at same time slot, when it is talking with shared one (here, x to y)
for fl in range(1, num_flows + 1):
    for pkt in range(1, pkt_per_flow[fl] + 1):
        for path in range(1, len(flow_path[fl-1])):
            for x in secondary_path[fl-1][path-1]:
                for y in secondary_path[fl-1][path-1]:
                    if(connected_s[x][y] == 1):
                        for ch in range(1, num_channels + 1):
                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
                            for ts in range(1, T + 1):
                                if(t1 <= ts <= t2):
                                    for fp in range(1, num_flows + 1):
                                        if (fp != fl):
                                            for pp in range(1,  pkt_per_flow[fp] + 1):
                                                for cp in range(1, num_channels + 1):
                                                    Exp1 = []
                                                    for pthp in range(1, len(flow_path[fp - 1])):
                                                        for xp in secondary_path[fp - 1][pthp - 1]:
                                                            for yp in secondary_path[fp - 1][pthp - 1]:
                                                                if(connected_s[xp][yp]==1):
                                                                    if(xp==y):
                                                                        Exp1.append(Not(ST[fp][pp][pthp][xp][yp][cp][ts])) 
                                                    slv.add(Implies(ST[fl][pkt][path][x][y][ch][ts], And(Exp1)))
                                                    

####***********************************************************************************************************************************####

####### Packet At Dedicated Nodes (PADN)
PADN = [[[[Bool('padn_%s_%s_%s_%s'%(fl,pkt,u,ts)) for ts in range(0, T+1)] for u in range(0, num_nodes + 1)] for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

####### Packet At Shared Nodes (PASN)
PASN = [[[[[Bool('pasn_%s_%s_%s_%s_%s'%(fl,pkt,path,u,ts)) for ts in range(0, T+1)] for u in range(0, num_nodes + 1)] for path in range(0, len(flow_path[fl - 1]))] for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

##### Packet Generation at source
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] + 1):
        src = flow_path[fl - 1][0]                 # src is source node
        ts = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
        slv.add(PADN[fl][pkt][src][ts])
            
#### Packet at dedicated path on different time
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for v in flow_path[fl-1]:
            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
            t2 = t1 + flow_period_deadline[fl-1][3] - 1
            for ts in range(1, T +1):
                if(t1 < ts <= t2):
                    Exp = []
                    for u in flow_path[fl-1]:
                        if((u!=v) and (connected_p[u][v]==1)):
                            for ch in range(1, num_channels + 1):
                                Exp.append(And(PADN[fl][pkt][u][ts-1], DT[fl][pkt][u][v][ch][ts-1]))
                    slv.add(Implies(PADN[fl][pkt][v][ts], Or(PADN[fl][pkt][v][ts-1], Or(Exp))))

#### Duplicate packet at each primary node
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] + 1):
        for u in flow_path[fl-1][:-1]: 
            for path in range(1, len(flow_path[fl - 1])):
                y =  secondary_path[fl - 1][path - 1][0]
                if(y == u):
                    t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
                    t2 = t1 + flow_period_deadline[fl-1][3] - 1
                    for ts in range(1, T +1): 
                        if(t1 <= ts <= t2):
                            slv.add(Implies(PADN[fl][pkt][u][ts], PASN[fl][pkt][path][y][ts]))
                            #slv.add(PktAtSrc_S[fl][pkt][path])
                                                                               
##### Duplicate packet at each primary node
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        for u in flow_path[fl-1][:-1]: 
#            for path in range(1, len(flow_path[fl - 1])):
#                for y in secondary_path[fl - 1][path - 1]:
#                    if(y == u):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl-1][3] - 1
#                        for ts in range(1, T +1): 
#                            if(t1 < ts <= t2):
#                                slv.add(Implies(PADN[fl][pkt][u][ts], PASN[fl][pkt][path][y][ts]))
 
#### Packet at shared path on different time
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            print(flow_path[fl-1][path-1])
            connected_s[flow_path[fl-1][path-1]][flow_path[fl-1][path]]=0   ### break the path (connection) initially
            for y in secondary_path[fl - 1][path - 1]:
                t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
                t2 = t1 + flow_period_deadline[fl-1][3] - 1
                for ts in range(1, T +1):
                    if(t1 < ts <= t2):
                        Exp1 = []
                        for x in secondary_path[fl - 1][path - 1]:
                            if((x!=y) and (connected_s[x][y]==1)):
                                for ch in range(1, num_channels + 1):
                                    Exp1.append(And(PASN[fl][pkt][path][x][ts-1], ST[fl][pkt][path][x][y][ch][ts-1]))
                        slv.add(Implies(PASN[fl][pkt][path][y][ts], Or(PASN[fl][pkt][path][y][ts-1], Or(Exp1))))  
            connected_s[flow_path[fl-1][path-1]][flow_path[fl-1][path]]=1   ### fix the path (connection) later on for other 
                                     
##### Packet at shared path on different time
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] +1):
#        for path in range(1, len(flow_path[fl - 1])):
#            for y in secondary_path[fl - 1][path - 1]:
#                t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
#                t2 = t1 + flow_period_deadline[fl-1][3] - 1
#                for ts in range(1, T +1):
#                    if(t1 <= ts <= t2):
#                        Exp1 = []
#                        for x in secondary_path[fl - 1][path - 1]:
#                            if((x!=y) and (connected_s[x][y]==1)):
#                                for ch in range(1, num_channels + 1):
#                                    Exp1.append(And(PASN[fl][pkt][path][x][ts-1], ST[fl][pkt][path][x][y][ch][ts-1]))
#                        slv.add(Implies(PASN[fl][pkt][path][y][ts], Or(PASN[fl][pkt][path][y][ts-1], Or(Exp1))))


### The packet should be at any of the dedicated node at certain time slot                                        
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
        t2 = t1 + flow_period_deadline[fl-1][3] - 1
        for ts in range(1, T +1):
            if(t1 <= ts <= t2):
                Exp=[]
                for u in flow_path[fl-1]:
                    Exp.append(PADN[fl][pkt][u][ts])
                slv.add(Or(Exp))
               

### The packet should be at any of the shared node at certain time slot
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
            t2 = t1 + flow_period_deadline[fl-1][3] - 1
            for ts in range(1, T +1):
                if(t1 <= ts <= t2):
                    Exp=[]
                    for x in secondary_path[fl - 1][path - 1]:
                        Exp.append(PASN[fl][pkt][path][x][ts])
                    slv.add(Or(Exp))

##### same packet can't be at different nodes on same time along primary path
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for v in flow_path[fl-1]:
            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
            t2 = t1 + flow_period_deadline[fl-1][3] - 1
            for ts in range(1, T +1):
                if(t1 <= ts <= t2):
                    Exp1=[]
                    for u in flow_path[fl-1]:
                        if(u!=v):
                            Exp1.append(Not(PADN[fl][pkt][u][ts]))
                    slv.add(Implies(PADN[fl][pkt][v][ts], And(Exp1)))

##### same packet can't be at different nodes on same time along secondry path
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            for y in secondary_path[fl - 1][path - 1]:
                t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
                t2 = t1 + flow_period_deadline[fl-1][3] - 1
                for ts in range(1, T + 1):
                    if(t1 <= ts <= t2):
                        Exp2=[]
                        for x in secondary_path[fl - 1][path - 1]:
                            if(x!=y):
                                Exp2.append(Not(PASN[fl][pkt][path][x][ts]))
                        slv.add(Implies(PASN[fl][pkt][path][y][ts], And(Exp2)))
                        #print(str(Implies(PASN[fl][pkt][path][y][ts], And(Exp2))))
#### The packet should be at any of the dedicated node at certain time slot                                        
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] +1):
#        #for v in flow_path[fl-1]:
#        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#        t2 = t1 + flow_period_deadline[fl-1][3] - 1
#        for ts in range(1, T +1):
#            if(t1 <= ts <= t2):
#                Exp=[]
#                for u in flow_path[fl-1]:
#                    Exp.append(PADN[fl][pkt][u][ts])
#                slv.add(Or(Exp))
               

#### The packet should be at any of the shared node at certain time slot
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] +1):
#        for path in range(1, len(flow_path[fl - 1])):
#            #for y in secondary_path[fl - 1][path - 1]:
#            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#            t2 = t1 + flow_period_deadline[fl-1][3] - 1
#            for ts in range(1, T +1):
#                if(t1 <= ts <= t2):
#                    Exp=[]
#                    for x in secondary_path[fl - 1][path - 1]:
#                        Exp.append(PASN[fl][pkt][path][x][ts])
#                    slv.add(Or(Exp))

###### same packet can't be at different nodes on same time along primary path
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] +1):
#        for v in flow_path[fl-1]:
#            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
#            t2 = t1 + flow_period_deadline[fl-1][3] - 1
#            for ts in range(1, T +1):
#                if(t1 <= ts <= t2):
#                    Exp1=[]
#                    for u in flow_path[fl-1]:
#                        if(u!=v):
#                            Exp1.append(Not(PADN[fl][pkt][u][ts]))
#                    slv.add(Implies(PADN[fl][pkt][v][ts], And(Exp1)))

###### same packet can't be at different nodes on same time along secondry path
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] +1):
#        for path in range(1, len(flow_path[fl - 1])):
#            for y in secondary_path[fl - 1][path - 1]:
#                t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl -1][2] * (pkt - 1)
#                t2 = t1 + flow_period_deadline[fl-1][3] - 1
#                for ts in range(1, T + 1):
#                    if(t1 <= ts <= t2):
#                        Exp2=[]
#                        for x in secondary_path[fl - 1][path - 1]:
#                            if(x!=y):
#                                Exp2.append(Not(PASN[fl][pkt][path][x][ts]))
#                        slv.add(Implies(PASN[fl][pkt][path][y][ts], And(Exp2)))
#                        print(str(Implies(PASN[fl][pkt][path][y][ts], And(Exp2))))
                       
####***********************************************************************************************************************************####


######## Packet at Source
##PktAtSrc = [[Bool('pas_%s_%s'%(fl,pkt)) for pkt in range(0, pkt_per_flow[fl] +
##1)] for fl in range(0, num_flows + 1)]
##PktAtSrc_real = [[Real('pas_int_%s_%s' %(fl,pkt)) for pkt in range(0,
##pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]
##for fl in range(1, num_flows + 1):
##    for pkt in range (1, pkt_per_flow[fl] + 1):
##        src = flow_path[fl - 1][0] # src is source node
##        Exp=[]
##        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2]
##        * (pkt - 1)
##        t2 = t1 + flow_period_deadline[fl-1][3] - 1
##        for ts in range(1, T +1):
##            if(t1 <= ts <= t2):
##                Exp.append(PktAtNode[fl][pkt][src][ts])
##        slv.add(Implies(PktAtSrc[fl][pkt], Or(Exp)))

##BExp1=[]
##for fl in range(1, num_flows + 1):
##    for pkt in range (1, pkt_per_flow[fl] + 1):
##        BExp1.append(And(Implies(PktAtSrc[fl][pkt], PktAtSrc_real[fl][pkt] ==
##        1), Implies(PktAtSrc [fl][pkt] == False, PktAtSrc_real[fl][pkt] ==
##        1)))
##slv.add(And(BExp1))

####### Packet At Destination along Dedicated path (PktAtDst_D)
PktAtDst_D = [[Bool('padd_%s_%s'%(fl,pkt)) for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

#PktAtDst_real = [[Real('pad_int_%s_%s' %(fl,pkt)) for pkt in range(0,
#pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] + 1):
        dst = flow_path[fl-1][-1]
        Exp1=[]
        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
        t2 = t1 + flow_period_deadline[fl-1][3] - 1
        for ts in range(1, T +1):
            if(t1 <= ts <= t2):
                Exp1.append(PADN[fl][pkt][dst][ts])
        slv.add(Implies(PktAtDst_D[fl][pkt], Or(Exp1)))
         
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        dst = flow_path[fl-1][-1]
#        Exp1=[]
#        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#        t2 = t1 + flow_period_deadline[fl-1][3] - 1
#        for ts in range(1, T +1):
#            if(t1 <= ts <= t2):
#                Exp1.append(PADN[fl][pkt][dst][ts])
#        slv.add(Implies(PktAtDst_D[fl][pkt], Or(Exp1)))

ExpD =[]
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        ExpD.append(PktAtDst_D[fl][pkt])
slv.add(And(ExpD))


####### Packet At Destination along Shared path (PktAtDst_D)
PktAtDst_S = [[[Bool('pads_%s_%s_%s'%(fl,pkt,path)) for path in range(0, len(flow_path[fl - 1]))] for pkt in range(0, pkt_per_flow[fl] + 1)] for fl in range(0, num_flows + 1)]

for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] + 1):
        for path in range(1, len(flow_path[fl - 1])):
            dst = flow_path[fl-1][-1]
            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
            t2 = t1 + flow_period_deadline[fl-1][3] - 1
            Exp2=[]
            for ts in range(1, T +1):
                if(t1 <= ts <= t2):
                    Exp2.append(PASN[fl][pkt][path][dst][ts])
            slv.add(Implies(PktAtDst_S[fl][pkt][path], Or(Exp2)))

#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        for path in range(1, len(flow_path[fl - 1])):
#            dst = flow_path[fl-1][-1]
#            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#            t2 = t1 + flow_period_deadline[fl-1][3] - 1
#            Exp2=[]
#            for ts in range(1, T +1):
#                if(t1 <= ts <= t2):
#                    Exp2.append(PASN[fl][pkt][path][dst][ts])
#            slv.add(Implies(PktAtDst_S[fl][pkt][path], Or(Exp2))) 

ExpS=[]
for fl in range(1, num_flows + 1):
    for pkt in range (1, pkt_per_flow[fl] +1):
        for path in range(1, len(flow_path[fl - 1])):
            ExpS.append(PktAtDst_S[fl][pkt][path])
slv.add(And(ExpS))


#BExp2=[]
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        BExp2.append(And(Implies(PktAtDst [fl][pkt], PktAtDst_real[fl][pkt] ==
#        1), Implies(PktAtDst [fl][pkt] == False, PktAtDst_real[fl][pkt] ==
#        1)))
#slv.add(And(BExp2))

#RExp1 = []
#RExp2 = []
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        RExp1.append(PktAtSrc_real[fl][pkt])
#        RExp2.append(PktAtDst_real[fl][pkt])
#slv.add((Sum(RExp2)/Sum(RExp1) * 100) >= 100)

##################################################
##################################################
### Solve the formal model
f_write_name = 'Newop2.txt'
f_write = open(f_write_name, 'w')
print ('Execution starts')

while True:
    status = slv.check()
    f_write.write('\n' + str(status))

    if(str(status) == 'sat'):
        print(status)
        M = slv.model()
        f_write.write('\n')
        #f_write.write('\nPacket at node: FlowType-PktNumber-Node-Time\n')
        #for fl in range (1, num_flows + 1):
        #    for pkt in range(1, pkt_per_flow[fl] + 1):
        #        for a in flow_path[fl-1]:
        #            for ts in range(1, T + 1):
        #                if(str(M[PAN[fl][pkt][a][ts]])=='True'):
        #                    f_write.write(str(fl) + '-' + str(pkt) + '-' +
        #                    str(a) + '-'+ str(ts) + ':' +
        #                    str(M[PAN[fl][pkt][a][ts]]) + '\n')

        f_write.write('\n### Packet at dedicated node:\nFlowType  PktNumber   Node   Time\n')
        for fl in range (1, num_flows + 1):
            for pkt in range(1, pkt_per_flow[fl] + 1):
                for a in flow_path[fl-1]:
                    for ts in range(1, T + 1):
                        if(str(M[PADN[fl][pkt][a][ts]])=='True'):
                            f_write.write('\t' + str(fl) + '\t\t ' + str(pkt) + '\t\t   ' +
                            str(a) + '\t   '+ str(ts) + '\n')

        f_write.write('\n### Packet at shared node: \nFlowType  PktNumber   Path   Node    Time\n')
        for fl in range (1, num_flows + 1):
            for pkt in range(1, pkt_per_flow[fl] + 1):
                for path in range(1, len(flow_path[fl - 1])):
                    for a in secondary_path[fl-1][path - 1]:
                        for ts in range(1, T + 1):
                            if(str(M[PASN[fl][pkt][path][a][ts]])=='True'):
                                f_write.write('\t' + str(fl) + '\t\t ' + str(pkt) + '\t\t   ' + str(path) + '\t   ' +
                                str(a) + '\t   ' + str(ts) + '\n')

        f_write.write('\n###Dedicated Transmission:\nFlowType  PktNumber  SenderNode  RecvrNode  Channel  Time\n')
        for fl in range(1, num_flows + 1):
            for pkt in range(1, pkt_per_flow[fl] + 1):
                for a in flow_path[fl - 1]:
                    for b in flow_path[fl - 1]:
                        for ch in range(1, num_channels + 1):
                            for ts in range(1, T + 1):
                                if(str(M[DT[fl][pkt][a][b][ch][ts]]) == 'True'):
                                    f_write.write('\t' + str(fl) + '\t\t ' + str(pkt) + '\t\t     ' + str(a) + '\t\t     ' + str(b) + '\t       ' + str(ch) + '\t  ' + str(ts) + '\n')

        f_write.write('\n###Shared Transmission:\nFlowType  PktNumber  Path  SenderNode  RecvrNode  Channel  Time\n')
        for fl in range(1, num_flows + 1):
            for pkt in range(1, pkt_per_flow[fl] + 1):
                for path in range(1, len(flow_path[fl - 1])):
                    for a in secondary_path[fl - 1][path - 1]:
                        for b in secondary_path[fl - 1][path - 1]:
                            for ch in range(1, num_channels + 1):
                                for ts in range(1, T + 1):
                                    if(str(M[ST[fl][pkt][path][a][b][ch][ts]]) == 'True'):
                                        f_write.write('\t '+ str(fl) + '\t\t  ' + str(pkt) + '\t\t  ' + str(path) + '\t\t   ' + str(a) + '\t      ' + str(b) + '\t\t     ' + str(ch) + '\t     ' + str(ts) + '\n')

        #f_write.write('\nPacket at src: FlowType-PktNumber\n')
        #for fl in range(1, num_flows + 1):
        #    for pkt in range(1, pkt_per_flow[fl] +1):
        #        if(str(M[PktAtSrc[fl][pkt]])=='True'):
        #            f_write.write(str(fl) + '-' + str(pkt) + ':'+
        #            str(M[PktAtSrc[fl][pkt]]) + '\n')

        #f_write.write('\nPacket at dst: FlowType-PktNumber\n')
        #for fl in range(1, num_flows + 1):
        #    for pkt in range(1, pkt_per_flow[fl] +1):
        #        if(str(M[PktAtDst[fl][pkt]])=='True'):
        #            f_write.write(str(fl) + '-' + str(pkt) + ':'+
        #            str(M[PktAtDst[fl][pkt]]) + '\n')
    else:
        f_write.write('\n did not meet requirements\n')
    break
    
f_write.write('\n\n*****************************************\n\n')

##################### End #######################

####***********************************************************************************************************************************####


##### Relation between DT and ST of the same packet of the same flow                   
#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[fl] + 1):
#        for s in flow_path[fl - 1]:
#            for r in flow_path[fl - 1]:
#                if(connected_p[s][r] == 1):
#                    for ch in range(1, num_channels + 1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                Exp1 = []
#                                for path in range(1, len(flow_path[fl - 1])):
#                                    for sp in secondary_path[fl - 1][path - 1]:
#                                        for rp in secondary_path[fl - 1][path - 1]: 
#                                            if(connected_s[sp][rp]==1):
#                                                if(rp==s):
#                                                    for cp in range(1, num_channels + 1):
#                                                        Exp1.append(Not(ST[fl][pkt][path][sp][rp][cp][ts]))
#                                slv.add(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1)))
#                                print(str(Implies(DT[fl][pkt][s][r][ch][ts], And(Exp1))))




### Channel Constraints for Dedicated Links
#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[fl] + 1):
#        for u in flow_path[fl - 1]:
#            for v in flow_path[fl - 1]: 
#                if(connected[u][v] == 1):
#                    for ch in range(1, num_channels + 1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                if(u == flow_path[fl - 1][-1]):
#                                    slv.add(Not(DT[fl][pkt][u][v][ch][ts]))
#                                else:
#                                    Exp1 = []
#                                    for fp in range(1, num_flows + 1):
#                                        #if(fp != fl):
#                                            for pp in range(1, pkt_per_flow[fp] + 1):
#                                                for up in flow_path[fp - 1]:
#                                                    for vp in flow_path[fp - 1]: 
#                                                        if((up != u) or (vp != v)):
#                                                            Exp1.append(Not(DT[fp][pp][up][vp][ch][ts]))
#                                    Exp2 = []
#                                    for fp in range(1, num_flows + 1):
#                                        #if(fp != fl):
#                                            for pp in range(1, pkt_per_flow[fp] + 1):
#                                                    for path in range(1, len(flow_path[fp - 1])):
#                                                        for up in secondary_path[fp - 1][path - 1]:
#                                                            for vp in secondary_path[fp - 1][path - 1]:
#                                                                if((up != u) or (vp != v)):
#                                                                    Exp2.append(Not(ST[fp][pp][up][vp][ch][ts]))
#                                    slv.add(Implies(DT[fl][pkt][u][v][ch][ts], Or(And(Exp1), And(Exp2))))

###### Channel Constraints for Shared Links
#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[fl] + 1):
#        for path in range(1, len(flow_path[fp - 1])):
#            for u in secondary_path[fp - 1][path - 1]:
#                for v in secondary_path[fp - 1][path - 1]:
#                    if(connected[u][v] == 1):
#                        for ch in range(1, num_channels + 1):
#                            t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                            t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                            for ts in range(1, T + 1):
#                                if(t1 <= ts <= t2):
#                                    if(u == flow_path[fl - 1][-1]):
#                                        slv.add(Not(ST[fl][pkt][u][v][ch][ts]))
#                                    else:
#                                        Exp1 = []
#                                        for fp in range(1, num_flows + 1):
#                                            if(fp != fl):
#                                                for pp in range(1, pkt_per_flow[fp] + 1):
#                                                    for up in flow_path[fp - 1]:
#                                                        for vp in flow_path[fp - 1]: 
#                                                            if((up != u) or (vp != v)):
#                                                                Exp1.append(Not(DT[fp][pp][up][vp][ch][ts]))
#                                        Exp2 = []
#                                        for fp in range(1, num_flows + 1):
#                                            if(fp != fl):
#                                                for pp in range(1, pkt_per_flow[fp] + 1):
#                                                    for path in range(1, len(flow_path[fp - 1])):
#                                                        for up in secondary_path[fp - 1][path - 1]:
#                                                            for vp in secondary_path[fp - 1][path - 1]:
#                                                                if((up != u) or (vp != v)):
#                                                                    Exp2.append(Not(ST[fp][pp][up][vp][ch][ts]))
#                                        slv.add(Implies(ST[fl][pkt][u][v][ch][ts], Or(And(Exp1), And(Exp2))))

#### different packets (with same src and dst) can't be scheduled at same time
#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[f] + 1):
#        for u in flow_path[fl - 1]:
#            for v in flow_path[fl - 1]:
#                if(connected[u][v] == 1):
#                    for ch in range(1, num_channels + 1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                for fl in range(1, num_flows + 1):
#                                    for pp in range(1, pkt_per_flow[f] + 1):
#                                        for cp in range(1, num_channels):
#                                            Exp = []
#                                            for tp in range(1, T+1):
#                                                if(tp!=ts):
#                                                    Exp.append(Not(DT[fp][pp][u][v][cp][tp]))
#                                            slv.add(Implies(DT[fl][pkt][u][v][ch][ts], And(Exp)))

#### different packets (with same src and dst) can't be scheduled at same time
#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[f] + 1):
#        for u in flow_path[fl - 1]:
#            for v in flow_path[fl - 1]:
#                if(connected[u][v] == 1):
#                    for ch in range(1, num_channels + 1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                Exp = []
#                                for fp in range(1, num_flows + 1):
#                                    if(fp != f):
#                                        for cp in range(1, num_channels):
#                                            Exp.append(Not(DT[fp][pkt][u][v][cp][ts]))
#                                slv.add(Implies(DT[fl][pkt][u][v][ch][ts], And(Exp)))


#### Packet can't be scheduled in different channel at same time
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[f] +1):
#        for u in flow_path[fl-1]:
#            for v in flow_path[fl-1]:
#                if(connected[u][v]==1):
#                    for ch in range(1, num_channels +1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl-1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                Exp=[]
#                                for cp in range(1, num_channels +1):
#                                    if(cp!=ch):
#                                        Exp.append(Not(DT[fl][pkt][u][v][cp][ts]))
#                                    slv.add(Implies(Scheduled[fl][pkt][u][v][ch][ts], And(Exp)))

#for fl in range(1, num_flows + 1):
#    for pkt in range(1, pkt_per_flow[fl] + 1): 
#        for s in flow_path[fl - 1]:
#            for r in flow_path[fl - 1]:
#                if(connected[s][r] == 1):
#                    #for pth in range(1, len(flow_path[fl-1])-1):
#                    for ch in range(1, num_channels + 1):
#                        t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                        t2 = t1 + flow_period_deadline[fl - 1][3] - 1
#                        for ts in range(1, T + 1):
#                            if(t1 <= ts <= t2):
#                                for cp in range(1, num_channels + 1):
#                                    for path in range(1, len(flow_path[fl - 1])):
#                                        for sp in secondary_path[fl - 1][path - 1]:
#                                            if(sp != r):
#                                                for tp in range(ts + 1, t2):
#                                                    slv.add(Implies(DT[fl][pkt][s][r][ch][ts], ST[fl][pkt][s][sp][cp][tp]))

##*************************************************************************************************************************##

################################################
#for fl in range(1, num_flows + 1):
#    for pkt in range (1, pkt_per_flow[fl] + 1):
#        for dst in range(1, num_nodes +1):         
#            if(flow_path[fl-1][-1]==dst):
#                Exp=[]
#                t1 = flow_period_deadline[fl - 1][1] + flow_period_deadline[fl - 1][2] * (pkt - 1)
#                t2 = t1 + flow_period_deadline[fl-1][3] - 1
#                for ts in range(1, T +1):
#                    if(t1 <= ts <= t2):
#                        Exp.append(PktAtNode[fl][pkt][dst][ts])
#                slv.add(Implies(PktAtDst[fl][pkt], Or(Exp)))
            #slv.add(Implies(Or(Exp), PktAtDst[p]))

## Packets released at each flow on different time slot 
#packet_generate_t = [[x for x in y if x is not None] for y in zip_longest(*packet_generate)]
#print(packet_generate_t)
##number = 0
#prt = []
#for t in range(1, T + 1):
#    if(sum(packet_generate_t[t]) > 0):
#        ls3 =[t]
#        for f in range(1, num_flows + 1):
#            if(packet_generate_t[t][f] == 1):       
#                #number = number + 1
#                #ls2 =[number]
#                ls1 = [f]
#                ls2 = [flow_path[f-1][0]]
#                deadline_slot = (t-1) + flow_period_deadline[f-1][-1]
#                ls4 = [deadline_slot]
#                ls = ls1 + ls2 +ls3 + ls4
#                prt.append(ls)

#prt = sorted(prt, key = lambda x: (x[0], x[-1]))

#print(prt)



#for p in range(1, num_flows + 1):
#    for b in range(1, num_nodes+ 1):
#        for t in range(2, flow_period_deadline[p-1][-1] + 1):
#            Exp = []
#            for a in range(1, num_nodes + 1):
#                if((a!=b) and (connected[a][b] == 1)):
#                    #for m in range(1, num_channels + 1):
#                    Exp.append(PktAtNode[p][a][t-1])
#            slv.add(Implies(PktAtNode[p][b][t], Or(PktAtNode[p][b][t-1], Or(Exp))))


#for p in range(1, num_flows + 1):
#    for s in range(1, num_nodes + 1):
#        if(flow_path[p-1][0]==s):
#            for d in range(1, num_nodes +1): 
#                if(flow_path[p-1][1]==d):
#                    Exp=[]
#                    for t in range(2, flow_period_deadline[p-1][-1] + 1):
#                        Exp.append(PktAtNode[p][d][t])
#                    slv.add(Implies(PktAtNode[p][s][1], Or(Exp)))
#slv.add(Not(PktAtNode[1][2][3]))



### source and destination node of each flow 
#cnp=[]
#for f in range(1, num_flows + 1): 
#    ls1 = [f]
#    ls2 = [flow_path[f-1][0]]
#    ls3 = [flow_path[f-1][-1]]
#    ls = ls1 + ls2 + ls3
#    cnp.append(ls)
#print(cnp)



### hyper-period, T (i.e., LCM of the periods of flows) 
#list_periods = []
#for i in range(0, num_flows):
#    list_periods.append(int(flow_period_deadline[i][1]))  
#print(list_periods)
#lcm = list_periods[0]
#for j in list_periods[1:]:
#    lcm = int(lcm) *j /gcd(int(lcm), j)
#T = int(lcm)

## packet generation
#packet_generate = [[0 for t in range(0, T + 1)] for f in range(0, num_flows + 1)]

#for f in range(1, num_flows + 1):                       
#    starting_slot = random.randint(1, 2)
#    for t in range(1, T + 1):
#         if(t == starting_slot):
#            packet_generate[f][t] = 1            # Initilization of packet generation 

#for f in range(1, num_flows + 1):
#    for t in range(1, T + 1):
#        if(packet_generate[f][t] == 1):
#            while(t < T + 1):
#                t = flow_period_deadline[f-1][1] + t
#                if (t < T+ 1):
#                    packet_generate[f][t] = 1
#print(packet_generate)

### number of packets released no later than T
#total_packet = 0
#for f in range(1, num_flows + 1):
#    for t in range(1, T + 1):
#        if(packet_generate[f][t] == 1):
#            total_packet = total_packet + 1
#print(total_packet)

# Packets released at each flow on different time slot 
#packet_generate_t = [[x for x in y if x is not None] for y in zip_longest(*packet_generate)]
#print(packet_generate_t)
##number = 0
#prt = []
#for t in range(1, T + 1):
#    if(sum(packet_generate_t[t]) > 0):
#        ls1 =[t]
#        for f in range(1, num_flows + 1):
#            if(packet_generate_t[t][f] == 1):       
#                #number = number + 1
#                #ls2 =[number]
#                ls2 = [f]
#                deadline_slot = (t-1) + flow_period_deadline[f-1][2]
#                ls3 = [deadline_slot]
#                ls = ls2 + ls1 +ls3
#                prt.append(ls)
#print(prt)

#### Corresponding deadline of packets
#number = 0
#cdp=[]
#for t in range(1, T+1):
#    for f in range(1, num_flows + 1):
#        if(packet_generate_t[t][f] == 1 ):
#            number = number + 1 
#            ls1 = [number]
#            deadline_slot = (t-1) + flow_period_deadline[f-1][2]
#            ls2 = [deadline_slot]
#            ls= ls1 + ls2
#            cdp.append(ls)
#print(cdp)



#for p in range(1, num_flows + 1):
#    for b in range(1, num_nodes + 1):
#        if(flow_path[p-1][0]!=b):
#            for t in range(2, flow_period_deadline[p-1][-1] + 1):
#                Exp2 = []
#                for a in range(1, num_nodes + 1):
#                    if(a!=b):
#                        for m in range(1, num_channels +1):
#                            Exp2.append(Scheduled[p][a][b][m][t-1])
#                slv.add(Implies(PktAtNode[p][b][t], Or(PktAtNode[p][b][t-1], Or(Exp2))))
#            #slv.add(Implies(Or(PktAtNode[p][b][t-1], Or(Exp2)), PktAtNode[p][b][t]))
#print(PktAtNode)

#for p in range(1, num_flows + 1):
#    for s in range(1, num_nodes + 1):
#        if(flow_path[p-1][0]==s):
#            for d in range(1, num_nodes +1): 
#                if(flow_path[p-1][1]==d):
#                    for t in range(1, flow_period_deadline[p-1][-1] + 1):
#                        slv.add(Implies(PktAtNode[p][s][1], PktAtNode[p][d][t]))



#for p in range(1, num_flows + 1):
#    for a in range(1, num_nodes +1):
#        for b in range(1, num_nodes+ 1):
#            if(Link[a][b]==True):
#                for m in range(1, num_channels +1):
#                    for t in range(1, flow_period_deadline[p-1][-1] + 1):
#                        #if(t<=cdp[p-1][1]):
#                        Exp =[]
#                        for pp in range(1, num_flows + 1):
#                            if(pp!=p):
#                                for ap in range(1, num_nodes + 1):
#                                    for bp in range(1, num_nodes + 1): 
#                                        if((Link[ap][bp]==True) and (ap!=a) and (bp!=b)):
#                                            Exp.append(Not(Scheduled[pp][ap][bp][m][t]))
#                            slv.add(Implies(Scheduled[p][a][b][m][t], And(Exp)))

#slv.add(Scheduled[1][1][2][1][1])
##print(Scheduled)



#for p in range(1, num_flows + 1):
#    for b in range(1, num_nodes + 1):
#        if(flow_path[p-1][0]==b):
#            slv.add(PktAtNode[p][b][1])
#        else:
#            for t in range(2, flow_period_deadline[p-1][-1] + 1):
#                Exp1 = PktAtNode[p][b][t-1]
#                Exp2 = []
#                for a in range(1, num_nodes + 1):
#                    if(a!=b and Link[a][b]==True):
#                        for m in range(1, num_channels +1):
#                            #for t in range(2, T + 1):
#                            Exp2.append(Scheduled[p][a][b][m][t-1])
#                Exp = Or(Exp1, Or(Exp2))
#                slv.add(Implies(PktAtNode[p][b][t], Exp))



#PktAtDst = [[[Bool('pan_%s_%s_%s'%(p,a,t)) for t in range(0, 10+1)] for a in range(0, num_nodes+1)] for p in range(0, num_flows+1)]


#for p in range(1, num_flows + 1):
#    for x in range(1, num_nodes + 1):
#        for t in range(1, flow_period_deadline[p-1][-1] + 1):
#            Exprs = []
#            for y in range(1, num_nodes + 1):
#                if (x != y):
#                    Exprs.append(Not(PktAtNode[p][y][t]))
#            slv.add(Implies(PktAtNode[p][x][t], And(Exprs)))



### A channel can be unavailable 
#Channel_avail = [[False for b in range(0, num_nodes + 1)] for a in range(0, num_nodes + 1)]

#for t in range(1, hyper_periods + 1):
#    for ch in range(1, num_channels + 1):
#        slv.add(Channel_avail[t][ch])
##print(Channel_avail)

#### Weather or not a packet can be schedulable or not
#scheduled = [Bool('scheduled_%s' %p) for p in range(0, num_packets + 1)] 

#met_deadline = [False for p in range(0, num_packets + 1)]

#unscheduled_packets = []
#for t in range(1, hyper_periods + 1):
#    print(t)
#    if(len(a[t-1]) >= 2):
#        list_of_packets = []
#        list_of_deadlines = []
#        for i in range (1, len(a[t-1])):
#            list_of_packets.append(int(a[t-1][i]))
#            list_of_deadlines.append(Deadlines[int(a[t-1][i])])
#        #print(list_of_packets)
#        #print(list_of_deadlines)
#        released_packets = list(zip(list_of_packets, list_of_deadlines))
#        unscheduled_packets = unscheduled_packets + released_packets
#        for ch in range(1, num_channels + 1):   
#            sorted_packets_list = sorted(unscheduled_packets, key=lambda x: x[1])
#            print(sorted_packets_list) 
#            if(len(sorted_packets_list)> 0):
#                deadline = sorted_packets_list[0][1]
#                #print(sorted_packets_list[0][0])
#                if( (t <= deadline) and (deadline <= hyper_periods)):
#                    met_deadline[sorted_packets_list[0][0]] = True
#                    slv.add(Implies(And(met_deadline[sorted_packets_list[0][0]], Channel_avail[t][ch]),scheduled[sorted_packets_list[0][0]]))
#                    unscheduled_packets.remove(sorted_packets_list[0])
#                    print(unscheduled_packets)
#                else:
#                    for (x,y) in sorted_packets_list:
#                        if((t > y) or (y > hyper_periods)):
#                            slv.add(Not(scheduled[x]))
#                            unscheduled_packets.remove((x,y))
#                    if(len(unscheduled_packets)>0):
#                        met_deadline[unscheduled_packets[0][0]] = True
#                        slv.add(Implies(And(met_deadline[unscheduled_packets[0][0]], Channel_avail[t][ch]),scheduled[unscheduled_packets[0][0]]))
#                        unscheduled_packets.remove(unscheduled_packets[0])
#                        print(unscheduled_packets)
#            else:
#                break
#    else:
#        for ch in range(1, num_channels + 1):   
#        #ch = 0
#        #while(ch < num_channels):
#            sorted_packets_list = sorted(unscheduled_packets, key=lambda x: x[1])
#            print(sorted_packets_list) 
#            if(len(sorted_packets_list)> 0):
#                deadline = sorted_packets_list[0][1]
#                #print(sorted_packets_list[0][0])
#                if( (t <= deadline) and (deadline <= hyper_periods)):
#                    met_deadline[sorted_packets_list[0][0]] = True
#                    slv.add(Implies(And(met_deadline[sorted_packets_list[0][0]], Channel_avail[t][ch]),scheduled[sorted_packets_list[0][0]]))
#                    unscheduled_packets.remove(sorted_packets_list[0])
#                    #ch = ch + 1
#                    print(unscheduled_packets)
#                else:
#                    for (x,y) in sorted_packets_list:
#                        if((t > y) or (y > hyper_periods)):
#                            slv.add(Not(scheduled[x]))
#                            unscheduled_packets.remove((x,y))
#                    if(len(unscheduled_packets)>0):
#                        met_deadline[unscheduled_packets[0][0]] = True
#                        slv.add(Implies(And(met_deadline[unscheduled_packets[0][0] ], Channel_avail[t][ch]),scheduled[unscheduled_packets[0][0]]))
#                        unscheduled_packets.remove(unscheduled_packets[0])
#                        #ch = ch + 1
#                        print(unscheduled_packets)
#            else:
#                break   

#print(met_deadline)
#scheduled_real = [Real('scheduled_int_%s' % p) for p in range(0, num_packets + 1)]

#Exp1 = []
#for p in range(1, num_packets + 1):        
#    Exp1.append(And(Implies(scheduled[p], scheduled_real[p] == 1), Implies(scheduled[p] == False, scheduled_real[p] == 0)))
#slv.add(And(Exp1))

#Exp2 = []
#for p in range(1, num_packets + 1):
#    Exp2.append(scheduled_real[p])
#slv.add(((Sum(Exp2)/p) * 100) >= th )
 

###################################################
###################################################
#### Solve the formal model

##slv.push()

#f_write_name = 'Output.txt'
#f_write = open(f_write_name, 'a')
#status = slv.check()
##f_write.write(str(status))
##f_write.write('\n')
#print(status)

#while True:
#    status = slv.check()
#    f_write.write(str(status))
#    f_write.write('\n')
#    print(status)

#    if(str(status) == 'sat'):
#        m = slv.model()
#        f_write.write('\n Initilization\n')
#        for p in range(1, total_packet + 1):
#            for a in range(1, num_nodes+ 1):
#                for t in range(1, T + 1):
#                    if(str(m[PktAtNode[p][a][t]])=='True'):
#                        f_write.write(str(p) + '-' + str(a) + '-'+ str(t) + ':' + str(m[PktAtNode[p][a][t]]) + '\n')

#        f_write.write('\n Scheduled\n')
#        for p in range(1, total_packet + 1):
#            for a in range(1, num_nodes +1):
#                for b in range(1, num_nodes+ 1):
#                    for m in range(1, num_channels +1):
#                        for t in range(1, T + 1):
#                            if(str(m[Scheduled[p][a][b][m][t]])=='True'):
#                                f_write.write(str(p) + '-' + str(a) + '-' + str(b) +'-' + str(m) +'-'+ str(t) + ':' + str(m[Scheduled[p][a][b][m][t]]) + '\n')
#    else:
#        f_write.write('\n did not meet requirements\n')
#        break
    
#f_write.write('***************************\n\n')

###################### End #######################


