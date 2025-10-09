from machine import UART, Pin

import select, sys



import os
from crsf import Crsf
from robo import Robo
import utime

BAUD = 115200


                





LEFT_VERTICAL=2
LEFT_HORIZONTAL=3

RIGHT_VERTICAL=1
RIGHT_HORIZONTAL=0
E_SWITCH=4
B_SWITCH=5

F_SWITCH=7
C_SWITCH=6
A_SWITCH=8


MIN=180
MAX=1750
CENTER=992
TH=60




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

# for ddsm
uart0 = UART(0, baudrate=BAUD, parity=None, stop=1, tx=Pin(12), rx=Pin(13) )
#for telemetrt TX12
uart1 = UART(1, baudrate=420000, bits=8, parity=None, stop=1, tx=Pin(8), rx=Pin(9))



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


crsf1 = Crsf(uart1)
utime.sleep_ms(100)
robo=Robo(MOTORS,uart0)
utime.sleep_ms(100)
robo.telemetry_change(arrow=1,speed=0.1,turn=0,turn_val=0,isBabyStep=False,isDisarmed=False)
utime.sleep_ms(500)
robo.telemetry_change(arrow=1,speed=0.0,turn=0,turn_val=0,isBabyStep=False,isDisarmed=False)

# Створюємо об'єкт poll для моніторингу вхідного потоку (sys.stdin)
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

print("Send me data over USB!")

ii=0
try:
        while True:
          ii+=1
          if crsf1.tick()!=1 :
              if crsf1.newRCData<=-9:
                utime.sleep_ms(10)
          if (ii%100) == 0:
              need_init = False
              for ii in range(len(robo.motors_def)):
                if robo.motors[ii].id is None:
                    need_init = True
              if  need_init:     
                    print(f" DDSM reinit:")
                    robo.init_motors()
                    
                    
                    
              
          # Перевіряємо, чи є дані для читання (timeout = 0, щоб не блокувати)
          if poll_obj.poll(0):
            # Якщо є, зчитуємо один рядок
            data = sys.stdin.readline().strip()
            if data:
                print(f"I received: {data}")
                if data.startswith('stat') or data.startswith('info'):
                    print(f"status is:")
                    print(f"  crsf1 :{crsf1.all_counter} {crsf1.cmd_counter}")
                    print(f"  DDSM210 :")
                    for ii in range(len(robo.motors_def)):
                        print(f"    ddsm is: {ii} is {robo.motors[ii].id}")
                        print(f"    ddsm is: {ii} is {robo.motors[ii].getFeedback()}")
                elif data.startswith('ini'):
                    print(f"status is:")
                    print(f"  crsf1 :{crsf1.all_counter} {crsf1.cmd_counter}")
                    print(f"  DDSM210 :")
                    print(f"    init:")
                    robo.init_motors()
                    for ii in range(len(robo.motors_def)):
                        print(f"    ddsm is: {ii} is {robo.motors[ii].id}")
                        print(f"    ddsm is: {ii} is {robo.motors[ii].getFeedback()}")
                    
                    
                
                
          #print('->',crsf1.channels[E_SWITCH],crsf1.channels[RIGHT_VERTICAL],crsf1.channels[LEFT_HORIZONTAL],crsf1.channels[RIGHT_VERTICAL],crsf1.channels[RIGHT_HORIZONTAL])
          arrow=0
          speed=0
          turn=0 
          turn_val=0
          if abs(crsf1.channels[RIGHT_VERTICAL]-CENTER)>TH:
            arrow=0
            speed=abs(crsf1.channels[RIGHT_VERTICAL]-CENTER)/CENTER
            if crsf1.channels[RIGHT_VERTICAL]-CENTER>0:
                arrow=1
            else:
                arrow=-1
            #print('dir',arrow,speed)

          if abs(crsf1.channels[RIGHT_HORIZONTAL]-CENTER)>TH:
            turn=0
            turn_val=abs(crsf1.channels[RIGHT_HORIZONTAL]-CENTER)/CENTER
            if crsf1.channels[RIGHT_HORIZONTAL]-CENTER>0:
                turn=1
            else:
                turn=-1
            #print('turn',turn,turn_val)
                
          
          robo.telemetry_change(arrow=arrow,speed=speed,turn=turn,turn_val=turn_val,isBabyStep=(crsf1.channels[RIGHT_VERTICAL]-CENTER>TH//2 or CENTER-crsf1.channels[RIGHT_VERTICAL]>TH//2),isDisarmed=(crsf1.channels[E_SWITCH]<=CENTER))
except KeyboardInterrupt:
    print('break there')
    robo.telemetry_change(arrow=0,speed=0,turn=0,turn_val=0,isBabyStep=False,isDisarmed=True)
    


print('Done.')

