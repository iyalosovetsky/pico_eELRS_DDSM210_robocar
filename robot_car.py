
from machine import Pin
from machine import PWM
import utime

'''
Class to represent our robot car
'''
class RobotCar:
    MAX_DUTY_CYCLE = 65535
    MIN_DUTY_CYCLE = 0
    OUT_MIN = 40000
    OUT_MAX = 65535
    def __init__(self, motor_pins, frequency=20000):
        self.left_motor_pin1 = PWM(Pin(motor_pins[0], mode=Pin.OUT))
        self.left_motor_pin2 = PWM(Pin(motor_pins[1], mode=Pin.OUT))
        self.right_motor_pin1 = PWM(Pin(motor_pins[2], mode=Pin.OUT))
        self.right_motor_pin2 = PWM(Pin(motor_pins[3], mode=Pin.OUT))
        self.stand_by_motor_pin= Pin(motor_pins[4], mode=Pin.OUT)
        # set PWM frequency
        self.left_motor_pin1.freq(frequency)
        self.left_motor_pin2.freq(frequency)
        self.right_motor_pin1.freq(frequency)
        self.right_motor_pin2.freq(frequency)
        self.stand_by_motor_pin.value(1)
        
        
        self.current_speed_left = RobotCar.MAX_DUTY_CYCLE
        self.current_speed_right = RobotCar.MAX_DUTY_CYCLE
        
    def move_forward(self):
        self.left_motor_pin1.duty_u16(self.current_speed_left)
        self.left_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        
        self.right_motor_pin1.duty_u16(self.current_speed_right)
        self.right_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
           
    def move_backward(self):
        self.left_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        self.left_motor_pin2.duty_u16(self.current_speed_left)
        
        self.right_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        self.right_motor_pin2.duty_u16(self.current_speed_right)
        
        
    def turn_left(self):
        self.left_motor_pin1.duty_u16(self.current_speed_left)
        self.left_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        
        self.right_motor_pin1.duty_u16(RobotCar.MAX_DUTY_CYCLE)
        self.right_motor_pin2.duty_u16(RobotCar.MAX_DUTY_CYCLE)
        
    def turn_right(self):
        self.left_motor_pin1.duty_u16(RobotCar.MAX_DUTY_CYCLE)
        self.left_motor_pin2.duty_u16(RobotCar.MAX_DUTY_CYCLE)
        
        self.right_motor_pin1.duty_u16(self.current_speed_right)
        self.right_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)

    def move_reverse (self, turn):
        if turn>0:
            self.left_motor_pin1.duty_u16(self.current_speed_left) # forward
            self.left_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
            
            self.right_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE) #backward
            self.right_motor_pin2.duty_u16(self.current_speed_right)
            
            

        elif turn<0:
            self.left_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE) #backward
            self.left_motor_pin2.duty_u16(self.current_speed_left)

            self.right_motor_pin1.duty_u16(self.current_speed_right) # forward
            self.right_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)


    def stop(self):
        self.left_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        self.left_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        
        self.right_motor_pin1.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        self.right_motor_pin2.duty_u16(RobotCar.MIN_DUTY_CYCLE)
        
    ''' Map duty cycle values from 0-100 to duty cycle 40000-65535 '''
    def __map_range0(self, x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def __map_range(self, x):
      if x<=0:
            return RobotCar.OUT_MIN
      if x>=1:
            return RobotCar.OUT_MAX
      return int(x * (RobotCar.OUT_MAX - RobotCar.OUT_MIN)  + RobotCar.OUT_MIN)


    ''' new_speed is a value from 0% - 100% 0..0.99  left -0.99 .. -0.01 rigth +1 .. +99'''
    def change_speed(self, new_speed, turn_val=0):
        if new_speed>0.2:
            new_duty_cycle_l = self.__map_range(new_speed*(1+turn_val*2))
            new_duty_cycle_r = self.__map_range(new_speed*(1-turn_val*2) )
        elif new_speed<=0.3 and turn_val>0:
            new_duty_cycle_l = self.__map_range(new_speed*(1+turn_val*4))
            new_duty_cycle_r = self.__map_range(new_speed )
        elif new_speed<=0.3 and turn_val<=0:
            new_duty_cycle_l = self.__map_range(new_speed)
            new_duty_cycle_r = self.__map_range(new_speed*(1-turn_val*4) )
            
        self.current_speed_left = new_duty_cycle_l
        self.current_speed_right = new_duty_cycle_r
        

        
    def deinit(self):
        """deinit PWM Pins"""
        print("Deinitializing PWM Pins")
        self.stop()
        utime.sleep(0.1)
        self.left_motor_pin1.deinit()
        self.left_motor_pin2.deinit()
        self.right_motor_pin1.deinit()
        self.right_motor_pin2.deinit()
        