from machine import UART, Pin
import time
import uarray as arr




LTCRC8_MAXIM=[0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83,   0xC2, 0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41,
0x9D, 0xC3, 0x21, 0x7F, 0xFC, 0xA2, 0x40, 0x1E,   0x5F, 0x01, 0xE3, 0xBD, 0x3E, 0x60, 0x82, 0xDC,
0x23, 0x7D, 0x9F, 0xC1, 0x42, 0x1C, 0xFE, 0xA0,   0xE1, 0xBF, 0x5D, 0x03, 0x80, 0xDE, 0x3C, 0x62,
0xBE, 0xE0, 0x02, 0x5C, 0xDF, 0x81, 0x63, 0x3D,   0x7C, 0x22, 0xC0, 0x9E, 0x1D, 0x43, 0xA1, 0xFF,
0x46, 0x18, 0xFA, 0xA4, 0x27, 0x79, 0x9B, 0xC5,   0x84, 0xDA, 0x38, 0x66, 0xE5, 0xBB, 0x59, 0x07,
0xDB, 0x85, 0x67, 0x39, 0xBA, 0xE4, 0x06, 0x58,   0x19, 0x47, 0xA5, 0xFB, 0x78, 0x26, 0xC4, 0x9A,
0x65, 0x3B, 0xD9, 0x87, 0x04, 0x5A, 0xB8, 0xE6,   0xA7, 0xF9, 0x1B, 0x45, 0xC6, 0x98, 0x7A, 0x24,
0xF8, 0xA6, 0x44, 0x1A, 0x99, 0xC7, 0x25, 0x7B,   0x3A, 0x64, 0x86, 0xD8, 0x5B, 0x05, 0xE7, 0xB9,
0x8C, 0xD2, 0x30, 0x6E, 0xED, 0xB3, 0x51, 0x0F,   0x4E, 0x10, 0xF2, 0xAC, 0x2F, 0x71, 0x93, 0xCD,
0x11, 0x4F, 0xAD, 0xF3, 0x70, 0x2E, 0xCC, 0x92,   0xD3, 0x8D, 0x6F, 0x31, 0xB2, 0xEC, 0x0E, 0x50,
0xAF, 0xF1, 0x13, 0x4D, 0xCE, 0x90, 0x72, 0x2C,   0x6D, 0x33, 0xD1, 0x8F, 0x0C, 0x52, 0xB0, 0xEE,
0x32, 0x6C, 0x8E, 0xD0, 0x53, 0x0D, 0xEF, 0xB1,   0xF0, 0xAE, 0x4C, 0x12, 0x91, 0xCF, 0x2D, 0x73,
0xCA, 0x94, 0x76, 0x28, 0xAB, 0xF5, 0x17, 0x49,   0x08, 0x56, 0xB4, 0xEA, 0x69, 0x37, 0xD5, 0x8B,
0x57, 0x09, 0xEB, 0xB5, 0x36, 0x68, 0x8A, 0xD4,   0x95, 0xCB, 0x29, 0x77, 0xF4, 0xAA, 0x48, 0x16,
0xE9, 0xB7, 0x55, 0x0B, 0x88, 0xD6, 0x34, 0x6A,   0x2B, 0x75, 0x97, 0xC9, 0x4A, 0x14, 0xF6, 0xA8,
0x74, 0x2A, 0xC8, 0x96, 0x15, 0x4B, 0xA9, 0xF7,   0xB6, 0xE8, 0x0A, 0x54, 0xD7, 0x89, 0x6B, 0x35]



def AddToCRC(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b^crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C # this means crc ^= 140
    return crc

# the same LTCRC8_MAXIM
def crc8_MAXIM(hex_data):
    msg = bytearray(hex_data)
    check = 0
    for i in msg:
        check = AddToCRC(i, check)
    return check


def get_full_command(command) -> bytes:
    _cmd = bytes(command, "utf-8")
    _crc = crc8_MAXIM(_cmd)
    
    full_command = _cmd + bytes([_crc])
    #print('get_full_command:',[hex(ll)  for ll in full_command])  
    return full_command

class ddsm(object):
    def __init__(self, uart, rx_PIO,rotate_dir=1 ):
        self.rxPio = rx_PIO
        self.uart = uart
        self.rotate_dir= rotate_dir
        self.buffer=arr.array("B", [0] * 32)
        self.id=self.getId()
        print('id=',self.id)
        self.mode=self.getMode()
        print('mode=',self.mode)
        self.setMode(0)
        print('mode=',self.mode)
        
    def getAnswer(self):
      time.sleep(0.05)
      if self.rxPio.recv():
        cnt = self.rxPio.get_data(self.buffer)
        #print('ret', cnt, [hex(ll)  for ll in self.buffer])
        time.sleep(0.05)
        return self.buffer
      return ''
    
    def ddsmCmd(self, cmd):
      _cmd=get_full_command(cmd)
      _decr=''
      _val=''
      if bytearray(_cmd)[1]==160:
        _decr='SetMode :'+str(bytearray(_cmd)[2])
      elif bytearray(_cmd)[1]==100:
        _decr='Drive'
        _val0=bytearray(_cmd)[2]*256+bytearray(_cmd)[3]
        if _val0>32767:
           _val0= -(65536+-_val0)
        _decr+=(' v='+str(_val0))
        
      elif bytearray(_cmd)[1]==200:
        _decr='GetID'
      elif bytearray(_cmd)[1]==0x75        :
        _decr='GetMode'
      elif bytearray(_cmd)[1]==0x74        :
        _decr='GetFeedback'

      else:
        _decr='?'
        print('ddsmCmd: cmd=',[hex(ll)  for ll in _cmd])  

      #print('ddsmCmd:',_decr,'ID=',bytearray(_cmd)[0])
      l=self.uart.write(_cmd)
      return self.getAnswer()
      
    
    def getId(self):
      _cmd0=b'\xC8\x64\x00\x00\x00\x00\x00\x00\x00'
      return bytearray(self.ddsmCmd(_cmd0))[0]


    # mode 0 stop 1 pos, 2 loop
    #0x00: set to open loop not use
    #0x01: break
    #0x02: set to velocity loop
    #0x03: set to position loop
    def setDrive0(self,driveMode=1,val=10, feedb=2, acctime=0): 
      #Velocity loop command (－210～210 rpm)
      #01 64 FF CE 00 00 00 00 00 DA (-5rpm)
      #01 64 00 00 00 00 00 FF 00 D1 brake
      vel  =b'\x00\x64\x00\x00\x00\x00\x00\x00\x00' # pos=0
      cmd_0=bytearray(vel)
      cmd_0[0]=self.id
      cmd_0[4]=0 #Feedback 1 content 0X01 - speed value 0X02 - bus current 0X03 - position value
      cmd_0[5]=feedb #Feedback 2 content
      if driveMode==1: # stop
        cmd_0[7]=255
        cmd_0[2]=0 #Speed/position set high 8 bits
        cmd_0[3]=0 #Speed/position set low 8 bits
        cmd_0[6]=acctime #Acceleration time Acceleration time: valid in the speed loop mode, the acceleration time per 1rpm, the unit is 0.1ms. When it is set to 1, the acceleration time per 1rpm is 0.1ms. When it is set to 10, the acceleration time per 1rpm is 10*0.1 ms=1ms. When set to 0, the default is 1, and the acceleration time per 1rpm is 0.1ms.
      else:
        cmd_0[7]=0
        if driveMode==2: #loop mode －210～210 rpm
            #Acceleration time: valid in the speed loop mode, the acceleration time per 1rpm, the unit is 0.1ms. When it is set to 1, the acceleration time per 1rpm is 0.1ms. When it is set to 10, the acceleration time per 1rpm is 10*0.1 ms=1ms. When set to 0, the default is 1, and the acceleration time per 1rpm is 0.1ms.
            if val<-210:
                print('bad value for mode 2, less -210')
                return None
            if val>210:
                print('bad value for mode 2, greater 210')
                return None
            m_dir=1 if val>=0 else 0
            if self.rotate_dir<0:
                m_dir=1-m_dir
            
            if m_dir<1:
                vv=65536-((abs(val)*10)%65535)
            else:
                vv=((abs(val)*10)%65535)
            #01 64 FF CE 00 00 00 00 00 DA (-5rpm)
            #01 64 FF 9C 00 00 00 00 00 9A (-10rpm)
            #01 64 00 00 00 00 00 00 00 50 (0rpm)
            #01 64 00 32 00 00 00 00 00 D3 (5rpm)
            #01 64 00 64 00 00 00 00 00 4F (10rpm)
            cmd_0[2]=vv//256 #Speed/position set high 8 bits
            cmd_0[3]=vv%256 #Speed/position set low 8 bits
        elif driveMode==3: #pos mode 0～32767 --todo calc for self.rotate_dir==-1
            if val<0:
                 print('bad value for mode 1')
                 return None
            vv=((val)%65535)
            #01 64 00 00 00 00 00 00 00 50 (0)
            #01 64 27 10 00 00 00 00 00 57 (10000)
            #01 64 4E 20 00 00 00 00 00 5E (20000)
            #01 64 75 30 00 00 00 00 00 A7 (30000)            
            cmd_0[2]=vv//256 #Speed/position set high 8 bits
            cmd_0[3]=vv%256 #Speed/position set low 8 bits
         
      cmd_1=bytes(cmd_0)
      print('setDrive', [hex(ll)  for ll in cmd_1])
      self.ddsmCmd(cmd_1)

    def setBrake(self):
        return self.setDrive0(val=0,driveMode=1, feedb=2, acctime=10) # 100*0.1ms

    #Protocol 3: Motor Mode Switch Sending Protocol
    #Data Field	DATA[0]	DATA[1]	DATA[2]	DATA[3]	DATA[4]	DATA[5]	DATA[6]	DATA[7]	DATA[8]	DATA[9]
    #Content	ID	0xA0	Mode Value	0	0	0	0	0	0	CRC8
    #Motor feedback:

    #Data Field	DATA[0]	DATA[1]	DATA[2]	DATA[3]	DATA[4]	DATA[5]	DATA[6]	DATA[7]	DATA[8]	DATA[9]
    #Content	ID	0xA0	Mode Value	0	0	0	0	0	0	CRC8
    #Mode value:
    #0x00: set to open loop
    #0x02: set to velocity loop
    #0x03: set to position loop

    def setMode(self, mode=0):
        #01 64 FF CE 00 00 00 00 00 DA (-5rpm)
        vel  =b'\x00\xA0\x00\x00\x00\x00\x00\x00\x00' # pos=0
        cmd_0=bytearray(vel)
        cmd_0[0]=self.id
        if mode<0 or mode>3 or mode==1:
          print('bad mode not in (0,2,3)')
          return None
        
        cmd_0[2]=mode
        cmd_1=bytes(cmd_0)
        res=self.ddsmCmd(cmd_1)
        self.mode=mode
        return res
    
    def getMode(self):
      #01 64 FF CE 00 00 00 00 00 DA (-5rpm)
      vel  =b'\x00\x75\x00\x00\x00\x00\x00\x00\x00' # pos=0
      cmd_0=bytearray(vel)
      cmd_0[0]=self.id
      self.mode=bytearray(self.ddsmCmd(bytes(cmd_0)) )[2]
      return self.mode
      
    
    #Send to the motor:

    #Data Field	DATA[0]	DATA[1]	DATA[2]	DATA[3]	DATA[4]	DATA[5]	DATA[6]	DATA[7]	DATA[8]	DATA[9]
    #Content	ID	0x74	0	0	0	0	0	0	0	CRC8
    #Motor feedback:

    #Data Field	DATA[0]	DATA[1]	DATA[2]	DATA[3]	DATA[4]	DATA[5]	DATA[6]	DATA[7]	DATA[8]	DATA[9]
    #Content	ID	0x74	Mileage laps high 8 bits	Mileage laps second high 8 bits	Mileage laps second low 8 bits	Mileage laps low 8 bits	Position high 8 bits	Position low 8 bits	Error code	CRC8
    #Mileage laps: Loop range -2147483467 to 2147483467, reset to 0 when power on it again.
    #Position value: 0~65535 corresponds to 0~360°
    #Error code:

    def getFeedback(self):    
        vel  =b'\x00\x74\x00\x00\x00\x00\x00\x00\x00' # pos=0
        cmd_0=bytearray(vel)
        cmd_0[0]=self.id
        res_ =bytearray(self.ddsmCmd(bytes(cmd_0) ) )
        milleage=res_[2]*256*256*256+res_[3]*256*256+res_[4]*256+res_[5]
        pos=res_[6]*256+res_[7]
        return milleage,pos    

    def setId(self,id):
        set_id  =b'\xAA\x55\x53\x01\x00\x00\x00\x00\x00' #id=1
        set_id_0=bytearray(set_id)
        set_id_0[3]=id
        _cmd0=bytes(set_id_0)
        _cmd=get_full_command(_cmd0)
        for i in range(5):
            l=uart0.write(_cmd)
            print(_cmd, l)
            time.sleep(0.075)
        uartr=self.getAnswer()
        print('setId: id', bytearray(uartr)[0])
        return bytearray(uartr)[0]    















    



    

    




    
    
                 
        
        
    
    

    
        
        

    
    

