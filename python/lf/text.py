from .utils import vimeval
from .option import lfopt


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
