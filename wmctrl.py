from collections import namedtuple

VERSBOSE = True
BaseWindow = namedtuple('Window', 'id desktop pid x y w h wm_class host wm_name wm_window_role wm_state')

def getoutput(s):
    import commands
    if VERSBOSE:
        print s
    return commands.getoutput(s)

def system(s):
    import os
    if VERSBOSE:
        print s
    return os.system(s)

def uniq(it):
    return list(set(it))

class Window(BaseWindow):

    @classmethod
    def list(cls):
        out = getoutput('wmctrl -l -G -p -x')
        windows = []
        for line in out.splitlines():
            parts = line.split(None, len(Window._fields)-3)
            parts = map(str.strip, parts)
            parts[1:7] = map(int, parts[1:7])
            parts.append(_wm_window_role(parts[0]))
            parts.append(_wm_state(parts[0]))
            ## parts.append('')
            ## parts.append('')
            if len(parts) != 12:
                continue
            windows.append(cls(*parts))
        return windows

    @classmethod
    def list_classes(cls):
        return uniq([w.wm_class for w in cls.list()])

    @classmethod
    def list_names(cls):
        return uniq([w.name_class for w in cls.list()])

    @classmethod
    def list_roles(cls):
        return uniq([w.wm_window_role for w in cls.list()])

    @classmethod
    def by_name(cls, name):
        return [win for win in cls.list() if win.wm_name == name]

    @classmethod
    def by_name_endswith(cls, name):
        return [win for win in cls.list() if win.wm_name.endswith(name)]

    @classmethod
    def by_name_startswith(cls, name):
        return [win for win in cls.list() if win.wm_name.startswith(name)]

    @classmethod
    def by_role(cls, role):
        return [win for win in cls.list() if win.wm_window_role == role]

    @classmethod
    def by_class(cls, wm_class):
        return [win for win in cls.list() if win.wm_class == wm_class]

    @classmethod
    def by_id(cls, id):
        return [win for win in cls.list() if int(win.id, 16) == id]

    @classmethod
    def get_active(cls):
        out = getoutput("xprop -root _NET_ACTIVE_WINDOW")
        parts = out.split()
        try:
            id = int(parts[-1], 16)
        except ValueError:
            return None
        lst = cls.by_id(id)
        if not lst:
            return None
        assert len(lst) == 1
        return lst[0]

    def activate(self):
        system('wmctrl -id -a %s' % self.id)

    def resize_and_move(self, x=None, y=None, w=None, h=None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if w is None:
            w = self.w
        if h is None:
            h = self.h
        mvarg = '0,%d,%d,%d,%d' % (x, y, w, h)
        system('wmctrl -i -r %s -e %s' % (self.id, mvarg))

    def resize(self, w=None, h=None):
        self.resize_and_move(w=w, h=h)

    def move(self, x=None, y=None):
        self.resize_and_move(x=x, y=y)

    def set_geometry(self, geometry):
        dim, pos = geometry.split('+', 1)
        w, h = map(int, dim.split('x'))
        x, y = map(int, pos.split('+'))
        self.resize_and_move(x, y, w, h)

    def set_properties(self,properties):
        proparg = ",".join(properties)
        system('wmctrl -i -r %s -b %s' % (self.id,proparg))

    def set_decorations(self, v):
        import gtk.gdk
        w = gtk.gdk.window_foreign_new(int(self.id, 16))
        w.set_decorations(v)
        gtk.gdk.window_process_all_updates()
        gtk.gdk.flush()

def _wm_window_role(winid):
    out = getoutput('xprop -id %s WM_WINDOW_ROLE' % winid)
    try:
        _, value = out.split(' = ')
    except ValueError:
        # probably xprop returned an error
        return ''
    else:
        return value.strip('"')

def strip_prefix (prefix, word):
    if word.startswith(prefix):
        return word[len(prefix):]
    return word

def _wm_state (winid):
    out = getoutput('xprop -id %s _NET_WM_STATE' % winid)
    try:
        _, value = out.split(' = ')
    except ValueError:
        # probably xprop returned an error
        return []
    else:
        return [strip_prefix("_NET_WM_STATE_",s).lower()
                for s in value.split(', ')]


if __name__ == '__main__':
    for w in Window.list():
        print '{w.id:10s} {w.x:4d} {w.y:4d} {w.w:4d} {w.h:4d} {w.wm_name} - {w.wm_class} - {w.wm_window_role}'.format(w=w)

    
