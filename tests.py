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
        self.serial_baudrate = os.getenv('PYCASO_SERIAL_BAUDRATE', 9600)
        if not self.serial_port:
            raise Exception('Please set the PYCASO_SERIAL_PORT environment variable to run the tests.')
        if not self.serial_baudrate:
            raise Exception('Please set the PYCASO_SERIAL_BAUDRATE environment variable to run the tests.')
        self.display = lcd.Display(self.serial_port, self.serial_baudrate)
        self.display.connect()

    def tearDown(self):
        self.display.gfx_BackgroundColour(0)
        self.display.gfx_Cls()
        self.display.close()


class SysTestCase(DisplayTestCase):

    def testGetModel(self):
        model = self.display.sys_GetModel()
        self.assertEqual('uLCD-43', model[:7])

    def testSleep(self):
        self.assertEqual(self.display.sys_Sleep(2), 0)

    def testSetBaudWait(self):
        for index, baudrate in self.display.BAUD_RATE_INDEX:
            if not baudrate in self.display.SUPPORTED_BAUD_RATES:
                continue
            self.assertEqual(self.display.setbaudWait(baudrate), True)
        self.assertEqual(self.display.setbaudWait(self.serial_speed), True)


class TextTestCase(DisplayTestCase):

    def testMoveCursor(self):
        self.assertTrue(self.display.txt_MoveCursor(0, 0))

    def testPutCh(self):
        self.assertTrue(self.display.txt_MoveCursor(0, 0))
        for ch in 'All your base are belong to us':
            self.assertTrue(self.display.putCH(ch))

    def testPutStr(self):
        self.assertTrue(self.display.txt_MoveCursor(0, 0))
        self.assertTrue(self.display.putStr('All your base are belong to us'))

    def testCharWidth(self):
        self.display.txt_FontID(2)
        self.assertEquals(8, self.display.charwidth('e'))

    def testCharHeight(self):
        self.display.txt_FontID(2)
        self.assertEquals(12, self.display.charheight('e'))

    def testFGColour(self):
        self.display.txt_FGcolour(self.BLACK)
        self.assertEquals(self.BLACK, self.display.txt_FGcolour(self.RED))

    def testBGColour(self):
        self.display.txt_BGcolour(self.BLACK)
        self.assertEquals(self.BLACK, self.display.txt_BGcolour(self.RED))

    def testFontID(self):
        self.display.txt_FontID(0)
        self.assertEquals(0, self.display.txt_FontID(1))

    def testTxtWidth(self):
        self.display.txt_Width(2)
        self.assertEquals(2, self.display.txt_Width(1))

    def testTxtHeight(self):
        self.display.txt_Height(2)
        self.assertEquals(2, self.display.txt_Height(1))

    def testTxtXGap(self):
        self.display.txt_Xgap(2)
        self.assertEquals(2, self.display.txt_Xgap(1))

    def testTxtYGap(self):
        self.display.txt_Ygap(2)
        self.assertEquals(2, self.display.txt_Ygap(1))

    def testTxtBold(self):
        self.display.txt_Bold(True)
        self.assertEquals(True, self.display.txt_Bold(False))

    def testTxtInverse(self):
        self.display.txt_Inverse(True)
        self.assertEquals(True, self.display.txt_Inverse(False))

    def testTxtItalic(self):
        self.display.txt_Italic(True)
        self.assertEquals(True, self.display.txt_Italic(False))

    def testTxtOpacity(self):
        self.display.txt_Opacity(True)
        self.assertEquals(True, self.display.txt_Opacity(False))

    def testTxtUnderline(self):
        self.display.txt_Underline(True)
        self.assertEquals(True, self.display.txt_Underline(False))

    def testTxtAttributes(self):
        self.display.txt_Attributes(0)
        modes = [
                self.display.TXT_ATTRIBUTE_BOLD | self.display.TXT_ATTRIBUTE_INVERSE,
                self.display.TXT_ATTRIBUTE_ITALIC | self.display.TXT_ATTRIBUTE_UNDERLINED
                ]
        self.assertEquals(0, self.display.txt_Attributes(modes[0]))
        self.assertEquals(modes[0], self.display.txt_Attributes(modes[1]))
        self.assertEquals(modes[1], self.display.txt_Attributes(0))


class TouchTestCase(DisplayTestCase):

    def testTouch(self):
        self.assertTrue(self.display.touch_Set(self.display.TOUCH_SET_MODE_DISABLE))
        self.assertTrue(self.display.touch_Set(self.display.TOUCH_SET_MODE_INIT))
        self.assertTrue(self.display.touch_DetectRegion((50, 50), (200, 200)))
        self.assertTrue(self.display.touch_Set(self.display.TOUCH_SET_MODE_RESET))
        self.assertEquals(self.display.touch_Get(self.display.TOUCH_GET_MODE_STATUS), self.display.TOUCH_STATUS_NOTOUCH)

    def testYourFinger(self):
        self.display.touch_Set(self.display.TOUCH_SET_MODE_INIT)
        self.display.touch_Set(self.display.TOUCH_SET_MODE_RESET)
        self.display.gfx_BevelWidth(8)
        self.display.gfx_Button(self.display.BUTTON_STATE_RAISED, (100, 100), self.GREEN, self.BLACK, 0, 3, 4, "Touch me!")
        max_x = self.display.gfx_Get(self.display.GFX_GET_OBJECT_RIGHT)
        max_y = self.display.gfx_Get(self.display.GFX_GET_OBJECT_BOTTOM)
        iterations = 0
        while self.display.touch_Get(self.display.TOUCH_GET_MODE_STATUS) != self.display.TOUCH_STATUS_PRESS:
            iterations += 1
            if iterations > 100:
                raise Exception('No touch detected, too slow?')
            time.sleep(0.05)
        x = self.display.touch_Get(self.display.TOUCH_GET_MODE_GET_X)
        y = self.display.touch_Get(self.display.TOUCH_GET_MODE_GET_Y)
        self.display.gfx_CircleFilled((x, y), 20, self.RED)
        self.assertTrue(100 <= x <= max_x)
        self.assertTrue(100 <= y <= max_y)
        time.sleep(0.1)


class GfxTestCase(DisplayTestCase):

    def testClearScreen(self):
        self.assertEqual(self.display.gfx_Cls(), True)

    def testChangeColour(self):
        self.assertTrue(self.display.gfx_ChangeColour(0, 65535))
        self.assertTrue(self.display.gfx_ChangeColour(65535, 0))

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



if __name__ == "__main__":
    unittest.main()
