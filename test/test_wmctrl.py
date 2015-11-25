import py
import subprocess
import time
from wmctrl import Window

class Xchild(object):
    cmd = None
    ARGS = []
    sleep = 0.5

    def __init__(self, *args):
        arglist = [self.CMD, '-name', self.NAME] + list(args)
        self.child = subprocess.Popen(arglist)
        time.sleep(self.sleep)

    def __del__(self):
        self.child.kill()

class Apps:
    class get_xclock(Xchild):
        CMD = 'xclock'
        NAME = 'xclock-for-pytest'

    class get_xfontsel(Xchild):
        CMD = 'xfontsel'
        NAME = 'xfontsel-for-pytest'

def get_win(name, *args):
    get_app = getattr(Apps, 'get_%s' % name)
    xapp = get_app(*args)
    win = Window.by_name(get_app.NAME)
    return win[0], xapp

def test_list():
    xclock = Apps.get_xclock()
    wins = Window.list()
    names = [win.wm_name for win in wins]
    assert xclock.NAME in names

def test_attributes():
    win, xclock = get_win('xclock', '-geometry', '100x200+0+0')
    assert win.wm_name == xclock.NAME
    assert win.wm_class == xclock.NAME + '.XClock'
    assert win.w == 100
    assert win.h == 200
    # measure the width and the height of WM decorations
    ofs_x = win.x
    ofs_y = win.y
    xclock.child.kill()
    win, xclock = get_win('xclock', '-geometry', '+30+40')
    assert win.x == 30 + ofs_x
    assert win.y == 40 + ofs_y

def test_activate():
    orig = Window.get_active()
    win, xfontsel = get_win('xfontsel', '-geometry', '+0+0')
    win.activate()
    time.sleep(0.5)
    active = Window.get_active()
    assert active.id == win.id
    orig.activate()
    time.sleep(0.5)
    active = Window.get_active()
    assert active.id == orig.id

def test_resize_and_move():
    win, xclock = get_win('xclock', '-geometry', '+0+0')
    ofs_x = win.x
    ofs_y = win.y
    win.resize_and_move(10, 20, 30, 40)
    win2 = Window.by_name(xclock.NAME)[0]
    assert win.id == win2.id
    assert win2.x == 10 + ofs_x
    assert win2.y == 20 + ofs_y
    assert win2.w == 30
    assert win2.h == 40

def check_geometry(geom):
    win, xclock = get_win('xclock', '-geometry', geom)
    win.resize_and_move(0, 0, 100, 200)
    win.set_geometry(geom)
    win2 = Window.by_name(xclock.NAME)[0]
    assert win2.x == win.x
    assert win2.y == win.y
    assert win2.w == win.w
    assert win2.h == win.h

def test_geometry():
    check_geometry('100x200+30+40')

def test_geometry_negative():
    py.test.skip('fixme')
    check_geometry('100x200-30-40')

def get_geometry (w):
    return (w.x, w.y, w.w, w.h)

def xor (a,b):
    return (a and not b) or (not a and b)

def state_xor (prop, w1, w2):
    return xor(prop in w1.wm_state, prop in w2.wm_state)

def test_properties():
    orig, xclock = get_win('xclock')
    orig.set_properties(("toggle","maximized_vert","maximized_horz"))
    curr = Window.by_name(xclock.NAME)[0]
    assert not (get_geometry(orig) == get_geometry(curr))
    assert state_xor("maximized_vert", curr, orig)
    assert state_xor("maximized_horz", curr, orig)
    time.sleep(0.5)
    orig.set_properties(("toggle","maximized_vert","maximized_horz"))
    curr = Window.by_name(xclock.NAME)[0]
    assert get_geometry(orig) == get_geometry(curr)
    assert not state_xor("maximized_vert", curr, orig)
    assert not state_xor("maximized_horz", curr, orig)
    time.sleep(0.5)
    orig.set_properties(("toggle","fullscreen"))
    curr = Window.by_name(xclock.NAME)[0]
    assert not (get_geometry(orig) == get_geometry(curr))
    assert state_xor("fullscreen", curr, orig)
    time.sleep(0.5)
    orig.set_properties(("toggle","fullscreen"))
    curr = Window.by_name(xclock.NAME)[0]
    assert get_geometry(orig) == get_geometry(curr)
    assert not state_xor("fullscreen", curr, orig)
    # restore the original maximized properties: fullscreen removes them
    if "maximized_horz" in orig.wm_state:
        orig.set_properties(("add","maximized_horz"))
    if "maximized_vert" in orig.wm_state:
        orig.set_properties(("add","maximized_vert"))
