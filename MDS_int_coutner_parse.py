'''
MDS interface counters parse
for MDS 9513 8G advanced Line card 

issue show interface counters  and capture or save to a text file ,then cut off interface mgt part ,cos this module only deal with FC counters


Created on Feb 13, 2018

@author: AlexFeng
'''
'''
Because E port and F port has different counters , delete all lines contained class- in advance 

fc1/1
    5 minutes input rate 352 bits/sec, 44 bytes/sec, 0 frames/sec
    5 minutes output rate 288 bits/sec, 36 bytes/sec, 0 frames/sec
    480849 frames input, 35793364 bytes
      0 discards, 0 errors, 0 CRC/FCS
      0 unknown class, 0 too long, 0 too short
    480932 frames output, 27649100 bytes
      0 discards, 0 errors
    0 timeout discards, 0 credit loss
    3 input OLS, 7 LRR, 0 NOS, 36 loop inits
    6 output OLS, 1 LRR, 1 NOS, 4 loop inits
    1 link failures, 0 sync losses, 1 signal losses
     14 Transmit B2B credit transitions to zero
     12 Receive B2B credit transitions to zero
      0 2.5us TxWait due to lack of transmit credits
      Percentage Tx credits not available for last 1s/1m/1h/72h: 0%/0%/0%/0%
      500 receive B2B credit remaining
      64 transmit B2B credit remaining
    Last clearing of "show interface" counters : never
    
    
interface fc counter collection list index define

1:       slot_id  
2:       interface_id
4:       5 minutes input rate x bits/sec 
5:       5 minutes input rate x bytes/sec
6:       5 minutes input rate x frames/sec
8:       5 minutes output rate x bits/sec
9:       5 minutes output rate x bytes/sec
10:      5 minutes output rate x frames/sec
11:      total x frames input
12:      total x bytes input
13:      x discards
14:      x errors
15:      x CRC/FCS
16:      x unknown class
17:      x too long
18:      x too short
19:      x frames output, 27649100 bytes
20:      x 27649100 bytes
21:      x discards
22:      x errors
23:      x timeout discards
24:      x credit loss
25:      x input OLS
26:      x input LRR
27:      x input NOS
28:      x input loop inits
29:      x output OLS
30:      x output LRR
31:      x output NOS
32:      x output loop inits
33:      x link failures
34:      x sync losses
35:      x signal losses
36:      x Transmit B2B credit transitions to zero
38:      x Receive B2B credit transitions to zero
40:      2.5us TxWait due to lack of transmit credits
46:      Percentage Tx credits not available for last 1s: 0%
47:      Percentage Tx credits not available for last 1m: 0%
48:      Percentage Tx credits not available for last 1h: 0%
49:      Percentage Tx credits not available for last 72h: 0%
50:      receive B2B credit remaining
52:      transmit B2B credit remaining
'''
import re


#open show interface counters text file
fh = open("/Users/AlexFeng/git/LAB/tmp/sw-core1-9710_10.75.60.4_if_count.txt", "r") 
fh_str = fh.read()


#split a whole file string to multilines
multiStr = fh_str.splitlines(1)


#delete the lines contains word class- , to avoid E port and F port's different counters
p = re.compile(r'class-') 
outStr=u""

for singleLine in multiStr: 
    if p.search(singleLine) == None:
        outStr += p.sub( '', singleLine,count = 1 )


#collect all the numbers from multi lines without class-
reObj1= re.compile(r"\d+\.?\d*")
fn_str= reObj1.findall(outStr)


#modeling numbers to a structured list  
interface_fc_info=[]
interface_fc_counters=[]
if_index=0
if_count_index=0

for i in fn_str:
    if_count_index=if_count_index+1
    interface_fc_counters.append(i)
    if if_count_index == 53: #each 53 counters form a single interface counters list  and append to the whole interface info list
        interface_fc_info.append(interface_fc_counters)
        if_count_index=0
        interface_fc_counters=[]
# interface info list completed , you may print it 

#print interface_fc_info        

#  example      print interface slot/id and tx bb_credit_zero    
for i in interface_fc_info:
    slot=i[0]  #has to -1 ;-(
    interface_id=i[1]
    tx_bb_zero=i[35]
    i[35]=int(i[35]) #convert string to integer
    print "interface fc "+slot+"/"+interface_id+"   tx bb_credit_zero  "+tx_bb_zero
    

#  example order by tx_bb_zero

print "=================print interface info order by tx bb credit zero==================="

def getKey(item):
    return item[35]

interface_fc_info_order_bb_zero=[]
interface_fc_info_order_bb_zero=sorted(interface_fc_info, key=getKey,reverse=True)

for i in interface_fc_info_order_bb_zero:
    slot=i[0]  #has to -1 ;-(
    interface_id=i[1]
    tx_bb_zero=i[35]
    print "interface fc "+slot+"/"+interface_id+"   tx bb_credit_zero  "+str(tx_bb_zero)

