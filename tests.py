import os
import time
import unittest

import ulcd43pct as lcd


class DisplayTestCase(unittest.TestCase):

    def setUp(self):
        self.serial_port = os.getenv('PYCASO_SERIAL_PORT')
        self.serial_speed = int(os.getenv('PYCASO_SERIAL_SPEED'))
        if not self.serial_port:
            raise Exception('Please set the PYCASO_SERIAL_PORT environment variable to run the tests.')
        if not self.serial_speed:
            raise Exception('Please set the PYCASO_SERIAL_SPEED environment variable to run the tests.')
        self.display = lcd.Display()
        self.display.set_serial_port(self.serial_port)
        self.display.set_serial_speed(self.serial_speed)
        self.display.connect()

    def tearDown(self):
        self.display.gfx_BackgroundColour(0)
        self.display.gfx_Cls()
        self.display.close()

    def testClearScreen(self):
        self.assertEqual(self.display.gfx_Cls(), True)

    def testGetModel(self):
        model = self.display.sys_GetModel()
        self.assertEqual('uLCD-43', model[:7])

    def testChangeColour(self):
        self.assertTrue(self.display.gfx_ChangeColour(0, 65535))
        self.assertTrue(self.display.gfx_ChangeColour(65535, 0))

    def testBackgroundColor(self):
        black = 0
        red   = 0b11111 << 11
        green = 0b111111 << 5
        blue  = 0b11111
        self.display.gfx_BackgroundColour(black)
        self.assertEqual(self.display.gfx_Cls(), True)
        self.assertEqual(black, self.display.gfx_BackgroundColour(red))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(red, self.display.gfx_BackgroundColour(green))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(green, self.display.gfx_BackgroundColour(blue))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(blue, self.display.gfx_BackgroundColour(black))

    def testBackgroundColorCycle(self):
        red   = 0b11111 << 11
        green = 0b111111 << 5
        blue  = 0b11111
        r = g = b = 0
        while r <= red:
            self.display.gfx_BackgroundColour(r)
            self.display.gfx_Cls()
            r += (1 << 11)
        while g <= green:
            self.display.gfx_BackgroundColour(g)
            self.display.gfx_Cls()
            g += (1 << 6)
        while b <= blue:
            self.display.gfx_BackgroundColour(b)
            self.display.gfx_Cls()
            b += 1

    def testSleep(self):
        self.assertEqual(self.display.sys_Sleep(2), 0)

    def testSetBaudWait(self):
        for index, baudrate in self.display.BAUD_RATE_INDEX:
            if not baudrate in self.display.SUPPORTED_BAUD_RATES:
                continue
            self.assertEqual(self.display.setbaudWait(baudrate), True)
        self.assertEqual(self.display.setbaudWait(self.serial_speed), True)

    def testContrast(self):
        self.display.gfx_Contrast(0)
        time.sleep(1)
        self.assertEqual(0, self.display.gfx_Contrast(15))


if __name__ == "__main__":
    unittest.main()
