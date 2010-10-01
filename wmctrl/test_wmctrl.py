import py
import subprocess
import time
from wmctrl import Window

NAME='xclock-for-pytest'

class get_xclock(object):
    def __init__(self, *args):
        self.child = subprocess.Popen(['xclock', '-name', NAME]+list(args))
        time.sleep(0.1)

    def __del__(self):
        self.child.kill()

def get_win(*args):
    xclock = get_xclock(*args)
    win = Window.by_name(NAME)
    return win[0], xclock

def test_list():
    xclock = get_xclock()
    wins = Window.list()
    names = [win.wm_name for win in wins]
    assert NAME in names

def test_attributes():
    win, xclock = get_win('-geometry', '100x200+0+0')
    assert win.wm_name == NAME
    assert win.wm_class == NAME + '.XClock'
    assert win.w == 100
    assert win.h == 200
    # measure the width and the height of WM decorations
    ofs_x = win.x
    ofs_y = win.y
    xclock.child.kill()
    win, xclock = get_win('-geometry', '+30+40')
    assert win.x == 30 + ofs_x
    assert win.y == 40 + ofs_y

def test_activate():
    win = Window.list()
    orig = Window.get_active()
    win[0].activate()
    active = Window.get_active()
    assert active.id == win[0].id
    orig.activate()

def test_resize_and_move():
    win, xclock = get_win('-geometry', '+0+0')
    ofs_x = win.x
    ofs_y = win.y
    win.resize_and_move(10, 20, 30, 40)
    win2 = Window.by_name(NAME)[0]
    assert win.id == win2.id
    assert win2.x == 10 + ofs_x
    assert win2.y == 20 + ofs_y
    assert win2.w == 30
    assert win2.h == 40

def check_geometry(geom):
    win, xclock = get_win('-geometry', geom)
    win.resize_and_move(0, 0, 100, 200)
    win.set_geometry(geom)
    win2 = Window.by_name(NAME)[0]
    assert win2.x == win.x
    assert win2.y == win.y
    assert win2.w == win.w
    assert win2.h == win.h

def test_geometry():
    check_geometry('10x20+30+40')

def test_geometry_negative():
    py.test.skip('fixme')
    check_geometry('10x20-30-40')

