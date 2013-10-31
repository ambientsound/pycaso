import os
import unittest

import ulcd43pct as lcd


class DisplayTestCase(unittest.TestCase):

    def setUp(self):
        self.serial_port = os.getenv('PYCASO_SERIAL_PORT')
        if not self.serial_port:
            raise Exception('Please set the PYCASO_SERIAL_PORT environment variable to run the tests.')
        self.display = lcd.Display()
        self.display.set_serial_port(self.serial_port)
        self.display.connect()

    def tearDown(self):
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
        self.display.gfx_BackgroundColour(0)
        self.assertEqual(self.display.gfx_BackgroundColour(0), 0)

    def testSleep(self):
        self.assertEqual(self.display.sys_Sleep(1), 0)


if __name__ == "__main__":
    unittest.main()
