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

    def testChangeColour(self):
        self.assertTrue(self.display.gfx_ChangeColour(0, 65535))
        self.assertTrue(self.display.gfx_ChangeColour(65535, 0))

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

    def testTriangle(self):
        self.assertTrue(self.display.gfx_Triangle((100, 100), (150, 150), (100, 200), self.GREEN))
        time.sleep(0.5)

    def testTriangleFilled(self):
        self.assertTrue(self.display.gfx_TriangleFilled((100, 100), (150, 150), (100, 200), self.GREEN))
        time.sleep(0.5)

    def testOrbit(self):
        self.display.gfx_MoveTo((0, 0))
        self.assertEquals(self.display.gfx_Orbit(40, 60), (45, 37))

    def testPixel(self):
        self.assertTrue(self.display.gfx_PutPixel((40, 60), self.GREEN))
        self.assertEquals(self.display.gfx_GetPixel((40, 60)), self.GREEN)

    def testMoveTo(self):
        self.assertTrue(self.display.gfx_MoveTo((40, 60)))

    def testLineTo(self):
        self.assertTrue(self.display.gfx_LineTo((30, 40)))

    def testClipping(self):
        self.assertTrue(self.display.gfx_Clipping(True))
        self.assertTrue(self.display.gfx_Clipping(False))

    def testClipWindow(self):
        self.display.gfx_Clipping(True)
        self.assertTrue(self.display.gfx_ClipWindow((50, 50), (150, 150)))
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 30), self.GREEN, self.RED, 0, 5, 5, "Hello world")
        time.sleep(0.5)

    def testSetClipRegion(self):
        self.assertTrue(self.display.gfx_SetClipRegion())

    def testEllipse(self):
        self.assertTrue(self.display.gfx_Ellipse((120, 120), 40, 80, self.RED))
        time.sleep(0.5)

    def testEllipseFilled(self):
        self.assertTrue(self.display.gfx_EllipseFilled((120, 120), 80, 40, self.GREEN))
        time.sleep(0.5)

    def testButton(self):
        self.assertTrue(self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 30), self.GREEN, self.RED, 0, 5, 5, "Hello world"))
        time.sleep(0.5)

    def testPanel(self):
        self.assertTrue(self.display.gfx_Panel(self.display.PANEL_STATE_RAISED, (30, 30), 100, 100, self.GREEN))
        time.sleep(0.5)

    def testSlider(self):
        self.display.gfx_BevelWidth(2)
        self.assertEquals(self.display.gfx_Slider(self.display.SLIDER_MODE_RAISED, (30, 30), (400, 90), self.GREEN, 100, 0), 52)
        self.display.gfx_RectangleFilled((51, 100), (53, 200), self.RED)
        self.display.gfx_TriangleFilled((42, 100), (62, 100), (52, 90), self.RED)
        time.sleep(0.5)

    def testScreenCopyPaste(self):
        self.display.gfx_EllipseFilled((120, 120), 80, 40, self.GREEN)
        self.assertTrue(self.display.gfx_ScreenCopyPaste((0, 0), (240, 0), 240, 136))
        self.assertTrue(self.display.gfx_ScreenCopyPaste((0, 0), (0, 136), 240, 136))
        self.assertTrue(self.display.gfx_ScreenCopyPaste((0, 0), (240, 136), 240, 136))
        time.sleep(0.5)

    def testBevelShadow(self):
        self.display.gfx_BevelShadow(0)
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 30), self.GREEN, self.RED, 0, 5, 5, "Hello world")
        self.assertEquals(self.display.gfx_BevelShadow(2), 0)
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 130), self.RED, self.GREEN, 0, 3, 3, "Why hello thar")
        time.sleep(0.5)

    def testBevelWidth(self):
        self.display.gfx_BevelWidth(0)
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 30), self.GREEN, self.RED, 0, 5, 5, "Hello world")
        self.assertEquals(self.display.gfx_BevelWidth(15), 0)
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (30, 130), self.RED, self.GREEN, 0, 3, 3, "Why hello thar")
        time.sleep(0.5)

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

    def testOutlineColor(self):
        self.display.gfx_OutlineColour(self.BLACK)
        self.assertEqual(self.display.gfx_OutlineColour(self.GREEN), self.BLACK)
        self.display.gfx_CircleFilled((120, 120), 80, self.RED)
        time.sleep(0.5)

    def testContrast(self):
        self.display.gfx_Contrast(0)
        time.sleep(1)
        self.assertEqual(0, self.display.gfx_Contrast(15))

    def testFrameDelay(self):
        self.display.gfx_FrameDelay(15)
        self.assertEqual(15, self.display.gfx_FrameDelay(0))

    def testLinePattern(self):
        rows = [i for i in xrange(0, 272) if i % 2]
        pats = [ 0b1010101010101010, 0b0101010101010101 ]
        self.display.gfx_LinePattern(0)
        self.assertEqual(0, self.display.gfx_LinePattern(pats[0]))
        for y in rows:
            self.display.gfx_Line((0, y), (479, y), self.BLUE)
        self.assertEqual(pats[0], self.display.gfx_LinePattern(pats[1]))
        for y in rows:
            self.display.gfx_Line((0, y), (479, y), self.RED)

    def testScreenMode(self):
        last_mode = self.display.SCREEN_MODE_LANDSCAPE
        self.display.gfx_ScreenMode(last_mode)
        for mode in self.display.SCREEN_MODES:
            self.assertEqual(last_mode, self.display.gfx_ScreenMode(mode))
            self.display.gfx_TriangleFilled((70, 70), (120, 120), (70, 170), self.GREEN)
            last_mode = mode
            time.sleep(0.1)
        self.display.gfx_ScreenMode(self.display.SCREEN_MODE_LANDSCAPE)

    def testTransparency(self):
        self.display.gfx_Transparency(False)
        self.assertEqual(False, self.display.gfx_Transparency(True))
        self.assertEqual(True, self.display.gfx_Transparency(False))

    def testTransparentColour(self):
        self.display.gfx_Transparency(True)
        self.display.gfx_TransparentColour(self.RED)
        self.display.gfx_OutlineColour(self.BLACK)
        self.display.gfx_CircleFilled((240, 140), 100, self.GREEN)
        self.display.gfx_RectangleFilled((220, 120), (260, 160), self.RED)
        self.assertEqual(self.RED, self.display.gfx_TransparentColour(self.BLACK))
        time.sleep(0.5)

    def testGfxSet(self):
        self.assertTrue(self.display.gfx_Set(self.display.GFX_SET_OBJECT_COLOUR, self.RED))
        self.assertTrue(self.display.gfx_Set(self.display.GFX_SET_PAGE_DISPLAY, 0))
        self.assertTrue(self.display.gfx_Set(self.display.GFX_SET_PAGE_READ, 0))
        self.assertTrue(self.display.gfx_Set(self.display.GFX_SET_PAGE_WRITE, 0))

    def testGfxGet(self):
        self.display.gfx_ScreenMode(self.display.SCREEN_MODE_LANDSCAPE)
        self.display.gfx_Panel(self.display.PANEL_STATE_RAISED, (0, 0), 100, 100, self.GREEN)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_X_MAX), 479)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_Y_MAX), 271)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_OBJECT_LEFT), 32000)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_OBJECT_TOP), 32000)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_OBJECT_RIGHT), 33536)
        self.assertEquals(self.display.gfx_Get(self.display.GFX_GET_OBJECT_BOTTOM), 33536)

    def testSleep(self):
        self.assertEqual(self.display.sys_Sleep(2), 0)

    def testSetBaudWait(self):
        for index, baudrate in self.display.BAUD_RATE_INDEX:
            if not baudrate in self.display.SUPPORTED_BAUD_RATES:
                continue
            self.assertEqual(self.display.setbaudWait(baudrate), True)
        self.assertEqual(self.display.setbaudWait(self.serial_speed), True)



if __name__ == "__main__":
    unittest.main()
