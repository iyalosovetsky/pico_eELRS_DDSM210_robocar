from machine import UART, Pin
import time




from  uart_rx_32 import UART_RX_32
from  dds210 import ddsm

#6. Velocity loop command (－210～210 rpm)
#01 64 FF CE 00 00 00 00 00 DA (-5rpm)
#01 64 FF 9C 00 00 00 00 00 9A (-10rpm)
#01 64 00 00 00 00 00 00 00 50 (0rpm)
#01 64 00 32 00 00 00 00 00 D3 (5rpm)
#01 64 00 64 00 00 00 00 00 4F (10rpm)
#7. Position loop command (0～32767 corresponds to 0～360°)
#01 64 00 00 00 00 00 00 00 50 (0)
#01 64 27 10 00 00 00 00 00 57 (10000)
#01 64 4E 20 00 00 00 00 00 5E (20000)
#01 64 75 30 00 00 00 00 00 A7 (30000)


#uart0 = UART(0, baudrate=115200, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
BAUD = 115200
uart0 = UART(0, baudrate=BAUD, parity=None, stop=1, tx=Pin(12), rx=Pin(13) )
uartr=""
info=b'\x01\x74\x00\x00\x00\x00\x00\x00'
#Data Field	DATA[0]	DATA[1]	DATA[2]	DATA[3]	DATA[4]	DATA[5]	DATA[6]	DATA[7]	DATA[8]	DATA[9]
#Content	ID	0x64	Speed/position set high 8 bits	Speed/position set low 8 bits	Feedback 1 content	Feedback 2 content	Acceleration time	Brake	0	CRC8

velo10  =b'\x01\x64\xff\xce\x00\x00\x00\x00\x00'
pos1    =b'\x01\x64\x00\x10\x00\x00\x00\x00\x00' # pos=0
set_id  =b'\xAA\x55\x53\x01\x00\x00\x00\x00\x00' #id=1
#set_id=b'\xAA\x55\x53\x01\x00\x00\x00\x00\x00\xCB' # with crc
#check_id=b'\xC8\x64\x00\x00\x00\x00\x00\x00\x00\xDE' # with crc

#set_id=b'\x64\x00\x00\x00\x00\x0\x00\x00\xDE' # with crc

#3. Brake command, valid in velocity loop mode.
#01 64 00 00 00 00 00 FF 00 D1
# rx PIO begin


# ---------------------------------------------------------
MOTORS=[{'rx':15,'sm':0,'dir':-1,'id':2,'name':'BackRight'},
        {'rx':14,'sm':1,'dir':-1,'id':4,'name':'FrontRight'},
        {'rx':11,'sm':4,'dir':1,'id':3,'name':'BackLeft'},
        {'rx':10,'sm':5,'dir':1,'id':1,'name':'FrontLeft'}
        ]

RXs=[None,None,None,None]
motors=[None,None,None,None]

for ii in range(4):
    print(MOTORS[ii])
    RXs[ii]=UART_RX_32(statemachine=MOTORS[ii]['sm'], rx_pin = MOTORS[ii]['rx'], baud=BAUD)
    RXs[ii].active(1)
    print('try',ii,MOTORS[ii]['name'])
    motors[ii]=ddsm(uart0,RXs[ii],MOTORS[ii]['dir'])  #id =1 fronrLeftt normal ++
    _=motors[ii].getFeedback()
    print('other in',_)
    motors[ii].setMode(mode=0) # open loop

print('==========try drive val=20,mode=2, feedb=2')
for ii in range(4):
    motors[ii].setMode(mode=2) # open loop
    motors[ii].setDrive0(val=15,driveMode=2, feedb=2)
time.sleep(5)

print('==========try brake')
for ii in range(4):
    motors[ii].setBrake()
time.sleep(1)

print('==========try angle val=16000,mode=3, feedb=2')
for ii in range(4):
    motors[ii].setMode(mode=3) # angle
time.sleep(1)
print('==========try2 angle val=16000,mode=3, feedb=2')
for ii in range(4):
    motors[ii].setDrive0(val=30000,driveMode=3, feedb=2)
time.sleep(10)

print('==========try release')
for ii in range(4):
    motors[ii].setBrake()
    motors[ii].setMode(mode=0) # release
print('Done.')