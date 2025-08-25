#https://github.com/crsf-wg/crsf/wiki/Packet-Types
class Crsf():
    # https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_GPS
    CRSF_SYNC = 0xC8
    '''Telemetry Item
    int32_t latitude in degrees * 1e7, big-endian
    e.g. 28.0805804N sent as 0x10BCC1AC / 280805804
    int32_t longitude
    int16_t ground speed in km/h * 10, big-endian
    e.g. 88 km/h sent as 0x0370 / 880
    e.g. 15m/s sent as 0x021C / 540
    int16_t ground course / GPS heading in degrees * 100, big-endian
    e.g. 90 degrees sent as 0x2328 / 9000
    uint16_t GPS altitude in meters + 1000m, big-endian
    e.g. 0m sent as 0x03E8 / 1000
    e.g. 10m sent as 0x03F2 / 1010
    e.g. -10m sent as 0x03DE / 990
    uint8_t satellite count'''
    GPS = 0x02
    
    #https://github.com/crsf-wg/crsf/wiki/Packet-Types
    VARIO = 0x07
    #https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_BATTERY_SENSOR
    # int16_t voltage in dV (Big Endian)
    # e.g. 25.2V sent as 0x00FC / 252
    # e.g. 3.7V sent as 0x0025 / 37
    # e.g. 3276.7V sent as 0x7FFF / 32767
    # int16_t current in dA (Big Endian)
    # e.g. 18.9A sent as 0x00BD / 189
    # e.g. 109.4A sent as 0x0446 / 1094
    # int24_t used capacity in mAh
    # e.g. 2199mAh used sent as 0x0897 / 2199
    # int8_t estimated battery remaining in percent (%)
    # e.g. 100% full battery sent as 0x64 / 100
    # e.g. 20% battery remaining sent as 0x14 / 20

    BATTERY_SENSOR = 0x08
    #https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_BARO_ALTITUDE
    BARO_ALT = 0x09
    #https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_HEARTBEAT
    HEARTBEAT = 0x0B
    #
    VIDEO_TRANSMITTER = 0x0F
    #https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_LINK_STATISTICS
    LINK_STATISTICS = 0x14
    #https://github.com/crsf-wg/crsf/wiki/CRSF_FRAMETYPE_RC_CHANNELS_PACKED
    RC_CHANNELS_PACKED = 0x16
    ATTITUDE = 0x1E
    FLIGHT_MODE = 0x21
    DEVICE_INFO = 0x29
    CONFIG_READ = 0x2C
    CONFIG_WRITE = 0x2D
    RADIO_ID = 0x3A
    
    def __init__(self, p_uart=None):
        self.rc=''
        self.channels=[0 for jj in range(16)]
        self.text=''
        self.newRCData=None
        self.uart = p_uart
    
    
    @staticmethod
    def crc8_dvb_s2(crc, a) -> int:
        crc = crc ^ a
        for ii in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0xD5
            else:
                crc = crc << 1
        return crc & 0xFF

    @staticmethod
    def crc8_data(data) -> int:
        crc = 0
        for a in data:
            crc = Crsf.crc8_dvb_s2(crc, a)
        return crc

    def crsf_validate_frame(frame) -> bool:
        return Crsf.crc8_data(frame[2:-1]) == frame[-1]
    
    @staticmethod
    def signed_byte(b):
        return b - 256 if b >= 128 else b




                        
    def tick(self) -> int:
        self.newRCData = -99
        if self.uart is None:
           self.newRCData=-10
           return self.newRCData
        if not self.uart.any() :
           self.newRCData=-9
           return self.newRCData
            
        
        input_buffer=self.uart.read()
        if len(input_buffer) < 3:
           self.newRCData=-8
           return self.newRCData
        if input_buffer[0]!=Crsf.CRSF_SYNC:
           self.newRCData=-7
           return self.newRCData
        
        expected_len = input_buffer[1] + 2
        if expected_len > 64 or expected_len < 4:
           self.newRCData=-6
           return self.newRCData
        if len(input_buffer) < expected_len:
           self.newRCData=-5
           return self.newRCData
        
        self.data = input_buffer[:expected_len]
        input_buffer = input_buffer[expected_len:]
        self.packet_validate=Crsf.crsf_validate_frame(self.data)
        if not self.packet_validate:
           packet = ' '.join(map(hex, self.data))
           print(f"CRC error: {packet}")
           self.newRCData=-4
           return self.newRCData
        
        if self.data[2]  != Crsf.RC_CHANNELS_PACKED:
           self.newRCData=-3
           return self.newRCData
        
        self.handleCrsfPacket()
        return self.newRCData


    def sentBattery(self,p_voltage,p_current, p_capacity,p_percent):
        buffer = bytearray([Crsf.CRSF_SYNC, 10, Crsf.BATTERY_SENSOR, p_voltage//256, p_voltage%256, p_current//256,p_current%256, 0,p_capacity//256,p_capacity%256,p_percent, 180])
        buffer[-1]=Crsf.crc8_data(buffer[2:-1])
        self.uart.write(buffer)
        #self.uart.write(bytearray([Crsf.CRSF_SYNC,0x0B, Crsf.BATTERY_SENSOR,  0x00, 0x25, 0x00, 0xBD, 0x00, 0x08, 0x97,0x14, Crsf.crc8_data([0x08])]))



    def handleCrsfPacket(self):
        self.newRCData=-1
        self.ptype = self.data[2]
        if self.ptype == Crsf.GPS:
            self.lat = int.from_bytes(self.data[3:7], byteorder='big', signed=True) / 1e7
            self.lon = int.from_bytes(self.data[7:11], byteorder='big', signed=True) / 1e7
            self.gspd = int.from_bytes(self.data[11:13], byteorder='big', signed=True) / 36.0
            self.hdg = int.from_bytes(self.data[13:15], byteorder='big', signed=True) / 100.0
            self.alt = int.from_bytes(self.data[15:17], byteorder='big', signed=True) - 1000
            self.sats = self.data[17]
            self.text=(f"GPS: Pos={self.lat} {self.lon} GSpd={self.gspd:0.1f}m/s Hdg={self.hdg:0.1f} Alt={self.alt}m Sats={self.sats}")
            self.newRCData=0
        elif self.ptype == Crsf.VARIO:
            self.vspd = int.from_bytes(self.data[3:5], byteorder='big', signed=True) / 10.0
            print(f"VSpd: {self.vspd:0.1f}m/s")
            self.newRCData=0
        elif self.ptype == Crsf.ATTITUDE:
            self.pitch = int.from_bytes(self.data[3:5], byteorder='big', signed=True) / 10000.0
            self.roll = int.from_bytes(self.data[5:7], byteorder='big', signed=True) / 10000.0
            self.yaw = int.from_bytes(self.data[7:9], byteorder='big', signed=True) / 10000.0
            self.text=(f"Attitude: Pitch={self.pitch:0.2f} Roll={self.roll:0.2f} Yaw={self.yaw:0.2f} (rad)")
        elif self.ptype == Crsf.BARO_ALT:
            self.alt = int.from_bytes(self.data[3:7], byteorder='big', signed=True) / 100.0
            self.text=(f"Baro Altitude: {self.alt}m")
            self.newRCData=0
        elif self.ptype == Crsf.LINK_STATISTICS:
            self.rssi1 = Crsf.signed_byte(self.data[3])
            self.rssi2 = Crsf.signed_byte(self.data[4])
            self.lq = self.data[5]
            self.snr = Crsf.signed_byte(self.data[6])
            self.text=(f"RSSI={self.rssi1}/{self.rssi2}dBm LQ={self.lq:03}")
            self.newRCData=0
        elif self.ptype == Crsf.BATTERY_SENSOR:
            self.vbat = int.from_bytes(self.data[3:5], byteorder='big', signed=True) / 10.0
            self.curr = int.from_bytes(self.data[5:7], byteorder='big', signed=True) / 10.0
            self.mah = self.data[7] << 16 | self.data[8] << 7 | self.data[9]
            self.pct = self.data[10]
            self.text=(f"Battery: {self.vbat:0.2f}V {self.curr:0.1f}A {self.mah}mAh {self.pct}%")
            self.newRCData=0
        elif self.ptype == Crsf.RC_CHANNELS_PACKED:
            zz=''
            kk=self.data[3:25]  
            for ii in kk:
                #zz='{:0>{w}}'.format(bin(ii)[2:], w=8)+zz
                zz='{0:08b}'.format(ii)+zz

                #https://github.com/alexeystn/python-scripts/blob/master/crossfire/decode_crsf_protocol.py
                # if packet[0] == 22:  # 0x16 = CRSF_FRAMETYPE_RC_CHANNELS_PACKED
                #     packet = packet[1:-1]  # remove type and crc
                #     packet_bin_8 = ['{0:08b}'.format(i)[::-1] for i in packet]  # [::-1] reverse
                #     packet_bin_full = ''.join(packet_bin_8)
                #     packet_bin_11 = [packet_bin_full[11*i:11*(i+1)] for i in range(16)]
                #     rc_packet = [int(b[::-1], 2) for b in packet_bin_11]

            if zz!=self.rc and len(zz)==176:
                self.channels=[sum([(1<<(10-ii) if (zz[(15-jj)*11:(16-jj)*11])[ii]=='1' else 0) for ii in range(11)]) for jj in range(16) ]
                #print('->',CHANNELS[E_SWITCH],CHANNELS[LEFT_VERTICAL],CHANNELS[LEFT_HORIZONTAL],CHANNELS[RIGHT_VERTICAL],CHANNELS[RIGHT_HORIZONTAL])
                #print('22->',CHANNELS)
                self.rc=zz
                self.newRCData=1
            else:
                self.newRCData=0
        else :
            #print("unknown ptype",ptype)
            self.newRCData=0
    
        
 



