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

    def detect_serial_speed(self):
        self.ser.setTimeout(0)
        for index, rate in self.BAUD_RATE_INDEX:
            self.ser.setBaudrate(rate)
            self.ser.flushInput()
            try:
                if self.sys_GetModel():
                    self.serial_speed = rate
                    return rate
            except:
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

    def send_ack(self, buf):
        """
        Write buffer to serial device and check for ACK. Throws an exception if ACK is not received.
        """
        assert self.ser.write(buf) == len(buf)
        self.ser.flush()
        if not self.get_ack():
            raise Exception('Command error, received ERR')
        return True

    def recv_word(self):
        """
        Return a WORD value from serial.
        """
        return self.unpack_word(self.ser.read(2))

    def send_args_ack(self, buf, *args):
        """
        Send buf along with the WORDs in args, expecting an ACK response.
        """
        buf += ''.join([self.pack_word(x) for x in args])
        return self.send_ack(buf)

    def send_args_recv_word(self, buf, *args):
        """
        Send buf along with the WORDs in args, expecting an ACK response and a WORD.
        """
        self.send_args_ack(buf, *args)
        return self.recv_word()

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
    CIRCLE = '\xff\xc3'
    CIRCLE_FILLED = '\xff\xc2'
    LINE = '\xff\xc8'
    RECTANGLE = '\xff\xc5'
    RECTANGLE_FILLED = '\xff\xc4'
    POLYLINE = '\x00\x15'
    POLYGON = '\x00\x13'
    POLYGON_FILLED = '\x00\x14'
    TRIANGLE = '\xff\xbf'
    TRIANGLE_FILLED = '\xff\xa9'
    ORBIT = '\x00\x12'
    BACKGROUND_COLOUR = '\xff\xa4'
    CONTRAST = '\xff\x9c'

    def gfx_Cls(self):
        return self.send_ack(self.CLEAR_SCREEN)

    def gfx_ChangeColour(self, old_colour, new_colour):
        return self.send_args_ack(self.CHANGE_COLOUR, old_colour, new_colour)

    def gfx_Circle(self, point, rad, colour):
        return self.send_args_ack(self.CIRCLE, point[0], point[1], rad, colour)

    def gfx_CircleFilled(self, point, rad, colour):
        return self.send_args_ack(self.CIRCLE_FILLED, point[0], point[1], rad, colour)

    def gfx_Line(self, point1, point2, colour):
        return self.send_args_ack(self.LINE, point1[0], point1[1], point2[0], point2[1], colour)

    def gfx_Rectangle(self, point1, point2, colour):
        return self.send_args_ack(self.RECTANGLE, point1[0], point1[1], point2[0], point2[1], colour)

    def gfx_RectangleFilled(self, point1, point2, colour):
        return self.send_args_ack(self.RECTANGLE_FILLED, point1[0], point1[1], point2[0], point2[1], colour)

    def gfx_Polyline(self, colour, *args):
        points = [x for x,y in args] + [y for x,y in args] + [colour]
        return self.send_args_ack(self.POLYLINE, len(points)/2, *points)

    def gfx_Polygon(self, colour, *args):
        points = [x for x,y in args] + [y for x,y in args] + [colour]
        return self.send_args_ack(self.POLYGON, len(points)/2, *points)

    def gfx_PolygonFilled(self, colour, *args):
        if len(args) < 3:
            raise Exception('gfx_PolygonFilled needs at least 3 points.')
        points = [x for x,y in args] + [y for x,y in args] + [colour]
        return self.send_args_ack(self.POLYGON_FILLED, len(points)/2, *points)

    def gfx_Triangle(self, point1, point2, point3, colour):
        return self.send_args_ack(self.TRIANGLE, point1[0], point1[1], point2[0], point2[1], point3[0], point3[1], colour)

    def gfx_TriangleFilled(self, point1, point2, point3, colour):
        return self.send_args_ack(self.TRIANGLE_FILLED, point1[0], point1[1], point2[0], point2[1], point3[0], point3[1], colour)

    def gfx_Orbit(self, angle, distance):
        self.send_args_ack(self.ORBIT, angle, distance)
        return struct.unpack('>HH', self.ser.read(4))

    def gfx_BackgroundColour(self, colour):
        return self.send_args_recv_word(self.BACKGROUND_COLOUR, colour)

    def gfx_Contrast(self, contrast):
        """
        From the documentation:
        uLCD-43 supports Contrast values from 1-15 and 0 to turn the Display off.
        """
        contrast &= 15
        return self.send_args_recv_word(self.CONTRAST, contrast)


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
        return self.send_args_recv_word(self.SLEEP, seconds)


    ###############################
    ###  5.10: System Commands  ###
    ###############################

    GET_DISPLAY_MODEL = '\x00\x1a'

    def sys_GetModel(self):
        c = self.send_args_recv_word(self.GET_DISPLAY_MODEL)
        return self.ser.read(c)



# Detect baud rate and set to max

if __name__ == "__main__":
    import os
    d = Display()
    d.set_serial_port(os.getenv('PYCASO_SERIAL_PORT'))
    d.set_serial_speed(int(os.getenv('PYCASO_SERIAL_SPEED', 9600)))
    d.connect()
    try:
        speed = d.detect_serial_speed()
        target = 115200
    except:
        print "Device doesn't seem to be responding. Try running detection again."
        exit(1)
    print "Device running at %d baud" % speed
    if speed != target:
        print "Switching to %d baud" % target
        if d.setbaudWait(target):
            print "Device running at %d baud" % speed
            print "export PYCASO_SERIAL_SPEED=%d" % target
            exit(0)
        print "Device doesn't seem to be responding. Try running detection again."
        exit(1)
    print "export PYCASO_SERIAL_SPEED=%d" % target
    exit(0)
