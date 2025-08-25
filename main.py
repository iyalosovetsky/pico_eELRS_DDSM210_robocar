from robot_car import RobotCar
from crsf import Crsf
import utime
from machine import UART, Pin, ADC


CRSF_SYNC = 0xC8
CHANNELS=[0 for jj in range(16)]
LEFT_VERTICAL=2
LEFT_HORIZONTAL=3

RIGHT_VERTICAL=1
RIGHT_HORIZONTAL=0
E_SWITCH=4
B_SWITCH=5

F_SWITCH=7
C_SWITCH=6
A_SWITCH=8



# Pico W GPIO Pin
'''LEFT_MOTOR1_PIN_1 = 16
LEFT_MOTOR1_PIN_2 = 17
RIGHT_MOTOR1_PIN_1 = 18
RIGHT_MOTOR1_PIN_2 = 19
MOTOR1_STBY = 20

LEFT_MOTOR2_PIN_1 = 15
LEFT_MOTOR2_PIN_2 = 14
RIGHT_MOTOR2_PIN_1 = 13
RIGHT_MOTOR2_PIN_2 = 12
MOTOR2_STBY = 11
'''

''' 16 17 gnd 18 19 20
 forward nc  AIN2 AIN1 STBY BIN1 BIN2 NC GND
         -    17   16   20   18   19  -  GND
         -    blue mag  red  yel  ora -  green  
 16 17 -> 0A 0B -> AIN1 AIN2 ->magenta blue
 18 19 -> 1A 1B -> BIN1 BIN2 ->yellow orange
 20 stand by
 #0A
#define LEFT_MOTOR_FORWARD_PIN_1 18
 #0B
#define LEFT_MOTOR_FORWARD_PIN_2 19
 #1A
#define RIGHT_MOTOR_FORWARD_PIN_1 16
 #1B
#define RIGHT_MOTOR_FORWARD_PIN_2 17
#define MOTOR_FORWARD_STBY 20

/* MOTOR_BACKWARD*/
// 15 14 gnd  13 12 11
// bacward nc  AIN2 AIN1 STBY BIN1 BIN2 NC GND
//         -    15   14   11    12   13  -  GND
//         -    mage blue red oran yell  -  green  
// 14 15 -> 7A 7B -> AIN1 AIN2 -> blue magenta
// 12 13 -> 6A 6B -> BIN1 BIN2 -> orange yellow
// 11 stand by red
// #7A
#define LEFT_MOTOR_BACKWARD_PIN_1 14
// #7B
#define LEFT_MOTOR_BACKWARD_PIN_2 15
// #6A
#define RIGHT_MOTOR_BACKWARD_PIN_1 12
// #6B
#define RIGHT_MOTOR_BACKWARD_PIN_2 13
#define MOTOR_BACKWARD_STBY 11

'''
LEFT_MOTOR1_PIN_1 = 18 
LEFT_MOTOR1_PIN_2 = 19 
RIGHT_MOTOR1_PIN_1 = 16
RIGHT_MOTOR1_PIN_2 = 17
MOTOR1_STBY = 20


LEFT_MOTOR2_PIN_1 = 14
LEFT_MOTOR2_PIN_2 = 15
RIGHT_MOTOR2_PIN_1 = 12
RIGHT_MOTOR2_PIN_2 = 13
MOTOR2_STBY = 11


uart = UART(1, baudrate=420000, bits=8, parity=None, stop=1, tx=Pin(8), rx=Pin(9))
analogue_input = ADC(28)



motor_forw_pins = [LEFT_MOTOR1_PIN_1, LEFT_MOTOR1_PIN_2, RIGHT_MOTOR1_PIN_1, RIGHT_MOTOR1_PIN_2,MOTOR1_STBY]
motor_back_pins = [LEFT_MOTOR2_PIN_1, LEFT_MOTOR2_PIN_2, RIGHT_MOTOR2_PIN_1, RIGHT_MOTOR2_PIN_2,MOTOR2_STBY]

# Create an instance of our robot car
robot_car_forw = RobotCar(motor_forw_pins, 20000)
robot_car_back = RobotCar(motor_back_pins, 20000)



crsf1 = Crsf(uart)










        
        
 

maxLeftVertical=1700
minLeftVertical=180

maxLeftHorizontal=1700
minLeftHorizontal=180


MIN=180
MAX=1750
CENTER=992
TH=40





old_speed=0
old_arrow=0
old_turn=0
old_turn_val=0
ii = 0
BAT_DIA=0.8*2 #v from 3.35 to 4.15 (100..0 prc)
BAT_FULL =4.2*2 #v 2S bat
BAT_CAPA =2900 #mAh 
#https://stfn.pl/blog/22-pico-battery-level/
VOLTAGE_K=3.3 * 3.232 / 65535 # Vref 3.3V 12bit 3.232 resistor divider


if __name__ == '__main__':
    try:
        while True:
          ii+=1
          if crsf1.tick()!=1 :
              if crsf1.newRCData<=-9:
                utime.sleep_ms(10)
          if ii%100==0:
            v2sbat=analogue_input.read_u16()* VOLTAGE_K
            prc2s=(BAT_DIA-(BAT_FULL-v2sbat))/BAT_DIA
            if prc2s>1:
                prc2s=1
            elif prc2s<0:
                prc2s=0
            v_bat=int(round(v2sbat*10,0 ))
            v_prc=int(round(prc2s*100,0 ))
            v_cap=int(round(BAT_CAPA*prc2s ,0 ))
            
        
            
            crsf1.sentBattery(v_bat,122, v_cap,v_prc)# 18ma 23% 1.2 A 4.1V    
          
          #print('->',CHANNELS[E_SWITCH],CHANNELS[LEFT_VERTICAL],CHANNELS[LEFT_HORIZONTAL],CHANNELS[RIGHT_VERTICAL],CHANNELS[RIGHT_HORIZONTAL])
          arrow=0
          speed=0
          turn=0
          turn_val=0
          if abs(crsf1.channels[LEFT_VERTICAL]-CENTER)>TH:
            arrow=0
            speed=abs(crsf1.channels[LEFT_VERTICAL]-CENTER)/CENTER
            if crsf1.channels[LEFT_VERTICAL]-CENTER>0:
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


          if crsf1.channels[E_SWITCH]>CENTER and  (old_arrow!=arrow or old_speed!=speed or old_turn!=old_turn or old_turn_val!=turn_val):
              old_arrow=arrow 
              old_speed=speed
              old_turn=turn
              old_turn_val=turn_val
              if (arrow==0 or speed<0.12) and turn!=0 and turn_val>0.2 and (crsf1.channels[LEFT_VERTICAL]-CENTER>TH//2 or CENTER-crsf1.channels[LEFT_VERTICAL]>TH//2):
                  robot_car_forw.change_speed(0.19,0.);
                  robot_car_back.change_speed(0.19,0.);
                  robot_car_forw.move_reverse(turn)
                  robot_car_back.move_reverse(turn)
                      
              elif speed==0 or arrow==0:
                robot_car_forw.stop()
                robot_car_back.stop()
              elif arrow>0:
                  robot_car_forw.change_speed(speed,turn*turn_val);
                  robot_car_back.change_speed(speed,turn*turn_val);
                  robot_car_forw.move_forward()
                  robot_car_back.move_forward()
              elif arrow<0:
                  robot_car_forw.change_speed(speed,turn*turn_val);
                  robot_car_back.change_speed(speed,turn*turn_val);
                  robot_car_forw.move_backward()
                  robot_car_back.move_backward()
                 
          elif crsf1.channels[E_SWITCH]<=CENTER :
                robot_car_forw.stop()
                robot_car_back.stop()

                            



        robot_car_forw.deinit()
        robot_car_back.deinit()

    except KeyboardInterrupt:
        robot_car_forw.deinit()
        robot_car_back.deinit()
