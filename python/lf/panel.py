from copy import copy
from .utils import vimeval, vimcmd
from .utils import setlocal, winexec, dplen, bytelen
from .text import Text
from .option import lfopt


class Panel(object):
    def close(self):
        vimcmd("call popup_close({})".format(self.winid))

    def _set_wincolor(self):
        setlocal(self.winid, "wincolor={}".format(lfopt.wincolor))


class DirPanel(Panel):
    def __init__(self, cwd, number):
        self.cwd = cwd.resolve()
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
        if self.number == 0:
            opt = lfopt.popup("left")
        elif self.number == 1:
            opt = lfopt.popup("middle")
        else:
            opt = lfopt.popup("right")
        self.winid = vimeval("popup_create([], {})".format(opt))
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        vimcmd("call lf#colorscheme#path_prop({})".format(self.bufnr))
        self._set_wincolor()

    def _glob(self):
        self.path_list = sorted(self.cwd.glob('*'))
        self._set_text()

    def _set_text(self):
        T = Text(self)
        self.text = T.text
        vimcmd("call popup_settext({}, {})".format(self.winid, T.props))

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
        return self.text == []

    def _index(self, item):
        find = False
        for i, line in enumerate(self.text):
            if line.path == item:
                self.index = i
                find = True
                break
        if not find:
            self.index = 0

    def curpath(self):
        return None if self._empty() else self.text[self.index].path

    def refresh(self, keep_pos=True):
        if keep_pos:
            item = self.curpath()
            self._glob()
            self._index(item)
            self._cursorline()
        else:
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

    def move(self, down=True):
        max = len(self.text)
        if not max:
            return
        offset = 1 if down else -1
        self.index = (self.index + offset) % max
        self._cursorline()
        return self.curpath()

    def _len(self):
        return len(self.text)

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
        self.refresh()

    def touch(self, name: str):
        file = self.cwd / name
        file.touch()
        self.refresh()


class FilePanel(Panel):
    def __init__(self, path):
        self.path = path.resolve()
        self._create()
        self._linenr()
        self._set_option()

    def _create(self):
        opt = lfopt.popup("right")
        self.buf_exist = vimeval("bufexists('{}') == v:true".format(self.path)) == '1'
        if self.buf_exist:
            vimcmd("noautocmd silent let winid = bufnr('{}')->popup_create({})".format(self.path, opt))
            self.winid = vimeval("winid")
        else:
            vimcmd("noautocmd silent let winid = '{}'->bufadd()->popup_create({})".format(self.path, opt))
            self.winid = vimeval("winid")

    def _linenr(self):
        winexec(self.winid, "let _lines = line('$')")
        self.lines = vimeval("_lines", 1)

    def _set_option(self):
        winid = self.winid
        #  setlocal(winid, "wrap")
        #  setlocal(winid, "nobuflisted")
        #  setlocal(winid, "buftype=nowrite")
        #  setlocal(winid, "bufhidden=hide")
        #  setlocal(winid, "number")
        #  setlocal(winid, "undolevels=-1")
        #  setlocal(winid, "noswapfile")
        #  setlocal(winid, "nolist")
        #  setlocal(winid, "norelativenumber")
        #  setlocal(winid, "nospell")
        #  setlocal(winid, "nofoldenable")
        #  setlocal(winid, "foldmethod=manual")
        #  setlocal(winid, "signcolumn=no")
        if self.path.stat().st_size < lfopt.max_file_size:
            winexec(self.winid, "filetype detect")
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        self._set_wincolor()

    def close(self):
        vimcmd("call popup_close({})".format(self.winid))
        if not self.buf_exist:
            vimcmd("bwipeout {}".format(self.bufnr))


class BottomPanel(Panel):
    def __init__(self, name, has_prop=True):
        self.winid = vimeval("popup_create([], {})".format(lfopt.popup(name)))
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        self.winwidth = vimeval("winwidth({})".format(self.winid), 1)
        self._set_wincolor()
        if has_prop:
            vimcmd("call lf#colorscheme#{}_prop({})".format(name, self.bufnr))

    def _settext(self, text):
        vimcmd("call popup_settext({}, {})".format(self.winid, text))

    def clear(self):
        self._settext('')


class InfoPanel(BottomPanel):
    def __init__(self, manager):
        super().__init__("info")
        self.manager = manager

    def _set_panel(self):
        self.left = self.manager.left_panel
        self.middle = self.manager.middle_panel
        self.right = self.manager.right_panel
        self.index = self.middle.index
        self.text_list = self.middle.text
        self.path = self.text_list[self.index].path.resolve()
        self.total = len(self.text_list)

    def info_path(self):
        self._set_panel()
        if self.text_list == []:
            self.clear()
            return
        self._set_sz()
        self._set_nr()
        self._set_path()
        self.info = self.path_str_fill + self.sz + self.nr
        self._settext_path()
        #  self._settext([info])

    def _settext_path(self):
        opt = {"text": self.info}
        prop_path = {
                "col": 1,
                "length": bytelen(self.path_str),
                "type": "path",
                }
        prop_size = {
                "col": self.winwidth - len(self.sz) - len(self.nr) + 1,
                "length": len(self.sz),
                "type": "size",
                }
        prop_nr = {
                "col": self.winwidth - len(self.nr) + 1,
                "length": len(self.nr),
                "type": "nr",
                }
        opt["props"] = [prop_path, prop_size, prop_nr]
        self._settext([opt])

    def _set_sz(self):
        self.sz = ''
        if self.path.is_file():
            sz = self.path.stat().st_size
            if sz < 2 ** 10:
                unit = 'B'
            elif sz < 2 ** 20:
                unit = 'KB'
                sz >>= 10
            elif sz < 2 ** 30:
                unit = 'MB'
                sz >>= 20
            else:
                unit = 'GB'
                sz >>= 30
            self.sz = " {} {} ".format(sz, unit)

    def _set_nr(self):
        if isinstance(self.right, DirPanel):
            lines = len(self.right.text)
        elif isinstance(self.right, FilePanel):
            lines = self.right.lines
        self.nr = " {}/{}:{} ".format(self.index + 1, self.total, lines)

    def _set_path(self):
        valid_len = self.winwidth - len(self.nr) - len(self.sz)
        path_str = " {} ".format(str(self.path))
        if dplen(path_str) > valid_len:
            path_str = path_str[:valid_len - 4] + '... '
        blank = valid_len - dplen(path_str)
        self.path_str = path_str
        self.path_str_fill = path_str + blank * ' '


def update(fun):
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        self = args[0]
        self._settext_input()
    return wrapper


class CliPanel(BottomPanel):
    def __init__(self, prompt):
        super().__init__("cli")
        self.prompt = prompt
        self.cmd = ''
        self.pos = 0  # number of chars before cursor
        self._settext_input()

    def _settext_input(self):
        text = self.prompt + self.cmd + ' '
        prompt_len = bytelen(self.prompt)
        cmd_len = bytelen(self.cmd[:self.pos])
        opt = {"text": text}
        prop_prompt = {
                "col": 1,
                "length": prompt_len,
                "type": "prompt",
                }
        prop_cursor = {
                "col": prompt_len + cmd_len + 1,
                "length": self._curlen(),
                "type": "cursor",
                }
        opt["props"] = [prop_prompt, prop_cursor]
        self._settext([opt])

    def input(self):
        while 1:
            action = vimeval("lf#cli()")
            if action in ['done', 'quit']:
                break

    def _empty(self):
        return self.cmd == ''

    def _at_end(self):
        return self.pos == len(self.cmd)

    def _head(self):
        return self.cmd[:self.pos]

    def _tail(self):
        if self._at_end():
            return ''
        return self.cmd[self.pos:]

    def _curlen(self):
        if self._at_end():
            return 1
        return bytelen(self.cmd[self.pos])

    @update
    def clear(self):
        self.cmd = ''
        self.pos = 0

    @update
    def add(self):
        char = vimeval("ch")
        self.cmd = self._head() + char + self._tail()
        self.pos += 1

    @update
    def delete(self):
        if self._empty():
            return
        self.cmd = self.cmd[:self.pos - 1] + self._tail()
        self.pos -= 1

    @update
    def left(self):
        if self._empty():
            return
        self.pos -= 1

    @update
    def right(self):
        if self._at_end():
            return
        self.pos += 1

    @update
    def go_start(self):
        self.pos = 0

    @update
    def go_end(self):
        self.pos = len(self.cmd)

    def done(self):
        self.close()
        self.do = True

    def quit(self):
        self.close()
        self.do = False


class BorderPanel(Panel):
    def __init__(self):
        self.winid = vimeval("popup_create([], {})".format(lfopt.popup("border")))
        self._set_wincolor()
