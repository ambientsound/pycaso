import serial
import struct

class Display(object):

    ser = None
    serial_port = None
    serial_speed = 9600

    ACK = '\x06'
    ERR = '\x15'

    ############################
    ###  Internal functions  ###
    ############################

    def pack_byte(self, byte):
        return struct.pack('>B', byte)

    def unpack_byte(self, byte):
        return struct.unpack('>B', byte)[0]

    def pack_word(self, word):
        return struct.pack('>H', word)

    def unpack_word(self, word):
        return struct.unpack('>H', word)[0]

    def set_serial_port(self, serial_port):
        self.serial_port = serial_port

    def set_serial_speed(self, serial_speed):
        self.serial_speed = serial_speed

    def discover_serial_speed(self):
        self.ser.setTimeout(0)
        for index, rate in self.BAUD_RATE_INDEX:
            self.ser.setBaudrate(rate)
            self.ser.flushInput()
            try:
                if self.sys_GetModel():
                    self.serial_speed = rate
                    return rate
            except:
                print 'failed', rate
                pass
        raise Exception('No match in any baud rate')

    def get_ack(self):
        """
        Returns True if serial response was an ACK reply, False if not.
        """
        ack = self.ser.read(1)
        if ack == self.ACK:
            return True
        self.ser.flushInput()
        if ack == self.ERR:
            return False
        raise Exception("Unknown reply: '%s'" % ack.encode('hex'))

    def write_recv(self, buf, return_bytes = 0):
        """
        Write buffer to serial device, check for ACK, and return more data if available.
        """
        assert self.ser.write(buf) == len(buf)
        self.ser.flush()
        if not self.get_ack():
            raise Exception('Command error, received ERR')
        if return_bytes <= 0:
            return True
        return self.ser.read(return_bytes)

    def write_recv_word(self, buf):
        return self.unpack_word(self.write_recv(buf, 2))

    def connect(self):
        if not self.serial_port:
            raise Exception("Serial port not set. Use set_serial_port() before calling connect().")
        if self.ser:
            raise Exception("Serial port already open.")
        self.ser = serial.Serial(self.serial_port)
        self.ser.open()
        self.ser.setBaudrate(self.serial_speed)
        self.ser.setParity('N')
        self.ser.setByteSize(8)
        self.ser.setStopbits(1)
        self.ser.setTimeout(5)
        self.ser.flushInput()
        self.ser.flushOutput()
        return True

    def reset(self):
        self.ser.setTimeout(0)
        self.ser.write('\x00\x00\x00')
        self.ser.read(1024)
        self.ser.setTimeout(5)
        return True

    def close(self):
        self.ser.close()
        self.ser = None
        return True


    ################################
    ###  5.2: Graphics Commands  ###
    ################################

    CLEAR_SCREEN = '\xff\xcd'
    CHANGE_COLOUR = '\xff\xb4'
    BACKGROUND_COLOUR = '\xff\xa4'
    CONTRAST = '\xff\x9c'

    def gfx_Cls(self):
        return self.write_recv(self.CLEAR_SCREEN)

    def gfx_ChangeColour(self, old_colour, new_colour):
        buf = self.CHANGE_COLOUR + self.pack_word(old_colour) + self.pack_word(new_colour)
        return self.write_recv(buf)

    def gfx_BackgroundColour(self, colour):
        buf = self.BACKGROUND_COLOUR + self.pack_word(colour)
        return self.write_recv_word(buf)

    def gfx_Contrast(self, contrast):
        """
        From the documentation:
        uLCD-43 supports Contrast values from 1-15 and 0 to turn the Display off.
        """
        contrast &= 15
        buf = self.CONTRAST + self.pack_word(contrast)
        return self.write_recv_word(buf)


    ####################################################
    ###  5.4: Serial (UART) Communications Commands  ###
    ####################################################

    SET_BAUD_RATE = '\x00\x26'
    BAUD_RATE_INDEX = [ (0, 110), (1, 300), (2, 600), (3, 1200), (4, 2400),
        (5, 4800), (6, 9600), (7, 14400), (8, 19200), (9, 31250), (10, 38400),
        (11, 56000), (12, 57600), (13, 115200), (14, 128000), (15, 256000),
        (16, 300000), (17, 375000), (18, 500000), (19, 600000) ]
    SUPPORTED_BAUD_RATES = [ 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800,
            2400, 4800, 9600, 19200, 38400, 57600, 115200 ]

    def setbaudWait(self, baudrate):
        for index, rate in self.BAUD_RATE_INDEX:
            if rate == baudrate:
                if rate not in self.SUPPORTED_BAUD_RATES:
                    raise Exception('Baud rate is supported by device, but probably not by OS.')
                self.ser.write(self.SET_BAUD_RATE + self.pack_word(index))
                self.ser.flush()
                self.ser.setBaudrate(baudrate)
                self.serial_speed = baudrate
                self.ser.flushInput()
                return self.get_ack()
        raise Exception("Unsupported baud rate.")


    #############################
    ###  5.5: Timer Commands  ###
    #############################

    SLEEP = '\xff\x3b'

    def sys_Sleep(self, seconds):
        return self.write_recv_word(self.SLEEP + self.pack_word(seconds))


    ###############################
    ###  5.10: System Commands  ###
    ###############################

    GET_DISPLAY_MODEL = '\x00\x1a'

    def sys_GetModel(self):
        c = self.write_recv_word(self.GET_DISPLAY_MODEL)
        return self.ser.read(c)
