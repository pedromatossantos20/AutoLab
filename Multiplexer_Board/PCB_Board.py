import serial
import time
import os

import win32com.client

class Multiplexer_Board():

    def __init__(self, baudrate=19200, timeout=2000,rest_time=0.1,offline = False,port="COM6"):
        self.port=port
        self._detect_mcp2200_port()
        self.rest_time=rest_time
        
        
        if self.port is not None:
            self.ser = serial.Serial(self.port, baudrate=baudrate, timeout=timeout)
        elif offline == False:
            raise Exception("MCP2200 device not found")
    
    def _detect_mcp2200_port(self):
        port_data = os.popen('mode').read()
        wmi = win32com.client.GetObject ("winmgmts:")
    
        for usb in wmi.InstancesOf ("Win32_SerialPort"):
            if usb.DeviceID==self.port:
                print("Found Board!")
                return usb.DeviceID
            print(usb.DeviceID)
        else:
            return None


    def is_open(self):
        return self.ser.is_open

    def open(self):
        if not self.is_open():
            self.ser.open()

    def close(self):
        if self.is_open():
            self.ser.close()

    def write(self, data):
        if self.is_open():
            self.ser.write(data)
        else:
            raise Exception("Serial port is not open")
        

    def set_channel_to_pin(self,channel,pin):    
        pin = self.correct_pin_number(pin)    
        pin -= 1
        
        multiplexer_ID = pin >> 4
        effective_pin=pin%16
        
        
        # Y0 - Y7
        decoded_bits = bin(effective_pin)[2:].zfill(4)[::-1] + bin(0b1111 - (1 << multiplexer_ID))[2:][::-1]

        # Start bit + channel + pin + Keep last chip off
        data0 = '1' + bin(channel)[2:].zfill(3)[::-1] + decoded_bits[:4]
        data1 = '1' + bin(channel)[2:].zfill(3)[::-1] + decoded_bits[4:]

        
        data = bytearray([int(data0[::-1],2), int(data1[::-1],2)])
        
        #print(data0, '   ', data1, '   ', data)
        time.sleep(self.rest_time)
        self.write(data)
        return data
    
    def set_channel_to_probe(self,channel,probe): #Not working, device isn't latchable for now
        channel_address = format(channel, '03b')   
        multiplexer_ID = (0 << 7) + (1 << 6) + (1 << 5) + (1 << 4)
        effective_pin=probe

        data = '01' + channel_address + format(effective_pin, '04b') + '101' + channel_address + format(multiplexer_ID, '08b')[:4] + '1'
        self.write(int(data))
        return data
            
    
    def correct_pin_number(self,pin):
        if pin > 0 and pin < 9:
            return pin
        elif pin > 8 and pin <17:
            return pin
        elif pin > 16 and pin <25:
            return pin + 16     
        elif pin > 24 and pin <33:
            return pin - 8
        elif pin > 32 and pin <41:
            return pin - 8
        else:
            error_message= "Invalid Pin Number"
            return (-1, error_message)

    def is_open(self):
        return self.ser.is_open

    def open(self):
        if not self.is_open():
            self.ser.open()

    def close(self):
        if self.is_open():
            self.ser.close()

    def write(self, data):
        if self.is_open():
            self.ser.write(data)
        else:
            raise Exception("Serial port is not open")