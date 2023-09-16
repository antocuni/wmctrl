import pytest
import subprocess
import time
from wmctrl import Window, Desktop

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
    win, xclock = get_win('xclock', '-geometry', '+100+200')
    ofs_x = win.x
    ofs_y = win.y
    win.resize_and_move(10, 20, 130, 140)
    win2 = Window.by_name(xclock.NAME)[0]
    assert win.id == win2.id
    # FIXME: these don't really work, see the XXX inside resize_and_move
    ## assert win2.x == 10 + ofs_x
    ## assert win2.y == 20 + ofs_y
    assert win2.w == 130
    assert win2.h == 140

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
    pytest.skip('fixme')
    check_geometry('100x200-30-40')

def test_properties():
    def get_geometry (w):
        return (w.x, w.y, w.w, w.h)
    #
    w1, xclock = get_win('xclock')
    assert 'maximized_vert' not in w1.wm_state
    assert 'maximized_horz' not in w1.wm_state
    w1.set_properties(("toggle", "maximized_vert", "maximized_horz"))
    #
    # get a new instance of w1, to re-read the wm_state
    w2 = Window.by_id(int(w1.id, 16))[0]
    assert not (get_geometry(w1) == get_geometry(w2))
    assert 'maximized_vert' in w2.wm_state
    assert 'maximized_horz' in w2.wm_state

def test_Desktop_list():
    dlist = Desktop.list()
    assert len(dlist) >= 1
    num_active = len([d for d in dlist if d.active])
    assert num_active == 1

def test_Desktop_active():
    desktop = Desktop.get_active()
    win = Window.get_active()
    assert win.desktop == desktop.num
