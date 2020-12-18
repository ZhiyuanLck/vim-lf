from .utils import vimeval, vimcmd, setlocal, winexec, vimget
from .text import Text
from .option import lfopt
from copy import copy


class Panel(object):
    def close(self):
        vimcmd("call popup_close({})".format(self.winid))


class DirPanel(Panel):
    def __init__(self, cwd, opt, number):
        self.cwd = cwd.resolve()
        self.opt = opt
        self.number = number
        self.index = 0
        self.cursorline_id = None
        self.text = None
        self.path_list = None
        self.show_hidden = lfopt.show_hidden
        self._create_popup()
        self.winwidth = vimeval("winwidth({})".format(self.winid), 1)
        winheight = vimeval("winheight({})".format(self.winid), 1)
        self.scroll_line = winheight // 2

    def _create_popup(self):
        self.winid = vimeval("popup_create([], {})".format(self.opt))
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        vimcmd("call lf#colorscheme#prop({})".format(self.bufnr))

    def _glob(self):
        self.path_list = sorted(self.cwd.glob('*'))
        self._set_text()

    def _set_text(self):
        self._filter()
        text = Text(self)
        self.text = text.text
        self.text_prop = text.opt
        vimcmd("call popup_settext({}, {})".format(self.winid, self.text_prop))

    def _cursorline(self):
        """
        highlight curcorline
        """
        if self.cursorline_id is not None:
            vimcmd("call clearmatches({})".format(self.winid))
            self.cursorline_id = None
        if self._empty():
            return
        self.cursorline_id = vimeval(
                "matchaddpos('vlf_hl_cursorline_%d', [%s], 100, -1, #{window: %s})"
                % (self.number, self.index + 1, self.winid))
        vimcmd('call win_execute({}, "norm! {}zz", 1)'.format(self.winid, self.index + 1))

    def _correct_index(self):
        """
        correct index when text list changed such as refesh, delete, paste
        """
        if self.index < 0:
            self.index = 0
        elif self.index >= self._len():
            self.index = self._len() - 1

    def _empty(self):
        return self.path_list == []

    def _index(self, item):
        try:
            self.index = self.path_list.index(item)
        except ValueError:
            self.index = 0

    def _filter(self):
        if not self.show_hidden:
            self.path_list = [p for p in self.path_list if not p.name.startswith('.')]

    def curpath(self):
        return None if self._empty() else self.path_list[self.index]

    def refresh(self):
        self._glob()
        self._correct_index()
        self._cursorline()

    def backward(self):
        if self.cwd == self.cwd.parent:
            return False
        item = copy(self.cwd)
        self.cwd = self.cwd.parent
        self._glob()
        self._index(item)
        self._cursorline()
        return True

    def forward(self):
        if self._empty():
            return
        curpath = self.curpath()
        if curpath.is_dir():
            self.cwd = curpath

    def _move(self, down=True):
        max = len(self.text)
        if not max:
            return
        offset = 1 if down else -1
        self.index = (self.index + offset) % max
        self._cursorline()
        return self.curpath()

    def down(self):
        return self._move()

    def up(self):
        return self._move(False)

    def _len(self):
        return len(self.path_list)

    def jump(self, top=True):
        if not self._empty():
            self.index = 0 if top else self._len() - 1
            self._cursorline()

    def scroll(self, down=True):
        if not self._empty():
            sign = 1 if down else -1
            self.index += sign * self.scroll_line
            self._correct_index()
            self._cursorline()

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        # get current path before path list changed
        item = self.curpath()
        self._glob()
        self._index(item)
        self._cursorline()


class FilePanel(Panel):
    def __init__(self, path, opt):
        path = path.resolve()
        self.buf_exist = vimeval("bufexists('{}') == v:true".format(path)) == '1'
        if self.buf_exist:
            vimcmd("noautocmd silent let winid = bufnr('{}')->popup_create({})".format(path, opt))
            self.winid = vimeval("winid")
        else:
            vimcmd("noautocmd silent let winid = '{}'->bufadd()->popup_create({})".format(path, opt))
            self.winid = vimeval("winid")
            winid = self.winid
            setlocal(winid, "wrap")
            setlocal(winid, "nobuflisted")
            setlocal(winid, "buftype=nowrite")
            setlocal(winid, "bufhidden=hide")
            setlocal(winid, "number")
            setlocal(winid, "undolevels=-1")
            setlocal(winid, "noswapfile")
            setlocal(winid, "nolist")
            setlocal(winid, "norelativenumber")
            setlocal(winid, "nospell")
            setlocal(winid, "nofoldenable")
            setlocal(winid, "foldmethod=manual")
            setlocal(winid, "signcolumn=no")
        if path.stat().st_size < lfopt.max_file_size:
            winexec(self.winid, "filetype detect")
        self.bufnr = vimeval("winbufnr({})".format(self.winid))

    def close(self):
        vimcmd("call popup_close({})".format(self.winid))
        if not self.buf_exist:
            vimcmd("bwipeout {}".format(self.bufnr))
