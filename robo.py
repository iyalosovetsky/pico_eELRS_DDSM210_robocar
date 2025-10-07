from machine import UART, Pin




from  uart_rx_32 import UART_RX_32
from  dds210 import ddsm



import utime

BAUD = 115200
class Robo():
    def __init__(self, motors_def, motors_uart, MAX_SPEED=209.0 ):
        print("motors_def",motors_def)
        self.motors_uart=motors_uart
        self.speed = 0
        self.arrow = 0
        self.motors_def=motors_def
        self.RXs=[None for ii in range(len(self.motors_def))]
        self.motors=[None for ii in range(len(self.motors_def))]
        self.motors_feedback=[None for ii in range(len(self.motors_def))]
        self.init_motors()
        self.mode=-1
        self.old_arrow=0
        self.arrow=0 
        self.old_speed=0
        self.speed=0 
        self.old_turn=0 
        self.turn=0
        self.old_turn_val=0 
        self.turn_val=0
        self.disarmed=False
        self.old_disarmed=True
        self.babyStep=False
        self.MAX_SPEED=MAX_SPEED
        self.update=utime.ticks_ms()

        
    def init_motors(self):
        print('try init')  
        for ii in range(len(self.motors_def)):
            print(self.motors_def[ii])
            self.RXs[ii]=UART_RX_32(statemachine=self.motors_def[ii]['sm'], rx_pin = self.motors_def[ii]['rx'], baud=BAUD)
            self.RXs[ii].active(1)
            print('try',ii,self.motors_def[ii]['name'])
            self.motors[ii]=ddsm(self.motors_uart,self.RXs[ii],self.motors_def[ii]['dir'])  #id =1 fronrLeftt normal ++
            self.motors_feedback[ii]=self.motors[ii].getFeedback()
            print('   feedback',self.motors_feedback[ii])
            self.motors[ii].setMode(mode=0) # open loop
        self.mode=0
        self.update=utime.ticks_ms()
        
    def telemetry_change(self,arrow,speed,turn,turn_val,isBabyStep,isDisarmed):
      if (self.old_arrow!=arrow or self.old_speed!=speed or self.old_turn!=turn or self.old_turn_val!=turn_val or self.disarmed!=isDisarmed or self.babyStep!=isBabyStep
          or utime.ticks_ms()-self.update>2000
          ):

         self.old_arrow=self.arrow 
         self.old_speed=self.speed
         self.old_turn=self.turn
         self.old_turn_val=self.turn_val
         self.old_disarmed=self.disarmed
         
         self.arrow=arrow 
         self.speed=speed
         self.turn=turn
         self.turn_val=turn_val
         
         self.disarmed=isDisarmed
         self.babyStep=isBabyStep
         self.run_engine()
         #print('lastu',self.update,utime.ticks_ms(),utime.ticks_ms()-self.update)
         self.update=utime.ticks_ms()
         



    def run_engine(self):
       if self.disarmed==0 and self.old_disarmed==1 and utime.ticks_ms()-self.update>10000 and self.mode==0:
           self.init_motors()
       if self.disarmed==1 and (self.old_disarmed==0 or utime.ticks_ms()-self.update>10000) :
         print('try disarm')  
         for ii in range(len(self.motors_def)):
           self.motors[ii].setBrake()
           self.motors[ii].setMode(mode=0) # release
         self.mode=0
       elif self.disarmed==0 and (self.arrow==0 or self.speed<0.12) and self.turn!=0 and self.turn_val>0.2 and self.babyStep==1:
         for ii in range(len(self.motors_def)):
           if self.mode!=2 or utime.ticks_ms()-self.update>2000:  
             self.motors[ii].setMode(mode=2) # open loop
           if self.motors_def[ii]['name'].endswith('Right')  :  
               self.motors[ii].setDrive0(val=-self.turn*5,driveMode=2, feedb=2)
           else:
               self.motors[ii].setDrive0(val=self.turn*5,driveMode=2, feedb=2)
           self.mode=2  
       elif self.disarmed==0 and self.arrow!=0:
         #print('try go ',int(self.MAX_SPEED*self.arrow*self.speed),self.turn*self.turn_val)  #arrow*speed,turn*turn_val
         baseSpeed=int(self.MAX_SPEED*self.arrow*self.speed)
         delta=int(baseSpeed*0.8*self.turn*self.turn_val)
         #print('try go ',baseSpeed,delta)  #arrow*speed,turn*turn_val
         for ii in range(len(self.motors_def)):
           if self.mode!=2 or utime.ticks_ms()-self.update>2000:  
             self.motors[ii].setMode(mode=2) # open loop
           
           if self.motors_def[ii]['name'].endswith('Right')  :
               speed=baseSpeed-delta
           else:
               speed=baseSpeed+delta
               
           self.motors[ii].setDrive0(val=speed,driveMode=2, feedb=2)
         self.mode=2  
       elif self.disarmed==0 and (self.speed==0 or self.arrow==0):
         for ii in range(len(self.motors_def)):
           if self.mode!=2 or utime.ticks_ms()-self.update>2000:
             self.motors[ii].setMode(mode=2) # open loop
           self.motors[ii].setBrake()
                




