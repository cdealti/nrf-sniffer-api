import logging, serial, collections
import serial.tools.list_ports as list_ports
import Exceptions
import time

class Uart:
    def __init__(self, portnum = None, useByteQueue = False):
        self.ser = serial.Serial(
                    port         = portnum,
                    baudrate     = 460800,
                    bytesize     = serial.EIGHTBITS,
                    parity       = serial.PARITY_NONE,
                    stopbits     = serial.STOPBITS_ONE,
                    timeout      = None, #seconds
                    #write_timeout= None, #changed in 3.0
                    writeTimeout= None,
                    rtscts       = True
                    )

        self.buffer = bytearray()
        self.bufferIndex = 0

    def __del__(self):
        if self.ser:
            logging.info("closing UART")
            self.ser.close()
        
    def switchBaudRate(self, newBaudRate):
        self.ser.baudrate = newBaudRate

    def readByte(self, timeout = None):
        result = None
        if self.bufferIndex >= len(self.buffer):
            if self.ser.timeout != timeout:
                try:
                    self.ser.timeout = timeout
                except ValueError:
                    logging.exception("Invalid UART read timeout: %d. Continuing.", timeout)
            self.buffer.extend(self.ser.read(self.ser.inWaiting() or 1))
        if self.bufferIndex < len(self.buffer):
            result = self.buffer[self.bufferIndex]
            self.bufferIndex += 1
        if len(self.buffer) > 4096:
            self.buffer = self.buffer[self.bufferIndex:]
            self.bufferIndex = 0
        if result is None:
            raise Exceptions.SnifferTimeout("Packet read timed out.")
        return result
        
    def writeList(self, array, timeout = None):
        nBytes = 0
        if timeout != self.ser.writeTimeout:
            try:
                self.ser.writeTimeout = timeout
            except ValueError:
                logging.exception("Invalid UART write timeout: %d. Continuing.", timeout)
        try:
            nBytes = self.ser.write(array)
        except:
            self.ser.close()
            raise
        
        return nBytes

def list_serial_ports():
    # Scan for available ports.
    return list_ports.comports()

# Convert a list of ints (bytes) into an ASCII string
def listToString(list):
    str = ""
    for i in list:
        str+=chr(i)
    return str

