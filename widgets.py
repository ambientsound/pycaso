"""
UI widget library for the ulcd43pct Display class.
"""

class Widget(object):
    ORIENTATION_SINGLE = 0
    ORIENTATION_HORIZONTAL = 1
    ORIENTATION_VERTICAL = 2

    def __init__(self, **kwargs):
        self.children = []
        self.parent = None
        self.envelope = None
        self.dirty = True
        self.children_fits = False
        self.orientation = self.ORIENTATION_SINGLE

        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        if not self.envelope:
            if self.parent:
                self.envelope = self.parent.envelope
            else:
                self.envelope = (0, 0, 0, 0)

    def _draw(self, display):
        pass

    def draw(self, display):
        self.mark_dirty()
        self.draw_dirty(display)

    def draw_dirty(self, display):
        if not self.children_fits:
            self.fit_children()
        if self.dirty:
            self._draw(display)
        self.dirty = False
        for child in self.children:
            child.draw_dirty(display)

    def mark_dirty(self):
        self.dirty = True
        for child in self.children:
            child.mark_dirty()

    def unfit(self):
        self.children_fits = False
        for child in self.children:
            child.unfit()

    def set_envelope(self, envelope=None):
        self.envelope = envelope
        self.mark_dirty()
        self.unfit()
    
    def add_child(self, child):
        if self.orientation == self.ORIENTATION_SINGLE and len(self.children) > 0:
            raise Exception('Cannot add more than one child to a non-grid widget')
        child.parent = self
        child.display = self.display
        self.children.append(child)
        self.mark_dirty()
        self.unfit()

    def fit_children(self):
        if self.orientation == self.ORIENTATION_SINGLE:
            return
        self.children_fits = True
        x1, y1, x2, y2 = self.envelope
        if self.orientation == self.ORIENTATION_HORIZONTAL:
            width_per_child = self.width() / len(self.children)
            height_per_child = self.height()
        elif self.orientation == self.ORIENTATION_VERTICAL:
            width_per_child = self.width()
            height_per_child = self.height() / len(self.children)
        for child in self.children:
            x = x1
            y = y1
            if self.orientation == self.ORIENTATION_HORIZONTAL:
                x2 = round(x1 + width_per_child)
                x1 = x2 + 1
            elif self.orientation == self.ORIENTATION_VERTICAL:
                y2 = round(y1 + height_per_child)
                y1 = y2 + 1
            child.set_envelope((x, y, x2, y2))

    def width(self):
        return self.envelope[2] - self.envelope[0]

    def height(self):
        return self.envelope[3] - self.envelope[1]


class Canvas(Widget):

    def __init__(self, display, **kwargs):
        self.background = 0
        self.active = False
        self.display = display
        super(Canvas, self).__init__(envelope=(0, 0, display.RES_X, display.RES_Y), **kwargs)

    def _draw(self, display):
        display.gfx_RectangleFilled(self.envelope[:2], self.envelope[2:], self.background)


class XGrid(Widget):

    def __init__(self, **kwargs):
        super(XGrid, self).__init__(**kwargs)
        self.orientation = self.ORIENTATION_HORIZONTAL


class YGrid(Widget):

    def __init__(self, **kwargs):
        super(YGrid, self).__init__(**kwargs)
        self.orientation = self.ORIENTATION_VERTICAL


class Button(Widget):

    def __init__(self, **kwargs):
        self.background = (1 << 16) - 1
        self.foreground = 0
        self.text = ''
        self.text_envelope = None
        self.char_height = 3
        self.char_width = 2
        self.char_size = None
        super(Button, self).__init__(**kwargs)

    def _get_char_size(self, display):
        display.txt_Width(self.char_width)
        display.txt_Height(self.char_height)
        self.char_size = (display.charwidth('e'), display.charheight('e'))

    def fit_children(self):
        super(Button, self).fit_children()
        if not self.char_size:
            self._get_char_size(self.display)
        x = (self.envelope[2]-(self.width()/2)) - ((len(self.text)*self.char_size[0])/2)
        y = (self.envelope[3]-(self.height()/2)) - (self.char_size[1]/2)
        x = x if x >= 0 else 0
        y = y if y >= 0 else 0
        self.text_envelope = (x, y)

    def _draw(self, display):
        display.gfx_Panel(display.PANEL_STATE_RAISED, self.envelope[:2], self.envelope[2]-self.envelope[0], self.envelope[3]-self.envelope[1], self.background)
        display.gfx_MoveTo(self.text_envelope)
        display.putStr(self.text)
