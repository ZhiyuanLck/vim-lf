from .utils import vimeval
from .option import lfopt


class Line(object):
    def __init__(self, cwd, path, winwidth):
        self._cwd = cwd
        self.path = path
        self._winwidth = winwidth
        self._parse_type()
        self._set_text()
        self._set_textline()

    def _parse_type(self):
        self.is_hidden = self.path.name.startswith('.')

    def _dplen(self, text):
        return vimeval('strdisplaywidth("{}")'.format(text), 1)

    def _bytelen(self, text):
        return vimeval('len("{}")'.format(text), 1)

    def _set_text(self):
        start = len(str(self._cwd))
        if str(self._cwd)[-1] != '/':
            start += 1
        slash = '/' if self.path.is_dir() else ''
        text = str(self.path)[start:] + slash
        rest = self._winwidth - self._dplen(text) % self._winwidth
        blank = ' ' * rest
        self.text = text + blank
        self.bytelen = self._bytelen(self.text)

    def _set_textline(self):
        opt = {"text": self.text}
        prop = {"col": 1, "length": self.bytelen}
        if self.show_hidden:
            if self.path.is_dir():
                prop_type = "hidden_dir" if self.is_hidden else "dir"
            elif self.path.is_file():
                prop_type = "hidden_file" if self.is_hidden else "file"
            else:
                prop_type = "file"
        else:
            prop_type = "dir" if self.path.is_dir() else "file"
        prop["type"] = prop_type
        opt["props"] = [prop]
        self.opt = opt


class Text(object):
    def __init__(self, panel):
        self.path_list = panel.path_list
        self.cwd = panel.cwd
        self.winwidth = panel.winwidth
        self.show_hidden = panel.show_hidden
        self.text = [self._get_text(p)[1] for p in self.path_list]
        self.opt = [self._get_opt(p) for p in self.path_list]

    def _dplen(self, text):
        return vimeval('strdisplaywidth("{}")'.format(text), 1)

    def _bytelen(self, text):
        return vimeval('len("{}")'.format(text), 1)

    def _is_hidden(self, path):
        return path.name.startswith('.')

    def _get_text(self, path):
        start = len(str(self.cwd))
        if str(self.cwd)[-1] != '/':
            start += 1
        slash = '/' if path.is_dir() else ''
        text = str(path)[start:] + slash
        rest = self.winwidth - self._dplen(text) % self.winwidth
        blank = ' ' * rest
        return self._bytelen(text), text + blank

    def _get_opt(self, path):
        hidden = self._is_hidden(path)
        length, text = self._get_text(path)
        opt = {"text": text}
        prop = {"col": 1, "length": length}
        if self.show_hidden:
            if path.is_dir():
                prop_type = "hidden_dir" if hidden else "dir"
            elif path.is_file():
                prop_type = "hidden_file" if hidden else "file"
            else:
                prop_type = "file"
        else:
            prop_type = "dir" if path.is_dir() else "file"
        prop["type"] = prop_type
        opt["props"] = [prop]
        return opt
