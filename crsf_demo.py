#https://medium.com/@mike_polo/parsing-crsf-protocol-from-a-flight-controller-with-a-raspberry-pi-for-telemetry-data-79e9426ff943
import os
from machine import UART, Pin


#uart = UART(0, baudrate=460800, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))

#uart = UART(0, baudrate=425000, bits=8, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
uart = UART(1, baudrate=420000, bits=8, parity=None, stop=1, tx=Pin(8), rx=Pin(9))


import time

CRSF_SYNC = 0xC8
CHANNELS=[0 for jj in range(16)]



#https://github.com/crsf-wg/crsf/wiki/Packet-Types
class PacketsTypes():
    # https://github.com/crsf-wg/crsf/wiki/CRimport bitstruct.c SF_FRAMETYPE_GPS
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

def crc8_dvb_s2(crc, a) -> int:
    crc = crc ^ a
    for ii in range(8):
        if crc & 0x80:
            crc = (crc << 1) ^ 0xD5
        else:
            crc = crc << 1
    return crc & 0xFF

def crc8_data(data) -> int:
    crc = 0
    for a in data:
        crc = crc8_dvb_s2(crc, a)
    return crc

def crsf_validate_frame(frame) -> bool:
    return crc8_data(frame[2:-1]) == frame[-1]

def signed_byte(b):
    return b - 256 if b >= 128 else b


def zfl(s):
  # Pads the provided string with leading 0's to suit the specified 'chrs' length
  # Force # characters, fill with leading 0's
  return '{:0>{w}}'.format(bin(s)[2:], w=8)


rc=''

def handleCrsfPacket(ptype, data):
    global rc
    if ptype == PacketsTypes.GPS:
        lat = int.from_bytes(data[3:7], byteorder='big', signed=True) / 1e7
        lon = int.from_bytes(data[7:11], byteorder='big', signed=True) / 1e7
        gspd = int.from_bytes(data[11:13], byteorder='big', signed=True) / 36.0
        hdg = int.from_bytes(data[13:15], byteorder='big', signed=True) / 100.0
        alt = int.from_bytes(data[15:17], byteorder='big', signed=True) - 1000
        sats = data[17]
        print(f"GPS: Pos={lat} {lon} GSpd={gspd:0.1f}m/s Hdg={hdg:0.1f} Alt={alt}m Sats={sats}")
    elif ptype == PacketsTypes.VARIO:
        vspd = int.from_bytes(data[3:5], byteorder='big', signed=True) / 10.0
        print(f"VSpd: {vspd:0.1f}m/s")
    elif ptype == PacketsTypes.ATTITUDE:
        pitch = int.from_bytes(data[3:5], byteorder='big', signed=True) / 10000.0
        roll = int.from_bytes(data[5:7], byteorder='big', signed=True) / 10000.0
        yaw = int.from_bytes(data[7:9], byteorder='big', signed=True) / 10000.0
        print(f"Attitude: Pitch={pitch:0.2f} Roll={roll:0.2f} Yaw={yaw:0.2f} (rad)")
    elif ptype == PacketsTypes.BARO_ALT:
        alt = int.from_bytes(data[3:7], byteorder='big', signed=True) / 100.0
        print(f"Baro Altitude: {alt}m")
    elif ptype == PacketsTypes.LINK_STATISTICS:
        rssi1 = signed_byte(data[3])
        rssi2 = signed_byte(data[4])
        lq = data[5]
        snr = signed_byte(data[6])
        print(f"RSSI={rssi1}/{rssi2}dBm LQ={lq:03}")
    elif ptype == PacketsTypes.BATTERY_SENSOR:
        vbat = int.from_bytes(data[3:5], byteorder='big', signed=True) / 10.0
        curr = int.from_bytes(data[5:7], byteorder='big', signed=True) / 10.0
        mah = data[7] << 16 | data[8] << 7 | data[9]
        pct = data[10]
        print(f"Battery: {vbat:0.2f}V {curr:0.1f}A {mah}mAh {pct}%")
    elif ptype == PacketsTypes.RC_CHANNELS_PACKED:
        zz=''
        kk=data[3:25]  
        for ii in kk:
            zz='{:0>{w}}'.format(bin(ii)[2:], w=8)+zz #+
        if zz!=rc and len(zz)==176:
            CHANNELS=[sum([(1<<(10-ii) if (zz[(15-jj)*11:(16-jj)*11])[ii]=='1' else 0) for ii in range(11)]) for jj in range(16) ]
            rc=zz
            print('->',CHANNELS[0],CHANNELS[1],CHANNELS[2],CHANNELS[3])
            
        
    else :
        print("unknown ptype",ptype)
        
 


input_buffer = bytearray()
while True:
     if uart.any() :
        #input_buffer.extend(uart.read())
         input_buffer=uart.read()
     else:
        time.sleep(0.010)
     if len(input_buffer) > 2:
        if input_buffer[0]!=CRSF_SYNC:
            input_buffer = []
     if len(input_buffer) > 2:       
            expected_len = input_buffer[1] + 2
            
            if expected_len > 64 or expected_len < 4:
                input_buffer = []
            elif len(input_buffer) >= expected_len:
                single_packet = input_buffer[:expected_len]
                input_buffer = input_buffer[expected_len:]
                #print(single_packet)
                if not crsf_validate_frame(single_packet):
                    packet = ' '.join(map(hex, single_packet))
                    print(f"CRC error: {packet}")
                else:
                  if single_packet[2]  == PacketsTypes.RC_CHANNELS_PACKED:
                    handleCrsfPacket(single_packet[2], single_packet)


