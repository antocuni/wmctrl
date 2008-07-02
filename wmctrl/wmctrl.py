import os
from commands import getoutput
from namedtuple import namedtuple

Window = namedtuple('Window', 'id desktop pid x y w h wm_class host wm_name wm_window_role')

def resize_and_move(win, x, y, w, h):
    mvarg = '0,%d,%d,%d,%d' % (x, y, w, h)
    os.system('wmctrl -i -r %s -e %s' % (win.id, mvarg))

def set_geometry(win, geometry):
    dim, pos = geometry.split('+', 1)
    w, h = map(int, dim.split('x'))
    x, y = map(int, pos.split('+'))
    resize_and_move(win, x, y, w, h)

def wm_window_role(winid):
    out = getoutput('xprop -id %s WM_WINDOW_ROLE' % winid)
    try:
        _, value = out.split(' = ')
    except ValueError:
        # probably xprop returned an error
        return ''
    else:
        return value.strip('"')

def winlist():
    out = getoutput('wmctrl -l -G -p -x')
    windows = []
    for line in out.splitlines():
        parts = line.split(None, len(Window._fields)-2)
        parts = map(str.strip, parts)
        parts[1:7] = map(int, parts[1:7])
        parts.append(wm_window_role(parts[0]))
        windows.append(Window(*parts))
    return windows

def win_by_name(name):
    return [win for win in winlist() if win.wm_name == name]

def win_by_name_endswith(name):
    return [win for win in winlist() if win.wm_name.endswith(name)]

def win_by_role(role):
    return [win for win in winlist() if win.wm_window_role == role]

def win_by_class(cls):
    return [win for win in winlist() if win.wm_class == cls]
