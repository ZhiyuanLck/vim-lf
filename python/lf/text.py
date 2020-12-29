from operator import attrgetter
from .utils import vimeval, dplen, bytelen
from .option import lfopt


class BaseLine(object):
    def __init__(self, path):
        self.path = path
        self.text = ''
        self._parse_type()

    def _parse_type(self):
        self.is_hidden = self.path.name.startswith('.')
        self.is_dir = self.path.is_dir()

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
    def __init__(self, cwd, path, winwidth, show_hidden):
        self._cwd = cwd
        self.path = path
        self._winwidth = winwidth
        self._show_hidden = show_hidden
        self._parse_type()
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
        self.text = []
        for p in panel.path_list:
            line = Line(panel.cwd, p, panel.winwidth, panel.show_hidden)
            if self._ignore(line):
                continue
            self.text.append(line)
        key = []
        if lfopt.sort_dir_first:
            key.append('sort_dir_first')
        if lfopt.sort_ignorecase:
            key.append('lower_text')
        if key == []:
            self.text = sorted(self.text)
        else:
            self.text = sorted(self.text, key=attrgetter(*key))
        self.props = [line.opt for line in self.text]

    def _ignore(self, line: Line):
        if not self.panel.show_hidden:
            return line.is_hidden
        return False
