import logging
from copy import copy
from operator import attrgetter
from .utils import *
from .text import Text, SimpleLine
from .option import lfopt, Option
from .search import RegexSearch


logger = logging.getLogger()


class Panel(object):
    def __init__(self, name, has_prop=True):
        self.lfopt = Option()
        self.winid = vimeval("popup_create([], {})".format(self.lfopt.popup(name)))
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        self.winwidth = vimeval("winwidth({})".format(self.winid), 1)
        self._set_wincolor()
        if has_prop:
            self._set_textprop(name)

    def _set_textprop(self, name):
        vimcmd("call lf#colorscheme#{}_prop({})".format(name, self.bufnr))

    def close(self):
        vimcmd("call popup_close({})".format(self.winid))

    def _set_wincolor(self):
        setlocal(self.winid, "wincolor={}".format(self.lfopt.wincolor))

    def resize(self, name):
        logger.info("resize panel {}".format(name))
        self.lfopt = Option()
        vimcmd("call popup_setoptions({}, {})".format(self.winid, self.lfopt.popup(name)))
        self.winwidth = vimeval("winwidth({})".format(self.winid), 1)


class Select(object):
    def __init__(self, panel):
        self.panel = panel
        self.path_list = panel.get_path_list()
        self.max_len = len(self.path_list)
        self.start = panel.index
        self.end = panel.index
        self.scroll_line = panel.scroll_line
        self.id_list = []
        self.is_add = True
        self._update()
        logger.info("record pos: [{}, {}]".format(self.start, self.end))

    def _winid(self):
        return self.panel.winid

    def _range(self):
        return range(min(self.start, self.end), max(self.start, self.end) + 1)

    def selection(self):
        a, b = min(self.start, self.end), max(self.start, self.end) + 1
        return self.path_list[a:b]

    def _update(self):
        self.panel.index = self.end
        self.panel.refresh(keep_pos=False)
        self._match_clear()
        for index in self._range():
            vimcmd(
                "call matchaddpos('vlf_hl_cursorline_v', [%s], 100, -1, #{window: %s})"
                % (index + 1, self._winid()))
        vimcmd(
            "call matchaddpos('vlf_hl_cursorline_1', [%s], 200, -1, #{window: %s})"
            % (self.end + 1, self._winid()))
        vimcmd('call win_execute({}, "norm! {}zz", 1)'.format(self._winid(), self.end + 1))

    def _match_clear(self):
        vimcmd("call clearmatches({})".format(self._winid()))

    def quit(self, interrupt=False):
        self._match_clear()
        self.panel.mode = "normal"
        #  if not interrupt:
            #  self.panel.index = self.start if self.start < self.end else self.end
            #  self.panel.refresh(keep_pos=False)

    def select_all(self):
        self.start = 0
        self.end = self.max_len - 1
        self._update()

    def change_active(self):
        self.start, self.end = self.end, self.start
        self._update()
        logger.info("record pos: [{}, {}]".format(self.start, self.end))

    def _move(self, index):
        self.end = index
        if self.end >= self.max_len:
            self.end = self.max_len - 1
        elif self.end < 0:
            self.end = 0
        self._update()
        logger.info("record pos: [{}, {}]".format(self.start, self.end))

    def down(self):
        self._move(self.end + 1)

    def up(self):
        self._move(self.end - 1)

    def scroll_down(self):
        self._move(self.end + self.scroll_line)

    def scroll_up(self):
        self._move(self.end - self.scroll_line)

    def top(self):
        self._move(0)

    def bottom(self):
        self._move(self.max_len - 1)


class DirPanel(Panel):
    def __init__(self, cwd, number):
        self.cwd = cwd.resolve() if cwd is not None else None
        self.number = number
        self._set_attr()
        self.index = 0
        self.cursorline_id = None
        self.text = []
        self.path_list = []
        self.lfopt = Option()
        self.show_hidden = self.lfopt.show_hidden
        self._create_popup()
        self.mode = "normal"
        self.winwidth = vimeval("winwidth({})".format(self.winid), 1)
        winheight = vimeval("winheight({})".format(self.winid), 1)
        self.scroll_line = winheight // 2

    def _set_attr(self):
        name_list = ["left", "middle", "right"]
        self.name = name_list[self.number]
        self.is_middle = self.number == 1

    def _create_popup(self):
        if self.number == 0:
            opt = self.lfopt.popup("left")
        elif self.number == 1:
            opt = self.lfopt.popup("middle")
        else:
            opt = self.lfopt.popup("right")
        self.winid = vimeval("popup_create([], {})".format(opt))
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        vimcmd("call lf#colorscheme#path_prop({})".format(self.bufnr))
        self._set_wincolor()
        logger.info("create {} pannel with winid: {}".format(self.name, self.winid))

    def _is_normal(self):
        return self.mode == "normal"

    def _is_select(self):
        return self.mode == "select"

    def get_path_list(self):
        return [line.path for line in self.text]

    def _glob(self):
        self.path_list = self.cwd.glob('*')
        self._set_text()

    def _set_text(self):
        T = Text(self)
        self.text = T.text
        props = [' ' * self.winwidth] if self.empty() else T.props
        vimcmd("call popup_settext({}, {})".format(self.winid, vimstr(props)))

    def _cursorline(self):
        """
        highlight curcorline
        """
        if self.cursorline_id is not None:
            vimcmd("call clearmatches({})".format(self.winid))
            self.cursorline_id = None
        if self.empty() and self.is_middle:
            self.cursorline_id = vimeval(
                    "matchaddpos('vlf_hl_cursorline_%d', [%s], 100, -1, #{window: %s})"
                    % (self.number, 1, self.winid))
            return
        self.cursorline_id = vimeval(
                "matchaddpos('vlf_hl_cursorline_%d', [%s], 100, -1, #{window: %s})"
                % (self.number, self.index + 1, self.winid))
        vimcmd('call win_execute({}, "norm! {}zz", 1)'.format(self.winid, self.index + 1))

    def select(self):
        if self.empty():
            return
        self.v_block = Select(self)
        self.mode = 'select'

    def _correct_index(self):
        """
        correct index when text list changed such as refesh, delete, paste
        """
        if self.index <= 0:
            self.index = 0
        elif self.index >= self._len():
            self.index = self._len() - 1

    def empty(self):
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
        return None if self.empty() else self.text[self.index].path

    def refresh(self, keep_pos=True, item=None, index=None):
        if index is not None:
            self._glob()
            self.index = index
            self._correct_index()
        elif item is not None:
            self._glob()
            self._index(item)
        elif keep_pos:
            item = self.curpath()
            self._glob()
            self._index(item)
        else:
            self._glob()
            self._correct_index()
        self._cursorline()
        if self.is_middle:
            logger.info("cursor pos after refresh: {}".format(self.index))

    def search_refresh(self, Text):
        self.text = Text.text
        self.index = 0
        props = [' ' * self.winwidth] if self.empty() else Text.props
        vimcmd("call popup_settext({}, {})".format(self.winid, props))
        self._cursorline()

    def backward(self):
        if self.cwd == self.cwd.parent:
            logger.warning("current cwd is root directory, action cancels")
            return False
        item = copy(self.cwd)
        self.cwd = self.cwd.parent
        self._glob()
        self._index(item)
        self._cursorline()
        logger.info("cursor pos after backward: {}".format(self.index))
        return True

    def forward(self):
        if self.empty():
            logger.warning("ignore empty directory {}".format(self.cwd))
            return
        curpath = self.curpath()
        if curpath.is_dir():
            self.cwd = curpath
        logger.info("cursor pos after forward: {}".format(self.index))

    def move(self, down=True):
        max = len(self.text)
        if not max:
            return
        offset = 1 if down else -1
        self.index = (self.index + offset) % max
        self._cursorline()
        logger.info("cursor pos after move: {}".format(self.index))
        return self.curpath()

    def _len(self):
        return len(self.text)

    def jump(self, top=True):
        if not self.empty():
            self.index = 0 if top else self._len() - 1
            self._cursorline()
            logger.info("cursor pos after jump: {}".format(self.index))
        else:
            logger.warning("ignore empty directory {}".format(self.cwd))

    def scroll(self, down=True):
        if not self.empty():
            sign = 1 if down else -1
            self.index += sign * self.scroll_line
            self._correct_index()
            self._cursorline()
            logger.info("cursor pos after scroll: {}".format(self.index))
        else:
            logger.warning("ignore empty directory {}".format(self.cwd))

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self.refresh()

    def touch(self, name: str):
        file = self.cwd / name
        logger.info("touch file {}".format(file))
        file.touch()
        self.refresh()


class FilePanel(Panel):
    def __init__(self, path):
        self.lfopt = Option()
        self.path = path.resolve(True)
        self._create()
        self._linenr()
        self._set_option()

    def _create(self):
        opt = self.lfopt.popup("right")
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

    def set_exist(self):
        self.buf_exist = True

    def _set_option(self):
        winid = self.winid
        if self.lfopt.file_numbered:
            setlocal(winid, "number")
        if self.path.stat().st_size < self.lfopt.max_file_size:
            winexec(self.winid, "filetype detect")
        self.bufnr = vimeval("winbufnr({})".format(self.winid))
        self._set_wincolor()

    def close(self):
        vimcmd("call popup_close({})".format(self.winid))
        if not self.buf_exist:
            vimcmd("bwipeout {}".format(self.bufnr))


class BaseShowPanel(Panel):
    def __init__(self, name, has_prop=True):
        super().__init__(name, has_prop)

    def _settext(self, text):
        vimcmd("call popup_settext({}, {})".format(self.winid, vimstr(text)))

    def clear(self):
        self._settext([])


class InfoPanel(BaseShowPanel):
    def __init__(self, manager):
        super().__init__("info")
        self.manager = manager

    def _set_panel(self):
        path = self.manager._curpath()
        self.path = '' if path is None else path.resolve(True)
        self.text_list = self.manager.middle_panel.text
        self.total = len(self.text_list)

    def _empty(self):
        return self.manager.empty()

    def _index(self):
        return self.manager.middle_panel.index

    def _mode(self):
        return self.manager.middle_panel.mode

    def _escape_path(self, path):
        return str(path).replace("\\\\", "\\")

    def info_path(self):
        self._set_panel()
        self._set_mode()
        self._set_sz()
        self._set_nr()
        self._set_path()
        self.info = self.keep + self.mode + self.path_str_fill + self.sz + self.nr
        self._settext_path()

    def _settext_path(self):
        opt = {"text": self.info}
        left_str = ''
        prop_keep = {
                "col": 1,
                "length": bytelen(self.keep),
                "type": "mode_keep_open",
                }
        if self.is_keep:
            left_str += self.keep
        prop_mode = {
                "col": bytelen(left_str) + 1,
                "length": bytelen(self.mode),
                }
        prop_mode["type"] = "mode_" + self._mode()
        left_str += self.mode
        prop_path = {
                "col": bytelen(left_str) + 1,
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
        opt["props"] = [prop_mode, prop_path, prop_size, prop_nr]
        if self.is_keep:
            opt["props"].append(prop_keep)
        self._settext([opt])

    def _set_mode(self):
        self.is_keep = self.manager.is_keep_open
        if self.is_keep:
            self.keep = " {} ".format(self.lfopt.mode_keep_open)
        else:
            self.keep = ''
        self.mode = " {} ".format(getattr(self.lfopt, "mode_{}".format(self._mode())))

    def _set_sz(self):
        self.sz = ''
        if self._empty():
            return
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
        if self._empty():
            self.nr = ' 0/0 '
            return
        lines = 0
        right = self.manager.right_panel
        if isinstance(right, DirPanel):
            lines = len(right.text)
        elif isinstance(right, FilePanel):
            lines = right.lines
        self.nr = " {}/{}:{} ".format(self._index() + 1, self.total, lines)

    def _set_path(self):
        valid_len = self.winwidth - len(self.nr) - len(self.sz) - len(self.keep) - len(self.mode)
        path_str = '' if self._empty() else " {} ".format(self._escape_path(self.path))
        if dplen(path_str) > valid_len:
            path_str = path_str[:valid_len - 4] + '... '
        blank = valid_len - dplen(path_str)
        self.path_str = path_str
        self.path_str_fill = path_str + blank * ' '


def update_cursor(fun):
    def wrapper(*args, **kwargs):
        fun(*args, **kwargs)
        self = args[0]
        self._settext_input()
    return wrapper


class CliPanel(BaseShowPanel):
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
        logger.info('cmd is "{}"'.format(self.cmd))
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

    @update_cursor
    def clear(self):
        self.cmd = ''
        self.pos = 0

    @update_cursor
    def add(self):
        char = vimeval("ch")
        self.cmd = self._head() + char + self._tail()
        self.pos += 1

    @update_cursor
    def delete(self):
        if self._empty():
            return
        self.cmd = self.cmd[:self.pos - 1] + self._tail()
        self.pos -= 1

    @update_cursor
    def left(self):
        if self._empty():
            return
        self.pos -= 1

    @update_cursor
    def right(self):
        if self._at_end():
            return
        self.pos += 1

    @update_cursor
    def go_start(self):
        self.pos = 0

    @update_cursor
    def go_end(self):
        self.pos = len(self.cmd)

    def done(self):
        self.close()
        self.do = True

    def quit(self):
        self.close()
        self.do = False


class RegexSearchPanel(CliPanel):
    def __init__(self, manager):
        super().__init__('/')
        self.manager = manager
        self.middle = manager.middle_panel
        self.save_index = self.middle.index
        self.regex_search = RegexSearch(self.middle.text, self)

    def _refresh(self):
        T, pos_list = self.regex_search.filter()
        self.middle.search_refresh(T)

    def restore(self):
        self.middle.refresh(index=self.save_index)

    def input(self):
        while 1:
            action = vimeval("lf#search()")
            if action in ['done', 'quit']:
                break

    def quit(self):
        super().quit()
        self.restore()

    def done(self):
        super().done()

    def add(self):
        super().add()
        self._refresh()


class MsgRemovePanel(BaseShowPanel):
    def __init__(self, path_list):
        super().__init__("msg")
        self.do = False
        self._set_textprop("path")
        self.path_list = path_list
        self._settext_firstline()
        self._settext_file()
        self._settext(self.dic_list)

    def action(self):
        while 1:
            action = vimeval("lf#msg()")
            if action in ["cancel", "agree"]:
                break

    def _settext_firstline(self):
        firstline = "Are you sure to delete following files?"
        warning_len = bytelen(firstline)
        firstline += " (y"
        default_opt_pos = bytelen(firstline)
        firstline += "/n)"
        self.dic_list = [{"text": firstline,
            "props": [
                {"col": 1, "length": warning_len, "type": "warning"},
                {"col": default_opt_pos ,
                    "length": 1,
                    "type": "default"}]
            }]

    def _settext_file(self):
        lines = sorted([SimpleLine(p) for p in self.path_list], key=attrgetter("sort_dir_first", "lower_text"))
        self.dic_list.extend([line.opt for line in lines])

    def agree(self):
        self.do = True
        self.close()

    def cancel(self):
        self.close()

    def skip(self):
        pass


class BorderPanel(Panel):
    def __init__(self):
        self.lfopt = Option()
        self.winid = vimeval("popup_create([], {})".format(self.lfopt.popup("border")))
        self._set_wincolor()
