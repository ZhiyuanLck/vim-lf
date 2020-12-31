from operator import attrgetter
from .utils import vimeval, dplen, bytelen
from .option import lfopt


class BaseLine(object):
    def __init__(self, path):
        self.path = path
        self.text = ''

    @property
    def is_hidden(self):
        return self.path.name.startswith('.')

    @property
    def is_dir(self):
        return self.path.is_dir()

    def _get_proptype(self):
        if self.is_dir:
            prop_type = "hidden_dir" if self.is_hidden else "dir"
        else:
            prop_type = "hidden_file" if self.is_hidden else "file"
        return prop_type


class SimpleLine(BaseLine):
    def __init__(self, path):
        super().__init__(path)
        self._set_text()
        self._set_sort()
        self._set_textline()

    def _set_text(self):
        self.text = str(self.path.resolve())

    def _set_sort(self):
        self.sort_dir_first = 0 if self.is_dir else 1
        self.lower_text = self.text.lower()

    def _set_textline(self):
        opt = {"text": self.text}
        prop = {"col": 1, "length": bytelen(self.text)}
        prop["type"] = self._get_proptype()
        opt["props"] = [prop]
        self.opt = opt


class Line(BaseLine):
    def __init__(self, path, panel):
        self.path = path
        self._cwd = panel.cwd
        self._winwidth = panel.winwidth
        self._show_hidden = panel.show_hidden
        self._set_text()
        self._set_textline()
        self._set_sort()

    def _set_sort(self):
        self.sort_dir_first = 0 if self.is_dir else 1
        self.lower_text = self.raw_text.lower()

    def _set_text(self):
        start = len(str(self._cwd))
        if str(self._cwd)[-1] != '/':
            start += 1
        slash = '/' if self.path.is_dir() else ''
        text = str(self.path)[start:] + slash
        self.raw_text = text
        rest = self._winwidth - dplen(text) % self._winwidth
        blank = ' ' * rest
        self.text = text + blank
        self.bytelen = bytelen(self.text)

    def _set_textline(self):
        opt = {"text": self.text}
        prop = {"col": 1, "length": self.bytelen}
        prop["type"] = self._get_proptype()
        opt["props"] = [prop]
        self.opt = opt


class Text(object):
    def __init__(self, panel):
        self.panel = panel
        self._text = []
        for p in panel.path_list:
            line = Line(p, panel)
            if self._ignore(line):
                continue
            self._text.append(line)
        key = []
        if lfopt.sort_dir_first:
            key.append('sort_dir_first')
        if lfopt.sort_ignorecase:
            key.append('lower_text')
        if key == []:
            self._text = sorted(self._text)
        else:
            self._text = sorted(self._text, key=attrgetter(*key))

    @property
    def text(self):
        return self._text

    @property
    def props(self):
        return [line.opt for line in self._text]

    def _ignore(self, line: Line):
        if not self.panel.show_hidden:
            return line.is_hidden
        return False
