# uart_rx32.py - 22.07.2022
#
# Prüft das Startbit 2x, an der Stelle des Stopbits muss der Pegel high sein.
# Das Ende der Übertragung wird erkannt, wenn nach dem letzten Byte innerhalb
# von 1 Takt kein neues Startbit empfangen wird.
#
# Liest bis zu 32 Byte ein und löst erst am Ende der Übertragung einen Interrupt aus.
# Achtung -
# nur geeignet für Sendungen, die komplett in die 32 Bytes der Fifos passen !
#
# Werden mehr als 32 Byte empfangen, dann würde alles nach dem 32. Byte ignoriert.
# Darum wird ein IndexError ausgelöst und die Statemachine deactiviert.
# 
from machine import Pin
import uarray as arr
from rp2 import PIO, StateMachine, asm_pio

# ----------------------------------------------------------------------------
#
# Diese Version prüft wx das Startbit, 1x das Stopbit und die nachfolgende Pause
# Die Datenbits werden jeweils 1x in der Bitmitte abgetastet.
# Jedes Bit hat eine Länge von 15 Takten -> PIO-Takt = Baud * 15   
@asm_pio(
        in_shiftdir=PIO.SHIFT_RIGHT,
        autopush=True,
        push_thresh=32,
        fifo_join=PIO.JOIN_RX) 

def uart_rx():
    label("restart")  
    mov(isr, null)            #  1 Bei einem Fehler sicherheitshalber das ISR zurücksetzen   
    wait(0, pin, 0)           #  2 Warten auf eine fallende Flanke

    set(x, 31)                #  3 Zähler für die 8 Fifos  
 
    wrap_target()             
    set(y, 7)                 #  4 Zähler für die Bits pro Byte
                              #    Das Signal ist mindestens 4 Takte gesetzt
    jmp(pin, "restart")   [5] #  5 - Fehler, wenn hier das Startbit nicht mehr low ist

                              #    Der 5. Takt ist die Mitte des Startbits
    jmp(pin, "restart")   [6] #  6 - Fehler, wenn hier das Startbit nicht mehr low 
    nop()                 [6] #  7 warten bis die Bit-Mitte des 1. Bits erreicht ist
                              
    label("next_bit")
    in_(pins, 1)          [6] #  8 Den Pegel einlesen und nach
    nop()                 [6] #  9
    jmp(y_dec, "next_bit")    # 10 weiteren 15 Takten das nächste Bit einlesen
    
    jmp(pin, "stop_bit_1")    # 11 Das Stopbit muss high sein 
    jmp("restart")            # 12 wenn nicht gesetzt, dann ist das ein Fehler
    
    label("stop_bit_1")
    jmp(pin, "byte_end")      # 13 Das Stopbit muss high sein, 
    jmp("restart")            # 14 wenn nicht gesetzt, dann ist das ein Fehler                         
    
    label("byte_end")         #    ein Byte ist komplett
                              #    Autopush wird aktiv
              
    jmp(x_dec, "end_1")       # 15 wenn weniger als 32 Byte
                              #    dann auf das nächste Startbit prüfen
                           
                              #    es sind 32 Bytes eingelesens
                              #    separate Warteschleife auf ein Startbit
                              #    Wenn noch ein Startbit folgt, dann sind
                              #    mehr als 32 Bit gesendet worden -> Fehler
    set(y, 3)                 # 16 Wartezeit auf ein Startbit laden 7 * 3 Takte
    label("fifo_1")
    
    jmp(y_dec, "fifo_2")      # 17  solange der Zähler nicht abgelaufen
    jmp("fifo_out")           # 18  der Zähler ist abgelaufen, y = 0
    
    label("fifo_2")
    jmp(pin, "fifo_1")        # 19 solange der Pin High weiter downcounten
                              #    der Pin ist low, da folgen noch weitere Bits
                            
    label("fifo_out")         #    hier gehts weiter X=32, Y=0 / >0 neues Byte folgte
    jmp("read_end_1")         # 20
                              #    wenn alle 7 Byte geschreiben
    
    # -- auf nachfolgendes folgendes Starbit prüfen --------------------------
    
    label("end_1")
    set(y, 4)                 # 21 Wartezeit nach dem Stopbit nach 'y'
                              #    wenn innerhalb dieser Zeit der Lavel nicht
                              #    auf gnd geht, dann ist die Übertragung beendet
    label("end_2")
    jmp(y_dec, "end_3")       # 22 Zähler Wartezeit decrementieren
    jmp("read_end")           # 23
    
    label("end_3")            #
    jmp(pin, "end_2")         # 24 hier prüfen, ob eine fallende Flanke auftrat 
    wrap()                    #    wenn ja, dann das nächste Byte einlesen
 
    label("read_end")  
    push(noblock)             # 25 den letzten Datensatz pushen, ggf. mit leeren Bytes
    label("read_end_1")       #    Einsprung, wenn 8 Fifo*s geschrieben wurden
                              #    hier ist kein push() mehr möglich 
    in_(x, 8)                 # 26 X- und Y-Register sichern
    in_(y, 8)                 # 27
    irq(rel(0))               # 28 den Interrupt auslösen
    push(block)               # 29 Das X-Register enthält jetzt einen Zähler der Bytes
                              #    Das Y-Register FF, wenn kein Startbit mehr erkannt wurde
                              #    einen anderen Wert, wenn ein Startbit erkannt wurde,
                              #    das bedeutet, dass die Sendung nicht komplett empfangen wurde.
    jmp("restart")            # 30
    
class UART_RX_32(object):
    def __init__(self, statemachine, rx_pin, baud=9600):
        self.sm = StateMachine(statemachine, uart_rx,
                in_base=Pin(rx_pin, Pin.IN, Pin.PULL_UP),
                jmp_pin=Pin(rx_pin, Pin.IN, Pin.PULL_UP),
                freq=baud * 15)
        
        self.sm.irq(self._irq_handler)
        self.rx_word_buffer = arr.array("I", [0] * 9)
        self.rx_idx = 0
        self.rx_cnt = 0

    def active(self, state=1):
        self.sm.active(1 if state else 0)
         
    def recv(self):
        # Liefert die Anzahl der empfangenen Words - bzw. 0
        return self.rx_cnt

    def _irq_handler(self, _):
        # Nachdem das Ende der Sendung erkannt ist, wird ein Interrupt ausgelöst
        # der diese ISR ausführt.
        # Hier werden die Fifos ausgelesen, danach ist der Empfänger wieder
        # empfangsbereit.
        self.sm.active(0)
        self.rx_idx = 0
        recv = self.sm.rx_fifo()
        while recv:
            recv -= 1
            self.rx_word_buffer[self.rx_idx] = self.sm.get()
            self.rx_idx += 1
            
        self.sm.active(1) 
        # wenn mehr als 27 Byte empfangen wurden, dann steckt noch ein 9.Word
        # blockend im Fifo, das wird hier abgeholt
        if self.rx_idx > 7:
            if self.sm.rx_fifo():
                self.rx_word_buffer[self.rx_idx] = self.sm.get() 
                self.rx_idx += 1
 
        # setzt die ISR und die Couner für shift_on/out zurück 
        # ->>>>>>>self.sm.restart()
        # Im letzten Word steht das X- und das Y-Register (0xYYXX ____):
        # Das X-Register liefert die Anzahl der empfangenen BYtes
        # das Y-Register liefert 0xFF (= 0 - 1), wenn kein Startbit mehr erkannt wurde,
        # sonst einen Zähler >= 0
        self.rx_idx -= 1
        status = self.rx_word_buffer[self.rx_idx] >> 16  # (0x____ YYXX)
        self.rx_cnt =  32 -  ((status + 1) & 0xFF)

        if self.rx_cnt == 32:
            if not status & 0xFF00 == 0xFF00:
                self.sm.active(0)
                self.rx_cnt = 0
                raise IndexError("received more than 32 Byte")

    def get_data(self, rx_byte_buffer):
        # Die 32-Bit-Fifo-Daten "rx_word_buffer" in der richtigen Folge in das
        # Array of Bytes "rx_byte_buffer" kopieren.
        # Ein Sonderfall muss berücksichtigt werden, wenn rx_cnt == 32
        idx = 0
        for j in range(self.rx_idx):
            temp = self.rx_word_buffer[j]
            if j < self.rx_idx - 1 or self.rx_cnt == 32:
                for i in range(4):
                    rx_byte_buffer[idx] = temp & 0xFF
                    idx += 1
                    temp >>= 8
                    
            # im letzten Word ggf. die Füllbytes am rechten Rand entfernen
            # beim Empfangen werden die Bits nach rechts ins Fifo geshiftet.
            # Wenn weniger als 4 Byte empfangen wurden, sind also am rechten
            # Rand noch Füllbytes, die ignoriert werden müssen.
            elif not self.rx_cnt == 32:
                # wieviele Füllbytes sind im letzten Buffer enthalten ?
                empty =  4 - self.rx_cnt % 4
 
                tmp = empty
                # die rechts stehenden und nutzlosen Bytes rausshiften
                while tmp:           
                    tmp -= 1
                    temp >>= 8
        
                # jetzt noch die verbleibenden Bytes umkopieren
                for i in range(4 - empty):
                    rx_byte_buffer[idx] = temp & 0xFF
                    idx += 1
                    temp >>= 8
                
        cnt = self.rx_cnt
        self.rx_cnt = 0
        return cnt
                    
if __name__ == "__main__":
    
    # -- Einstellungen für die Tests  ------------------------
    #BAUD = 9600
    BAUD = 115200
    
    # ---------------------------------------------------------
    
    rx_1 = UART_RX_32(statemachine=0, rx_pin = 15, baud=BAUD)
    rx_2 = UART_RX_32(statemachine=1, rx_pin = 14, baud=BAUD)
    rx_3 = UART_RX_32(statemachine=4, rx_pin = 13, baud=BAUD)
    rx_4 = UART_RX_32(statemachine=5, rx_pin = 12, baud=BAUD) 
    
    rx_1.active(1)
    rx_2.active(1)
    rx_3.active(1)
    rx_4.active(1)
    
    # Array für das Abholen der 8 Fifo-Worte als Bytes
    buffer=arr.array("B", [0] * 32)
    
    print("Waiting for data   ...  Ctrl-C to stop\n")
    
    try:
        while True:
            #time.sleep(.2)
            if rx_1.recv():

                cnt = rx_1.get_data(buffer)
                print("1", end = " ")
                try:
                    print(buffer[:cnt].decode(), cnt)
                except:
                    print(buffer[:cnt], cnt)
                        
            if rx_2.recv():
                cnt = rx_2.get_data(buffer)
                print("2", end = " ")
                try:
                    print(buffer[:cnt].decode(), cnt)
                except:
                    print(buffer[:cnt], cnt)
                        
            if rx_3.recv():
                cnt = rx_3.get_data(buffer)
                print("3", end = " ")
                try:
                    print(buffer[:cnt].decode(), cnt)
                except:
                    print(buffer[:cnt], cnt)
                        
            if rx_4.recv():
                cnt = rx_4.get_data(buffer)
                print("4", end = " ")
                try:
                    print(buffer[:cnt].decode(), cnt)
                except:
                    print(buffer[:cnt], cnt)
               
    except KeyboardInterrupt:
        pass
             
    rx_1.active(0)
    rx_2.active(0)
    rx_3.active(0)
    rx_4.active(0)
    
    print("\ndone")