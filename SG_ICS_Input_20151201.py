
## NOTE: The number of unique measurements (for both power flows and power consumptions) needs to be moved up (one step) manually in the input file

import io
import sys
import datetime
import random


NUMBER_BUSES = 14
NUMBER_LINES = 20


MSR_PER_IED = 2     ## The average number of measurements per IED

RTU_MTU_HIERARCHY_LEVEL = 2     ## The average hierarchy level (how an rtu is connected to the MTU)

## Resiliency constraints 
MAX_UNAVAILABLE_IEDS = 1
MAX_UNAVAILABLE_RTUS = 1


#################################################
## Open the files to get preliminary data to produce the input file

num_buses = NUMBER_BUSES
num_lines = NUMBER_LINES

f_read_name = 'ICS_Bus_' + str(num_buses) + '_' + str(num_lines)  + '.txt'
f_read = open(f_read_name, 'r')

f_read_name2 = 'ICS_H_Matrix_' + str(num_buses) + '_' + str(num_lines)  + '.txt'
f_read2 = open(f_read_name2, 'r')


#################################################
## Number of buses and measurements
while True:
    line = f_read.readline()
    if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
        continue

    words = line.split()
    
    if (len(words) == 2):
        if ((num_buses != int(words[0])) or (num_buses != int(words[0]))):
            print ('Wrong Input File: Exit')
            sys.exit()
        #print num_states, num_msrs
    else:
        print ('Unmatched Input: Exit')
        sys.exit()

    break



#################################################
## Line Information

line_bus_matrix = [[0 for j in range(0, num_buses + 1)] for i in range(0, num_lines + 1)]

for j in range(1, num_lines + 1):     
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) == 3):
            ## If the corresponding measurement is taken
            if (int(words[0]) != j):
                print ('Wrong Input: Exit')
                sys.exit()
                                    
            line_bus_matrix[j][int(words[1])] = 1
            line_bus_matrix[j][int(words[2])] = -1

        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break


#################################################
## Create the measurement information

num_msrs = num_lines * 2 + num_buses
bus_msr_matrix = [[0 for j in range(0, num_msrs + 1)] for i in range(0, num_buses + 1)]

for j in range(1, num_buses + 1):     
    for i in range(1, num_lines + 1):                                 
        if (line_bus_matrix[i][j] == 1):    ## Forward Current flow                                                                
            bus_msr_matrix[j][i] = 1
        elif (line_bus_matrix[i][j] == -1):    ## Forward Current flow                                                                
            bus_msr_matrix[j][num_lines + i] = 1


#################################################
## Measurement Information

msr_taken = [0 for i in range(0, num_msrs + 1)]

for i in range(1, num_msrs + 1):
    while True:
        line = f_read.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) == 2):
            ## If the corresponding measurement is taken
            if (int(words[0]) != i):
                print ('Wrong Input: Exit')
                sys.exit()
            
            if (int(words[1]) == 1):
                msr_taken[i] = 1
        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        break


#################################################
## Deploy IEDs for measurements, associated RTUs

msr_ied = [0 for i in range(0, num_msrs + 1)]
ied_rtu = []
ied_rtu.append(0)

num_ieds = 1
num_rtus = 1
for i in range(1, num_buses + 1):    
    flag = False
    if (msr_taken[i + 2 * num_lines] == 1):
        msr_ied[i + 2 * num_lines] = num_ieds;
        num_ieds += 1        
                
        ied_rtu.append(num_rtus)    ## When we have a new IED to assign, associate an RTU to the previous IED                      
        flag = True

    count = 0
    for j in range(1, num_msrs + 1):
        if ((bus_msr_matrix[i][j] == 1) and (msr_taken[j] == 1)):    ## Forward Current flow
            if (count >= MSR_PER_IED):
                if (random.randint(0, 1) == 1):
                    num_ieds += 1                    
                    count = 0

                    ied_rtu.append(num_rtus)
                    flag = True                    

            msr_ied[j] = num_ieds;
            count += 1
    
    if (count > 0):
        num_ieds += 1 
        ied_rtu.append(num_rtus)
        flag = True                
               
    if (flag == True):
        num_rtus += 1 

num_ieds -= 1   ## the number of ieds is num_ieds - 1
num_rtus -= 1   ## the number of rtus is num_rtus - 1

#################################################
## Networks between RTUs and the MTU

links_rtus_mtu = []
links_rtus_mtu.append([0, 0])   ## The first empty slot
num_links_rtus_mtu = 0

rtus = [0 for i in range(0, num_rtus + 1)]

mtu_id = num_rtus + 1   ## Assuming the last node is the MTU

r = random.randint(1, num_rtus) ## A random rtu for the first link with the MTU
rtus[r] = 1
link = [r, mtu_id]
links_rtus_mtu.append(link)
num_links_rtus_mtu += 1

for i in range(2, num_rtus + 1):    ## One rtu is already selected
    
    while(True):
        r = random.randint(1, num_rtus) ## A random rtu
        if (rtus[r] == 0):  # If the rtu is not considered already
            rtus[r] = 1
            break

    to_rtu = random.randint(0, RTU_MTU_HIERARCHY_LEVEL - 1) ## If 0, then directly connected to the MTU
    if (to_rtu != 0):
        r2 = 0
        while(True):
            r2 = random.randint(1, num_rtus) ## A random rtu
            if ((r2 != r) and (rtus[r2] == 1)):  # If the rtu is already considered
                break
        link = [r, r2]
        links_rtus_mtu.append(link)
        num_links_rtus_mtu += 1
    else:
        link = [r, mtu_id]
        links_rtus_mtu.append(link)
        num_links_rtus_mtu += 1
        
#for i in range(1, num_links_rtus_mtu + 1):
#    print links_rtus_mtu[i], '\n'
 
##################################################
##################################################
### Write the input file

f_write_name = 'Input_ICS_Bus_' + str(num_buses) + '_' + str(num_lines) + '_' + str(RTU_MTU_HIERARCHY_LEVEL) + '.txt'
f_write = open(f_write_name, 'w')

##################################################
f_write.write('# Number of states and measurements\n')
f_write.write(str(num_buses) + ' ' + str(num_msrs) + '\n')
f_write.write('\n')

##################################################
f_write.write('# Jacobian matrix (states and measurement association) and if corresponding measurement is recorded/reported\n')

for i in range(1, num_msrs + 1):     
    while True:
        line = f_read2.readline()
        if ((line is None) or (line[0] == '#') or (line[0] == '\n')):
            continue

        words = line.split()
                        
        if (len(words) == num_buses):                                                        
            for j in range(0, num_buses):
                f_write.write(words[j] + ' ')
        else:
            print ('Unmatched Input: Exit')
            sys.exit()

        f_write.write(str(msr_taken[i]))
        break

    f_write.write('\n')
f_write.write('\n')

##################################################
count = 0
f_write.write('# Power flow unique measurement sets\n')
for i in range(1, num_lines + 1):
    flag = False
    if ((msr_taken[i] == 1) and (msr_taken[i + num_lines] == 1)):
        f_write.write(str(i) + ' ' + str(i + num_lines))
        flag = True
        count += 1
    elif (msr_taken[i] == 1):
        f_write.write(str(i))
        flag = True
        count += 1
    elif (msr_taken[i + num_lines] == 1):
        f_write.write(str(i + num_lines))
        flag = True
        count += 1
    
    if (flag == True):
        f_write.write('\n')

f_write.write('\n')

f_write.write('# Number of power flow unique measurement sets\n')
f_write.write(str(count) + '\n')
f_write.write('\n')

##################################################
count = 0
f_write.write('# Power consumption unique measurement sets\n')
for i in range(1, num_buses + 1):    
    if (msr_taken[i + 2 * num_lines] == 1):
        f_write.write(str(i + 2 * num_lines) + ' ')
        count += 1
        flag = True
        for j in range(1, num_msrs - num_buses + 1):
            if (bus_msr_matrix[i][j] == 1):
                if (msr_taken[j] == 0):
                    flag = False
                    break

        if (flag == True):            
            for j in range(1, num_msrs - num_buses + 1):
                if (bus_msr_matrix[i][j] == 1):
                    f_write.write(str(j) + ' ')            

        f_write.write('\n')            
f_write.write('\n')

f_write.write('# Number of power consumption unique measurement sets\n')
f_write.write(str(count) + '\n')
f_write.write('\n')

##################################################
f_write.write('# Numbers of IEDs and RTUs\n')
f_write.write(str(num_ieds) + ' ' + str(num_rtus) + '\n')
f_write.write('\n')

f_write.write('# Measurements corresponding to IEDs\n')
for i in range(1, num_ieds + 1):
    f_write.write(str(i) + ' ')    
    for j in range(1, num_msrs + 1):
        if ((msr_taken[j] == 1) and (msr_ied[j] == i)):            
            f_write.write(str(j) + ' ')    
    f_write.write('\n')            
f_write.write('\n')

##################################################
f_write.write('# Topology (Links)\n')
f_write.write(str(num_ieds + num_links_rtus_mtu) + '\n')
f_write.write('\n')

f_write.write('# Communication Path (among the IEDs, the RTUs, and the MTU)\n')
for i in range(1, num_ieds + 1):
    f_write.write(str(i) + ' ' + str(ied_rtu[i] + num_ieds) + '\n')

for i in range(1, num_links_rtus_mtu + 1):
    f_write.write(str(links_rtus_mtu[i][0] + num_ieds) + ' ' + str(links_rtus_mtu[i][1] + num_ieds) + '\n')        
f_write.write('\n')

f_write.write('# k Resiliency requirements (ieds and/or rtus)\n')
f_write.write(str(MAX_UNAVAILABLE_IEDS) + ' ' + str(MAX_UNAVAILABLE_RTUS) + '\n')

###################### End #######################

