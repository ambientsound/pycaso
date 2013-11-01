import os
import time
import unittest

import ulcd43pct as lcd


class DisplayTestCase(unittest.TestCase):

    BLACK = 0
    RED   = 0b11111 << 11
    GREEN = 0b111111 << 5
    BLUE  = 0b11111

    def setUp(self):
        self.serial_port = os.getenv('PYCASO_SERIAL_PORT')
        self.serial_speed = int(os.getenv('PYCASO_SERIAL_SPEED', 9600))
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

    def testCircle(self):
        MAX = 240
        for rad, color in ((0, self.RED), (1, self.GREEN), (2, self.BLUE)):
            while rad < MAX:
                self.assertTrue(self.display.gfx_Circle((240, 140), rad, color))
                rad += 3

    def testCircleFilled(self):
        for rad, color in ((240, self.RED), (180, self.GREEN), (120, self.BLUE)):
            self.assertTrue(self.display.gfx_CircleFilled((240, 140), rad, color))
            time.sleep(0.33)

    def testLine(self):
        self.assertTrue(self.display.gfx_Line((0, 0), (479, 271), self.GREEN))
        self.assertTrue(self.display.gfx_Line((0, 271), (479, 0), self.RED))
        time.sleep(0.5)

    def testRectangle(self):
        self.assertTrue(self.display.gfx_Rectangle((0, 0), (479, 135), self.GREEN))
        self.assertTrue(self.display.gfx_Rectangle((0, 138), (479, 271), self.RED))
        time.sleep(0.5)

    def testRectangleFilled(self):
        self.assertTrue(self.display.gfx_RectangleFilled((0, 0), (479, 135), self.BLUE))
        self.assertTrue(self.display.gfx_RectangleFilled((0, 138), (479, 271), self.RED))
        time.sleep(0.5)

    def testPolyline(self):
        self.assertTrue(self.display.gfx_Polyline(self.GREEN, (50, 50), (100, 100), (50, 150), (100, 200), (150, 150), (200, 200)))
        time.sleep(0.5)

    def testPolygon(self):
        self.assertTrue(self.display.gfx_Polygon(self.RED, (100, 100), (150, 150), (100, 200)))
        time.sleep(0.5)

    def testPolygonFilled(self):
        self.assertTrue(self.display.gfx_PolygonFilled(self.RED, (100, 100), (150, 150), (100, 200)))
        time.sleep(0.5)

    def testChangeColour(self):
        self.assertTrue(self.display.gfx_ChangeColour(0, 65535))
        self.assertTrue(self.display.gfx_ChangeColour(65535, 0))

    def testBackgroundColor(self):
        self.display.gfx_BackgroundColour(self.BLACK)
        self.assertEqual(self.display.gfx_Cls(), True)
        self.assertEqual(self.BLACK, self.display.gfx_BackgroundColour(self.RED))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(self.RED, self.display.gfx_BackgroundColour(self.GREEN))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(self.GREEN, self.display.gfx_BackgroundColour(self.BLUE))
        self.assertEqual(self.display.gfx_Cls(), True)
        time.sleep(0.25)
        self.assertEqual(self.BLUE, self.display.gfx_BackgroundColour(self.BLACK))

    def testBackgroundColorCycle(self):
        r = g = b = 0
        while r <= self.RED:
            self.display.gfx_BackgroundColour(r)
            self.display.gfx_Cls()
            r += (1 << 11)
        while g <= self.GREEN:
            self.display.gfx_BackgroundColour(g)
            self.display.gfx_Cls()
            g += (1 << 6)
        while b <= self.BLUE:
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
