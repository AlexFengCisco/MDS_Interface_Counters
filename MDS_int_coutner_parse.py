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
## some old line card interface counters as below    
fc5/11
    5 minutes input rate 191985848 bits/sec, 23998231 bytes/sec, 11642 frames/sec
    5 minutes output rate 190598816 bits/sec, 23824852 bytes/sec, 11635 frames/sec
    245118543753 frames input, 500744079849872 bytes
      0 class-2 frames, 0 bytes
      245118543753 class-3 frames, 500744079849872 bytes
      0 class-f frames, 0 bytes
      0 discards, 0 errors, 0 CRC
      0 unknown class, 0 too long, 0 too short
    528152042374 frames output, 1084283773043848 bytes
      0 class-2 frames, 0 bytes
      528152042374 class-3 frames, 1084283773043848 bytes
      0 class-f frames, 0 bytes
      11 discards, 0 errors
    2 input OLS, 2 LRR, 1 NOS, 82 loop inits
    18 output OLS, 12 LRR, 18 NOS, 17 loop inits
    13 link failures, 43 sync losses, 0 signal losses
     4407703765 transmit B2B credit transitions from zero
     4769921 receive B2B credit transitions from zero
      32 receive B2B credit remaining
      5 transmit B2B credit remaining
      5 low priority transmit B2B credit remaining    
      
      
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
##23:      x timeout discards
##24:      x credit loss
23:      x input OLS
24:      x input LRR
25:      x input NOS
26:      x input loop inits
27:      x output OLS
28:      x output LRR
29:      x output NOS
30:      x output loop inits
31:      x link failures
32:      x sync losses
33:      x signal losses
34:      x Transmit B2B credit transitions to zero
35:      x Receive B2B credit transitions to zero
##40:      2.5us TxWait due to lack of transmit credits
##46:      Percentage Tx credits not available for last 1s: 0%
##47:      Percentage Tx credits not available for last 1m: 0%
##48:      Percentage Tx credits not available for last 1h: 0%
##49:      Percentage Tx credits not available for last 72h: 0%
38:      receive B2B credit remaining
40:      transmit B2B credit remaining
'''
import re
import xlsxwriter  

#open show interface counters text file
fh = open("/Users/AlexFeng/git/MDS_Interface_Counters/sw-core1-9710_10.75.60.4_if_count.txt", "r") 
fh_str = fh.read()


#split a whole file string to multilines
multiStr = fh_str.splitlines(1)


#delete the lines contains word class- , to avoid E port and F port's different counters
p1 = re.compile(r'class-') 
p2 = re.compile(r'timeout')
p3 = re.compile(r'TxWait')
p4 = re.compile(r'Percentage')
p5 = re.compile(r'low')
outStr=u""

for singleLine in multiStr: 
    if p1.search(singleLine) == None and p2.search(singleLine)== None and p3.search(singleLine) == None and p4.search(singleLine)== None:
        outStr += p1.sub( '', singleLine,count = 1 )


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
    if if_count_index == 41: #each 41 counters form a single interface counters list  and append to the whole interface info list
        interface_fc_info.append(interface_fc_counters)
        if_count_index=0
        interface_fc_counters=[]
# interface info list completed , you may print it 

#print interface_fc_info        

#  example      print interface slot/id and tx bb_credit_zero    
for i in interface_fc_info:
    slot=i[0]  #has to -1 ;-(
    interface_id=i[1]
    tx_bb_zero=i[33]
    i[33]=int(i[33]) #convert string to integer
    print "interface fc "+slot+"/"+interface_id+"   tx bb_credit_zero  "+tx_bb_zero
    

#  example order by tx_bb_zero

print "=================print interface info order by tx bb credit zero==================="

def getKey(item):
    return item[33]

interface_fc_info_order_bb_zero=[]
interface_fc_info_order_bb_zero=sorted(interface_fc_info, key=getKey,reverse=True)

for i in interface_fc_info_order_bb_zero:
    slot=i[0]  #has to -1 ;-(
    interface_id=i[1]
    tx_bb_zero=i[33]
    print "interface fc "+slot+"/"+interface_id+"   tx bb_credit_zero  "+str(tx_bb_zero)

# example save as xlsx file

workbook=xlsxwriter.Workbook('/Users/AlexFeng/git/MDS_Interface_Counters/sw-core1-9710_10.75.60.4_if_count.xlsx')
worksheet = workbook.add_worksheet()

row=0
col=0

worksheet.write(row, 0, 'Interface')
worksheet.write(row, 1, 'Tx bb_credit_zero')
row +=1

for i in interface_fc_info:
    slot=i[0]  #has to -1 ;-(
    interface_id=i[1]
    tx_bb_zero=i[33]
    print "interface fc "+slot+"/"+interface_id+"   tx bb_credit_zero  "+str(tx_bb_zero)

    worksheet.write(row, col,slot+'/'+interface_id)
    worksheet.write(row, col+1,tx_bb_zero)
    row +=1
    
    
workbook.close()
